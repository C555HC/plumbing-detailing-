#!/usr/bin/env python3
"""File-backed helpers for a Codex-driven cutaway skill; no model/API calls."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from decimal import Decimal, InvalidOperation
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from uuid import uuid4

WEIGHTS = {"construction": 45, "topology": 25, "completeness": 15,
           "appearance": 10, "clarity": 5}
BLOCK_NAMES = {"construction": "Конструкция", "topology": "Расположение и связи",
               "completeness": "Функциональная полнота", "appearance": "Внешнее сходство",
               "clarity": "Ясность и выноски"}
FACTORS = {"pass": Decimal(1), "partial": Decimal("0.5"),
           "fail": Decimal(0), "unknown": Decimal(0)}
SOURCE_KINDS = {"manufacturer_model", "manufacturer_series", "analog", "product_photo", "style_reference"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load(path):
    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream)


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def digest(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def text_value(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: expected nonempty text")
    return value


def points(value):
    if isinstance(value, bool):
        raise ValueError("Boolean points are invalid")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("Invalid points") from exc
    if not result.is_finite() or result <= 0:
        raise ValueError("Points must be finite and positive")
    return result


def validate_inputs(spec, checklist, sources):
    text_value(checklist.get("version"), "checklist.version")
    text_value(spec.get("model"), "spec.model")
    source_map = {}
    for source in sources.get("sources", []):
        sid = text_value(source.get("id"), "source.id")
        if sid in source_map or source.get("kind") not in SOURCE_KINDS:
            raise ValueError("Duplicate source ID or unsupported source kind")
        text_value(source.get("url"), "source.url")
        text_value(source.get("applicability"), "source.applicability")
        if source.get("verified") is not True:
            raise ValueError("Sources must be inspected and verified by the agent")
        source_map[sid] = source
    if not source_map:
        raise ValueError("No verified sources")
    nodes = spec.get("nodes", [])
    if not nodes:
        raise ValueError("No functional nodes")
    node_ids = set()
    for node in nodes:
        nid = text_value(node.get("id"), "node.id")
        text_value(node.get("name"), "node.name")
        if nid in node_ids:
            raise ValueError("Duplicate functional node")
        node_ids.add(nid)
        if node.get("evidence") not in {"model", "series", "analog", "unknown"}:
            raise ValueError("Invalid node evidence status")
        refs = node.get("source_ids", [])
        if any(sid not in source_map for sid in refs):
            raise ValueError("Unknown node source")
        required = {"model": "manufacturer_model", "series": "manufacturer_series", "analog": "analog"}
        if node["evidence"] in required and not any(
                source_map[sid]["kind"] == required[node["evidence"]] for sid in refs):
            raise ValueError("Node evidence does not agree with source provenance")
    checks = checklist.get("checks", [])
    if not checks:
        raise ValueError("Empty checklist")
    ids, totals = set(), {key: Decimal(0) for key in WEIGHTS}
    for check in checks:
        cid = text_value(check.get("id"), "check.id")
        text_value(check.get("requirement"), "check.requirement")
        text_value(check.get("locator"), "check.locator")
        block = check.get("block")
        if cid in ids or block not in WEIGHTS:
            raise ValueError("Duplicate check ID or invalid block")
        ids.add(cid)
        totals[block] += points(check.get("points"))
        refs = check.get("source_ids", [])
        if not refs or any(sid not in source_map for sid in refs):
            raise ValueError("Checks require existing sources")
        if block == "construction" and any(source_map[sid]["kind"] not in {
                "manufacturer_model", "manufacturer_series"} for sid in refs):
            raise ValueError("Analog/photo cannot prove construction of the target model")
        if not isinstance(check.get("critical", False), bool):
            raise ValueError("critical must be a boolean")
        if check.get("critical") and check.get("partial_rule"):
            raise ValueError("Critical checks must be binary")
    for block, total in totals.items():
        if total not in (Decimal(0), Decimal(WEIGHTS[block])):
            raise ValueError(f"{block}: allocated {total}, expected {WEIGHTS[block]} or empty")
    return source_map


def evaluate(checklist, review):
    if review.get("checklist_version") != checklist["version"]:
        raise ValueError("Review checklist version mismatch")
    answers = review.get("checks", [])
    if not isinstance(answers, list):
        raise ValueError("Review checks must be a list")
    by_id = {}
    for answer in answers:
        cid = answer.get("id")
        if cid in by_id:
            raise ValueError("Duplicate review check")
        text_value(answer.get("observation"), "observation")
        text_value(answer.get("region"), "region")
        if answer.get("status") not in FACTORS:
            raise ValueError("Invalid review status")
        by_id[cid] = answer
    if set(by_id) != {item["id"] for item in checklist["checks"]}:
        raise ValueError("Review must cover every check exactly once")
    totals = {block: Decimal(0) for block in WEIGHTS}
    critical_errors, critical_unknown, issues = [], [], []
    breakdown = []
    for check in checklist["checks"]:
        answer = by_id[check["id"]]
        status = answer["status"]
        if status == "partial" and (not check.get("partial_rule") or check.get("critical")):
            raise ValueError("Partial score requires an explicit noncritical partial_rule")
        earned = points(check["points"]) * FACTORS[status]
        totals[check["block"]] += earned
        item = {**answer, "points": float(earned), "max_points": float(points(check["points"])),
                "requirement": check["requirement"], "critical": check.get("critical", False)}
        breakdown.append(item)
        if status != "pass":
            issues.append(check["id"])
        if check.get("critical") and status == "fail":
            critical_errors.append(check["id"])
        if check.get("critical") and status == "unknown":
            critical_unknown.append(check["id"])
    return {"checklist_version": checklist["version"],
            "total": float(sum(totals.values())), "blocks": {k: float(v) for k, v in totals.items()},
            "critical_errors": critical_errors, "critical_unknown": critical_unknown,
            "issues": issues, "checks": breakdown,
            "unrated_blocks": [block for block in WEIGHTS if not any(
                check["block"] == block for check in checklist["checks"])]}


@contextmanager
def transaction(run):
    run = Path(run)
    if not (run / "state.json").is_file():
        raise ValueError("Run does not exist")
    with (run / ".lock").open("a") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            state = load(run / "state.json")
            yield state
            state["updated_at"] = now()
            atomic_json(run / "state.json", state)
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def event(state, action, **details):
    state["events"].append({"at": now(), "action": action, **details})


def image_details(path, allowed_formats=("PNG",)):
    from PIL import Image
    with Image.open(path) as img:
        img.verify()
    with Image.open(path) as img:
        if img.format not in allowed_formats:
            raise ValueError("Unsupported image format; expected " + ", ".join(allowed_formats))
        return list(img.size), img.format


def image_size(path):
    return image_details(path)[0]


def initialize(root, product_id, model, url, image, limit=10):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", product_id):
        raise ValueError("product_id must be a short lowercase identifier")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 10:
        raise ValueError("Initial run limit must be 1..10")
    image_size(image)
    run = Path(root).resolve() / product_id / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
    (run / "input").mkdir(parents=True)
    shutil.copy2(image, run / "input/reference.png")
    atomic_json(run / "state.json", {"schema_version": 1, "run_id": run.name,
        "product_id": product_id, "model": model, "url": url, "limit": limit,
        "created_at": now(), "updated_at": now(), "stage": "needs_inputs",
        "attempts": [], "events": [], "inputs_version": 0, "best": None})
    return run


def prepare(run, spec_path, checklist_path, sources_path, update=False):
    run = Path(run)
    spec, checklist, sources = map(load, (spec_path, checklist_path, sources_path))
    validate_inputs(spec, checklist, sources)
    with transaction(run) as state:
        if spec["model"] != state["model"]:
            raise ValueError("Spec model differs from run model")
        if any(a["status"] == "reserved" for a in state["attempts"]):
            raise ValueError("Cannot change inputs during an unfinished attempt")
        if state["inputs_version"] and not update:
            raise ValueError("Inputs already frozen; use prepare --update explicitly")
        version = state["inputs_version"] + 1
        folder = run / "inputs" / f"v{version}"
        if folder.exists():
            raise ValueError("Orphaned input version exists; inspect it before continuing")
        folder.mkdir(parents=True)
        for name, value in [("spec.json", spec), ("checklist.json", checklist), ("sources.json", sources)]:
            atomic_json(folder / name, value)
        state["inputs_version"] = version
        state["inputs_dir"] = str(folder.relative_to(run))
        state["checklist_sha256"] = digest(folder / "checklist.json")
        state["input_hashes"] = {name: digest(folder / name) for name in ("spec.json", "checklist.json", "sources.json")}
        for attempt in state["attempts"]:
            if "score" in attempt:
                attempt.setdefault("score_history", []).append(attempt.pop("score"))
        state["best"] = None
        state["stage"] = "ready"
        event(state, "prepare", version=version, checklist=checklist["version"])
    return {"inputs_version": version, "checklist_sha256": digest(folder / "checklist.json")}


def reserve(run, prompt_file, refs, parent=None, kind="generate"):
    run = Path(run)
    prompt = Path(prompt_file).read_text(encoding="utf-8")
    text_value(prompt, "prompt")
    if kind not in {"generate", "edit"}:
        raise ValueError("Invalid attempt kind")
    ref_paths = [Path(p).resolve() for p in refs]
    ref_formats = [image_details(ref, ("PNG", "JPEG", "WEBP"))[1] for ref in ref_paths]
    if not ref_paths:
        raise ValueError("At least one inspected image reference is required")
    with transaction(run) as state:
        if not state["inputs_version"]:
            raise ValueError("Prepare technical inputs first")
        verify_inputs(run, state)
        if len(state["attempts"]) >= state["limit"]:
            raise ValueError("Generation limit exhausted")
        if any(a["status"] == "reserved" for a in state["attempts"]):
            raise ValueError("An unfinished attempt exists; record or fail it first")
        if parent is not None:
            previous = get_attempt(state, parent)
            if previous.get("image") is None:
                raise ValueError("Parent has no image")
        if kind == "edit" and parent is None:
            raise ValueError("Edit requires a parent attempt")
        number = len(state["attempts"]) + 1
        folder = run / "attempts" / f"{number:03d}"
        if folder.exists():
            raise ValueError("Orphaned attempt directory exists; inspect it before retrying")
        folder.mkdir(parents=True)
        (folder / "prompt.md").write_text(prompt, encoding="utf-8")
        saved_refs = []
        for path, image_format in zip(ref_paths, ref_formats):
            checksum = digest(path)
            suffix = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}[image_format]
            target = run / "references" / f"{checksum}{suffix}"
            target.parent.mkdir(exist_ok=True)
            if not target.exists():
                shutil.copy2(path, target)
            saved_refs.append({"path": str(target.relative_to(run)), "sha256": checksum})
        attempt = {"id": number, "kind": kind, "parent": parent, "status": "reserved",
                   "reserved_at": now(), "refs": saved_refs,
                   "prompt": str((folder / "prompt.md").relative_to(run)),
                   "checklist_sha256": state["checklist_sha256"]}
        state["attempts"].append(attempt)
        state["stage"] = "generating"
        event(state, "reserve", attempt=number)
    return {"attempt": number, "remaining": state["limit"] - number}


def get_attempt(state, number):
    for attempt in state["attempts"]:
        if attempt["id"] == number:
            return attempt
    raise ValueError("Unknown attempt")


def verify_inputs(run, state):
    folder = Path(run) / state["inputs_dir"]
    for name, expected in state["input_hashes"].items():
        if digest(folder / name) != expected:
            raise ValueError("Frozen inputs changed; use prepare --update and re-review")


def record(run, number, image, metadata=None):
    run = Path(run)
    size = image_size(image)
    with transaction(run) as state:
        attempt = get_attempt(state, number)
        if attempt["status"] not in {"reserved", "unknown"}:
            raise ValueError("Attempt already resolved")
        target = run / "attempts" / f"{number:03d}" / "image.png"
        if target.exists() and digest(target) != digest(image):
            raise ValueError("Different existing image; refusing overwrite")
        if Path(image).resolve() != target.resolve():
            shutil.copy2(image, target)
        attempt.update(status="recorded", image=str(target.relative_to(run)),
                       image_sha256=digest(target), image_size=size, recorded_at=now())
        if metadata is not None:
            atomic_json(target.parent / "tool-result.json", metadata)
        state["stage"] = "reviewing"
        event(state, "record", attempt=number)
    return {"attempt": number, "image": str(target)}


def fail(run, number, reason, unknown=False):
    text_value(reason, "failure reason")
    with transaction(run) as state:
        attempt = get_attempt(state, number)
        if attempt["status"] != "reserved":
            raise ValueError("Only reserved attempts can fail")
        attempt.update(status="unknown" if unknown else "failed", error=reason)
        state["stage"] = "ready"
        event(state, "generation_error", attempt=number, reason=reason, uncertain=unknown)
    return {"attempt": number, "status": attempt["status"]}


def scored_candidates(state):
    candidates = [a for a in state["attempts"] if a.get("score", {}).get("checklist_sha256") == state["checklist_sha256"]]
    return sorted(candidates, key=lambda a: (bool(a["score"]["critical_errors"]),
                                             -a["score"]["total"], a["id"]))


def review_attempt(run, number, review_path, preview=None):
    run = Path(run)
    review = load(review_path)
    with transaction(run) as state:
        attempt = get_attempt(state, number)
        if attempt.get("image") is None:
            raise ValueError("Attempt has no image to inspect")
        if digest(run / attempt["image"]) != attempt["image_sha256"]:
            raise ValueError("Candidate image changed after recording")
        checklist = load(run / state["inputs_dir"] / "checklist.json")
        verify_inputs(run, state)
        score = evaluate(checklist, review)
        ordinal = len(attempt.get("reviews", [])) + 1
        folder = run / "attempts" / f"{number:03d}"
        if preview:
            image_size(preview)
            destination = folder / f"preview-{ordinal:02d}.png"
            if Path(preview).resolve() != destination.resolve():
                shutil.copy2(preview, destination)
            attempt["preview"] = str(destination.relative_to(run))
            attempt["preview_sha256"] = digest(destination)
        review_file = folder / f"review-{ordinal:02d}.json"
        atomic_json(review_file, review)
        attempt.setdefault("reviews", []).append(str(review_file.relative_to(run)))
        score.update(checklist_sha256=state["checklist_sha256"], evaluated_at=now())
        if "score" in attempt:
            attempt.setdefault("score_history", []).append(attempt["score"])
        attempt["score"] = score
        attempt["status"] = "reviewed"
        state["best"] = scored_candidates(state)[0]["id"]
        state["stage"] = "ready"
        event(state, "review", attempt=number, total=score["total"])
    return {"attempt": number, "rating": score["total"], "best": state["best"],
            "critical_errors": score["critical_errors"], "issues": score["issues"]}


def coverage(spec):
    result = {kind: [] for kind in ("model", "series", "analog", "unknown")}
    for node in spec["nodes"]:
        result[node["evidence"]].append(node["name"])
    return result


def report_text(run, state, candidates, reason):
    run = Path(run)
    best = candidates[0]
    score = best["score"]
    spec = load(run / state["inputs_dir"] / "spec.json")
    sources = load(run / state["inputs_dir"] / "sources.json")["sources"]
    lines = [f"# {state['model']}: итог пилота", "", f"Лучший вариант: **{best['id']}**, рейтинг **{score['total']:g}/100**.",
        "Рейтинг сравнивает варианты, а не измеряет вероятность технической правильности.",
        f"Попытки: {len(state['attempts'])}/{state['limit']}. Причина остановки: {reason}.",
        "Технический специалист ещё не подтвердил результат.", "", "![Лучший вариант](best.png)", "", "## Проверка выбранного варианта", ""]
    for block in WEIGHTS:
        lines.append(f"- {BLOCK_NAMES[block]}: {score['blocks'][block]:g}/{WEIGHTS[block]}.")
    lines += ["", f"Критические противоречия: {', '.join(score['critical_errors']) or 'не обнаружены в проведённой проверке'}.",
              f"Непроверенные критические пункты: {', '.join(score['critical_unknown']) or 'нет'}."]
    for item in score["checks"]:
        if item["status"] != "pass":
            lines.append(f"- {item['id']} ({item['status']}): {item['observation']}")
    lines += ["", "## Основания и реконструкция", ""]
    for kind, names in coverage(spec).items():
        lines.append(f"- {kind}: {', '.join(names) or 'нет'}.")
    for gap in spec.get("gaps", []):
        lines.append(f"- Ограничение: {gap}")
    for assumption in spec.get("analog_assertions", []):
        lines.append(f"- Реконструкция по аналогам: {assumption}")
    lines += ["", "## История вариантов", "", "| Версия | Рейтинг | Критические ошибки | Замечания и исправления |", "|---|---:|---|---|"]
    for a in state["attempts"]:
        s = a.get("score")
        if s:
            review = load(run / a["reviews"][-1])
            notes = review.get("summary", "")
            changes = review.get("resolved_changes", [])
            if changes:
                notes += " Исправлено: " + "; ".join(changes)
            lines.append(f"| {a['id']} | {s['total']:g} | {', '.join(s['critical_errors']) or '—'} | {notes.replace('|', '/').replace(chr(10), ' ')} |")
        else:
            lines.append(f"| {a['id']} | — | — | {a['status']}: {a.get('error', 'не оценено')} |")
    lines += ["", "## Источники", ""]
    for source in sources:
        lines.append(f"- [{source.get('title', source['id'])}]({source['url']}): {source['kind']}; {source['applicability']}")
    return "\n".join(lines) + "\n"


def error_report_text(run, state):
    lines = ["# Ошибки и ограничения запуска", "",
             "Сохранены наблюдения по каждой версии. unknown означает непроверенность, а не доказанную техническую ошибку.", ""]
    for attempt in state["attempts"]:
        lines += [f"## Попытка {attempt['id']}", ""]
        if attempt.get("error"):
            lines.append(f"- Ошибка вызова: {attempt['error']} ({attempt['status']}).")
        for i, path in enumerate(attempt.get("reviews", []), 1):
            review = load(Path(run) / path)
            lines.append(f"Проверка {i}:")
            issues = [item for item in review["checks"] if item["status"] != "pass"]
            for item in issues:
                lines.append(f"- {item['id']} / {item['status']}: {item['observation']}")
            if not issues:
                lines.append("- В данном проходе замечаний не записано.")
            for change in review.get("resolved_changes", []):
                lines.append(f"- Исправлено/изменено: {change}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def finalize(run, reason):
    run = Path(run)
    text_value(reason, "stop reason")
    with transaction(run) as state:
        verify_inputs(run, state)
        if any(a["status"] == "reserved" for a in state["attempts"]):
            raise ValueError("An unfinished generation remains")
        unreviewed = [a["id"] for a in state["attempts"] if a.get("image") and not a.get("score")]
        if unreviewed:
            raise ValueError(f"Review every available candidate before finalizing: {unreviewed}")
        candidates = scored_candidates(state)
        if not candidates:
            raise ValueError("No scored candidates")
        for candidate in candidates:
            if digest(run / candidate["image"]) != candidate["image_sha256"]:
                raise ValueError("Candidate changed after evaluation")
            if candidate.get("preview") and digest(run / candidate["preview"]) != candidate["preview_sha256"]:
                raise ValueError("Candidate preview changed after evaluation")
        best = candidates[0]
        selected = run / best.get("preview", best["image"])
        expected = best.get("preview_sha256", best["image_sha256"])
        if digest(selected) != expected:
            raise ValueError("Selected PNG changed after evaluation; re-review it")
        final = run / "final"
        final.mkdir(exist_ok=True)
        shutil.copy2(selected, final / "best.png")
        atomic_json(final / "ranking.json", [{"attempt": a["id"], "rating": a["score"]["total"],
                    "critical_errors": a["score"]["critical_errors"]} for a in candidates])
        (final / "report.md").write_text(report_text(run, state, candidates, reason), encoding="utf-8")
        (final / "errors.md").write_text(error_report_text(run, state), encoding="utf-8")
        contact_sheet(run, candidates, final / "contact-sheet.jpg")
        state.update(best=best["id"], stage="complete", stop_reason=reason)
        event(state, "finalize", best=best["id"], reason=reason)
    return {"best": best["id"], "rating": best["score"]["total"], "image": str(final / "best.png"),
            "report": str(final / "report.md"), "errors": str(final / "errors.md")}


def contact_sheet(run, candidates, target):
    from PIL import Image, ImageDraw, ImageOps
    cols, width, height = 2, 540, 450
    canvas = Image.new("RGB", (cols * width, math.ceil(len(candidates) / cols) * height), "white")
    draw = ImageDraw.Draw(canvas)
    for i, a in enumerate(candidates):
        x, y = (i % cols) * width, (i // cols) * height
        with Image.open(Path(run) / a.get("preview", a["image"])) as img:
            thumb = ImageOps.contain(img.convert("RGB"), (width - 20, height - 45))
            canvas.paste(thumb, (x + (width - thumb.width)//2, y + 30))
        draw.text((x + 12, y + 8), f"#{a['id']}  {a['score']['total']:g}/100", fill="#073363")
    canvas.save(target, quality=90)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("init")
    for name in ("root", "product-id", "model", "url", "image"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--limit", type=int, default=10)
    p = sub.add_parser("prepare")
    for name in ("run", "spec", "checklist", "sources"):
        p.add_argument("--" + name, required=True)
    p.add_argument("--update", action="store_true")
    p = sub.add_parser("reserve")
    p.add_argument("--run", required=True); p.add_argument("--prompt-file", required=True)
    p.add_argument("--ref", action="append", required=True)
    p.add_argument("--parent", type=int); p.add_argument("--kind", choices=("generate", "edit"), default="generate")
    p = sub.add_parser("record")
    p.add_argument("--run", required=True); p.add_argument("--attempt", type=int, required=True)
    p.add_argument("--image", required=True); p.add_argument("--metadata")
    p = sub.add_parser("fail")
    p.add_argument("--run", required=True); p.add_argument("--attempt", type=int, required=True)
    p.add_argument("--reason", required=True); p.add_argument("--unknown", action="store_true")
    p = sub.add_parser("review")
    p.add_argument("--run", required=True); p.add_argument("--attempt", type=int, required=True)
    p.add_argument("--review-file", required=True); p.add_argument("--preview")
    p = sub.add_parser("finalize")
    p.add_argument("--run", required=True); p.add_argument("--reason", required=True)
    p = sub.add_parser("status"); p.add_argument("--run", required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            result = {"run": str(initialize(args.root, args.product_id, args.model, args.url, args.image, args.limit))}
        elif args.command == "prepare":
            result = prepare(args.run, args.spec, args.checklist, args.sources, args.update)
        elif args.command == "reserve":
            result = reserve(args.run, args.prompt_file, args.ref, args.parent, args.kind)
        elif args.command == "record":
            result = record(args.run, args.attempt, args.image, load(args.metadata) if args.metadata else None)
        elif args.command == "fail":
            result = fail(args.run, args.attempt, args.reason, args.unknown)
        elif args.command == "review":
            result = review_attempt(args.run, args.attempt, args.review_file, args.preview)
        elif args.command == "finalize":
            result = finalize(args.run, args.reason)
        else:
            result = load(Path(args.run) / "state.json")
        print(json.dumps(result, ensure_ascii=False, allow_nan=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
