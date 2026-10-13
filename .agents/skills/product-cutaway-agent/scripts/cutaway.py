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
DEFAULT_LIMIT = 5
NODE_ASPECTS = {"type_count", "shape", "attachment", "placement_connections", "material"}
READINESS_LABELS = {
    "best_available": "Лучший доступный: есть критические ошибки",
    "needs_technical_review": "Нужна техническая проверка: существенные признаки не подтверждены",
    "ready_for_technical_review": "Подготовлен к технической приёмке",
}


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
    protocol = checklist.get("protocol_version", 1)
    if type(protocol) is not int or protocol not in (1, 2):
        raise ValueError("Unsupported scoring protocol version")
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
    if protocol == 2:
        covered = {nid: set() for nid in node_ids}
        essential_nodes = set()
        for node in nodes:
            if type(node.get("essential", True)) is not bool:
                raise ValueError("node.essential must be a boolean")
            if node.get("essential", True):
                essential_nodes.add(node["id"])
        for check in checks:
            aspect = check.get("aspect")
            nid = check.get("node_id")
            if aspect not in NODE_ASPECTS | {"delivery"}:
                raise ValueError("Checks need an atomic node aspect or delivery aspect")
            if aspect != "delivery" and nid not in node_ids:
                raise ValueError("Technical checks require a functional node_id")
            if type(check.get("essential")) is not bool or type(check.get("evidence_supported")) is not bool:
                raise ValueError("essential and evidence_supported must be explicit booleans")
            if aspect != "delivery" and nid in essential_nodes and not check["essential"]:
                raise ValueError("Essential node aspects cannot be optional")
            text_value(check.get("source_fact"), "check.source_fact")
            level = check.get("evidence_level")
            if level not in {"model", "series", "analog", "photo", "style", "unknown"}:
                raise ValueError("Invalid check evidence level")
            if aspect != "delivery" and level in {"photo", "style"}:
                raise ValueError("Exterior/style references cannot prove an internal node aspect")
            required = {"model": "manufacturer_model", "series": "manufacturer_series",
                        "analog": "analog", "photo": "product_photo", "style": "style_reference"}
            if level in required and not any(source_map[sid]["kind"] == required[level] for sid in check["source_ids"]):
                raise ValueError("Check evidence level disagrees with source provenance")
            if level == "unknown" and check["evidence_supported"]:
                raise ValueError("Unknown evidence cannot be supported")
            if aspect != "delivery":
                covered[nid].add(aspect)
        for node in nodes:
            exclusions = node.get("excluded_aspects", {})
            if not isinstance(exclusions, dict) or set(exclusions) - NODE_ASPECTS:
                raise ValueError("Invalid node aspect exclusions")
            for reason in exclusions.values():
                text_value(reason, "excluded aspect reason")
            if covered[node["id"]] & set(exclusions):
                raise ValueError("A node aspect cannot be checked and excluded")
            if node["id"] in essential_nodes and covered[node["id"]] | set(exclusions) != NODE_ASPECTS:
                raise ValueError("Cover each node aspect or explain why it is inapplicable; missing sources are not an exclusion")
    return source_map


def evaluate(checklist, review):
    protocol = checklist.get("protocol_version", 1)
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
        if protocol == 2:
            text_value(answer.get("source_observation"), "review.source_observation")
            if not check["evidence_supported"] and status != "unknown":
                raise ValueError("Unsupported source facts must be reviewed as unknown")
        if status == "partial" and (not check.get("partial_rule") or check.get("critical")):
            raise ValueError("Partial score requires an explicit noncritical partial_rule")
        earned = points(check["points"]) * FACTORS[status]
        totals[check["block"]] += earned
        item = {**answer, "points": float(earned), "max_points": float(points(check["points"])),
                "requirement": check["requirement"], "critical": check.get("critical", False)}
        if protocol == 2:
            item.update({key: check.get(key) for key in ("node_id", "aspect", "essential", "evidence_level",
                        "evidence_supported", "source_fact", "source_ids", "locator")})
        breakdown.append(item)
        if status != "pass":
            issues.append(check["id"])
        if check.get("critical") and status == "fail":
            critical_errors.append(check["id"])
        if check.get("critical") and status == "unknown":
            critical_unknown.append(check["id"])
    score = {"checklist_version": checklist["version"], "protocol_version": protocol,
            "total": float(sum(totals.values())), "blocks": {k: float(v) for k, v in totals.items()},
            "critical_errors": critical_errors, "critical_unknown": critical_unknown,
            "issues": issues, "checks": breakdown,
            "unrated_blocks": [block for block in WEIGHTS if not any(
                check["block"] == block for check in checklist["checks"])]}
    if protocol == 2:
        technical = [item for item in breakdown if item["aspect"] != "delivery" and (item["essential"] or item["critical"])]
        evidence = {level: [] for level in ("model", "series", "analog", "unknown")}
        confirmed = {level: [] for level in ("model", "series", "analog")}
        for item in technical:
            level = item["evidence_level"] if item["evidence_supported"] else "unknown"
            evidence[level].append(item["id"])
            if item["status"] == "pass" and level in confirmed:
                confirmed[level].append(item["id"])
        unavailable = [item for item in checklist["checks"] if not item["evidence_supported"]]
        score["evidence_summary"] = {"scope": "essential_internal_facts", "source_basis": evidence, "confirmed_facts": confirmed,
            "unverified": [item["id"] for item in technical if item["status"] == "unknown"],
            "contradicted": [item["id"] for item in technical if item["status"] == "fail"],
            "partial": [item["id"] for item in technical if item["status"] == "partial"],
            "unavailable_checks": [item["id"] for item in unavailable],
            "unavailable_points": float(sum(points(item["points"]) for item in unavailable)),
            "source_supported_ceiling": float(sum(points(check["points"]) for check in checklist["checks"] if check["evidence_supported"]))}
    score["readiness"] = readiness(score)
    return score


def readiness(score):
    if score["critical_errors"]:
        status, reasons = "best_available", score["critical_errors"]
    elif score.get("protocol_version", 1) != 2:
        status, reasons = "needs_technical_review", ["legacy_unstructured_checks"]
    else:
        reasons = [item["id"] for item in score["checks"] if (item["essential"] or item["critical"]) and
                   (item["status"] != "pass" or not item["evidence_supported"] or
                    (item["aspect"] != "delivery" and item["evidence_level"] not in {"model", "series"}))]
        reasons += ["unrated_block:" + block for block in score["unrated_blocks"]]
        status = "needs_technical_review" if reasons else "ready_for_technical_review"
    return {"status": status, "label": READINESS_LABELS[status], "reasons": reasons,
            "technical_approval": False}


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


def initialize(root, product_id, model, url, image, limit=DEFAULT_LIMIT):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", product_id):
        raise ValueError("product_id must be a short lowercase identifier")
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= DEFAULT_LIMIT:
        raise ValueError("New run limit must be 1..5; preserve older runs and use a linked revision to continue")
    size, image_format = image_details(image, ("PNG", "JPEG", "WEBP"))
    run = Path(root).resolve() / product_id / (datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + uuid4().hex[:8])
    (run / "input").mkdir(parents=True)
    suffix = {"PNG": ".png", "JPEG": ".jpg", "WEBP": ".webp"}[image_format]
    reference = run / "input" / ("reference" + suffix)
    shutil.copy2(image, reference)
    atomic_json(run / "state.json", {"schema_version": 1, "run_id": run.name,
        "product_id": product_id, "model": model, "url": url, "limit": limit,
        "created_at": now(), "updated_at": now(), "stage": "needs_inputs",
        "attempts": [], "events": [], "inputs_version": 0, "best": None, "scoring_protocol_version": 2,
        "input_image": {"path": str(reference.relative_to(run)), "sha256": digest(reference),
                        "format": image_format, "size": size}})
    return run


def prepare(run, spec_path, checklist_path, sources_path, update=False):
    run = Path(run)
    spec, checklist, sources = map(load, (spec_path, checklist_path, sources_path))
    validate_inputs(spec, checklist, sources)
    with transaction(run) as state:
        if checklist.get("protocol_version", 1) < state.get("scoring_protocol_version", 1):
            raise ValueError("New runs require atomic scoring protocol v2; do not downgrade a revised run")
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
        state["scoring_protocol_version"] = checklist.get("protocol_version", 1)
        state["inputs_dir"] = str(folder.relative_to(run))
        state["checklist_sha256"] = digest(folder / "checklist.json")
        state["input_hashes"] = {name: digest(folder / name) for name in ("spec.json", "checklist.json", "sources.json")}
        for attempt in state["attempts"]:
            if "score" in attempt:
                attempt.setdefault("score_history", []).append(attempt.pop("score"))
            attempt.pop("caption_audit", None)
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
        verify_evidence(run, state)
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


def archive_evidence(run, source_id, locator, observation, file=None, gap=None):
    """Archive an inspected source asset, or explicitly record why no asset exists."""
    run = Path(run)
    text_value(locator, "evidence.locator")
    text_value(observation, "evidence.observation")
    if bool(file) == bool(gap):
        raise ValueError("Supply either an evidence file or an explicit archive gap")
    if gap:
        text_value(gap, "evidence.gap")
    with transaction(run) as state:
        if not state.get("inputs_version"):
            raise ValueError("Prepare technical inputs before archiving evidence")
        verify_inputs(run, state)
        sources = load(run / state["inputs_dir"] / "sources.json")["sources"]
        source = next((s for s in sources if s["id"] == source_id), None)
        if source is None:
            raise ValueError("Unknown evidence source")
        entries = state.setdefault("evidence_archives", [])
        entry = {"id": len(entries) + 1, "source_id": source_id, "url": source["url"],
                 "kind": source["kind"], "applicability": source["applicability"],
                 "inputs_version": state["inputs_version"], "locator": locator,
                 "observation": observation, "archived_at": now()}
        if file:
            original = Path(file)
            checksum = digest(original)
            suffix = original.suffix.lower()
            if not re.fullmatch(r"\.[a-z0-9]{1,10}", suffix):
                suffix = ".bin"
            target = run / "evidence" / "files" / (checksum + suffix)
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and digest(target) != checksum:
                raise ValueError("Archived evidence changed; refusing overwrite")
            if not target.exists():
                shutil.copy2(original, target)
            entry.update(path=str(target.relative_to(run)), sha256=checksum)
        else:
            entry["gap"] = gap
        manifest = run / "evidence" / f"{entry['id']:03d}.json"
        if manifest.exists():
            raise ValueError("Orphaned evidence manifest exists; inspect before retrying")
        atomic_json(manifest, entry)
        entries.append({**entry, "manifest": str(manifest.relative_to(run)),
                        "manifest_sha256": digest(manifest)})
        event(state, "archive_evidence", source_id=source_id, archived=bool(file))
    return entry


def verify_evidence(run, state):
    for entry in state.get("evidence_archives", []):
        if digest(Path(run) / entry["manifest"]) != entry["manifest_sha256"]:
            raise ValueError("Evidence manifest changed after archiving")
        if entry.get("path") and digest(Path(run) / entry["path"]) != entry["sha256"]:
            raise ValueError("Archived evidence changed after inspection")


def validate_label_review(labels, audit, source_ids, hashes):
    if any(audit.get(key) != value for key, value in hashes.items()):
        raise ValueError("Label review hashes do not match base, labels and preview")
    if audit.get("layout_checked") is not True or audit.get("title_checked") is not True:
        raise ValueError("Inspect caption layout and title before registering the preview")
    expected = [text_value(item.get("id"), "label.id") for item in labels.get("labels", [])]
    if len(set(expected)) != len(expected):
        raise ValueError("Duplicate label ID")
    checks = audit.get("checks", [])
    actual = [item.get("id") for item in checks]
    if len(set(actual)) != len(actual) or set(actual) != set(expected):
        raise ValueError("Label review must cover every label exactly once")
    by_id = {item["id"]: item for item in checks}
    for label in labels.get("labels", []):
        check = by_id[label["id"]]
        text_value(check.get("observation"), "label observation")
        text_value(check.get("locator"), "label source locator")
        refs = check.get("source_ids", [])
        if not refs or any(sid not in source_ids for sid in refs):
            raise ValueError("Label names require applicable sources")
        if check.get("text_checked") is not True:
            raise ValueError("Label wording has not been checked")
        if ("target" in label or "target_image" in label) and check.get("target_checked") is not True:
            raise ValueError("Label endpoint has not been visually checked")


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


def review_attempt(run, number, review_path, preview=None, labels_path=None, label_review_path=None):
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
        verify_evidence(run, state)
        score = evaluate(checklist, review)
        if labels_path or label_review_path:
            if not (preview and labels_path and label_review_path):
                raise ValueError("Caption review requires preview, labels and label-review together")
            sources = load(run / state["inputs_dir"] / "sources.json")["sources"]
            source_ids = {s["id"] for s in sources if s["kind"] != "style_reference"}
            validate_label_review(load(labels_path), load(label_review_path), source_ids,
                                  {"base_sha256": attempt["image_sha256"],
                                   "labels_sha256": digest(labels_path), "preview_sha256": digest(preview)})
        ordinal = len(attempt.get("reviews", [])) + 1
        folder = run / "attempts" / f"{number:03d}"
        if preview:
            image_size(preview)
            destination = folder / f"preview-{ordinal:02d}.png"
            if Path(preview).resolve() != destination.resolve():
                shutil.copy2(preview, destination)
            attempt["preview"] = str(destination.relative_to(run))
            attempt["preview_sha256"] = digest(destination)
            # A new preview must never inherit a previous caption audit.
            attempt.pop("caption_audit", None)
            if labels_path:
                saved = {}
                for key, source in (("labels", labels_path), ("label_review", label_review_path)):
                    target = folder / f"{key}-{ordinal:02d}.json"
                    if Path(source).resolve() != target.resolve():
                        shutil.copy2(source, target)
                    saved[key] = str(target.relative_to(run))
                    saved[key + "_sha256"] = digest(target)
                attempt["caption_audit"] = saved
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
            "critical_errors": score["critical_errors"], "issues": score["issues"],
            "readiness": score["readiness"], "evidence_summary": score.get("evidence_summary")}


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
    status = score.get("readiness") or readiness(score)
    lines += ["", "## Состояние результата", "", status["label"] + ".",
              "Основания статуса: " + (", ".join(status["reasons"]) or "обязательные проверки пройдены") + ".",
              "Этот статус не означает одобрение специалистом или разрешение публикации."]
    evidence = score.get("evidence_summary")
    if evidence:
        lines += ["", "## Подтверждение отдельных признаков", "",
                  "Счётчики относятся к существенным внутренним признакам, а не к проценту достоверности всего изделия. Потолок баллов учитывает весь checklist."]
        for level, ids in evidence["source_basis"].items():
            lines.append(f"- Основание {level}: {len(ids)} ({', '.join(ids) or 'нет'}).")
        for level, ids in evidence["confirmed_facts"].items():
            lines.append(f"- Совпадение изображения с основанием {level}: {len(ids)} ({', '.join(ids) or 'нет'}).")
        for key in ("unverified", "contradicted", "partial"):
            lines.append(f"- {key}: {', '.join(evidence[key]) or 'нет'}.")
        lines += [f"Недоступные по текущим источникам баллы: {evidence['unavailable_points']:g}; пункты: {', '.join(evidence['unavailable_checks']) or 'нет'}.",
                  f"Потолок по имеющимся основаниям: {evidence['source_supported_ceiling']:g}/100. Это не обещание получить данный балл.", "",
                  "| Пункт | Узел / признак | Основание | Статус | Источник / локатор | Сопоставление |",
                  "|---|---|---|---|---|---|"]
        for item in score["checks"]:
            cells = [item["id"], f"{item.get('node_id') or 'оформление'} / {item['aspect']}",
                     item["evidence_level"] if item["evidence_supported"] else "unknown", item["status"],
                     ', '.join(item["source_ids"]) + ": " + item["locator"], item["source_observation"]]
            lines.append("| " + " | ".join(str(cell).replace('|', '/').replace(chr(10), ' ') for cell in cells) + " |")
    else:
        lines += ["", "Историческая шкала не содержит отдельной проверки всех признаков; её баллы не перенесены на протокол v2."]
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
    lines += ["", "## Архив доказательств", ""]
    archives = state.get("evidence_archives", [])
    if not archives:
        lines.append("Локальный архив источников не зарегистрирован; ссылки не заменяют сохранённые ракурсы.")
    for entry in archives:
        asset = f"[файл](../{entry['path']})" if entry.get("path") else "не сохранено: " + entry["gap"]
        lines.append(f"- {entry['source_id']}, inputs v{entry['inputs_version']}, {entry['locator']}: {entry['observation']}; {asset}.")
    current_ids = {entry["source_id"] for entry in archives if entry["inputs_version"] == state["inputs_version"]}
    missing = [source["id"] for source in sources if source["id"] not in current_ids]
    if missing:
        lines.append("Для текущих входных данных архив или причина отсутствия не зарегистрированы: " + ", ".join(missing) + ".")
    lines += ["", "## Проверка подписей", "",
              "По всем выноскам зарегистрированы проверка названия и визуальный осмотр конечных точек. Это проверка агентом, не автоматическое распознавание деталей."
              if best.get("caption_audit") else "Отдельный машинно проверяемый протокол подписей не зарегистрирован (исторический или иной режим)."]
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
        verify_evidence(run, state)
        if any(a["status"] == "reserved" for a in state["attempts"]):
            raise ValueError("An unfinished generation remains")
        unreviewed = [a["id"] for a in state["attempts"] if a.get("image") and not a.get("score")]
        if unreviewed:
            raise ValueError(f"Review every available candidate before finalizing: {unreviewed}")
        candidates = scored_candidates(state)
        if not candidates:
            raise ValueError("No scored candidates")
        for candidate in candidates:
            for key in ("labels", "label_review"):
                audit = candidate.get("caption_audit", {})
                if key in audit and digest(run / audit[key]) != audit[key + "_sha256"]:
                    raise ValueError("Caption audit changed after evaluation")
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
        for key in ("labels", "label_review"):
            audit = best.get("caption_audit", {})
            target = final / (key + ".json")
            if key in audit:
                shutil.copy2(run / audit[key], target)
            elif target.exists():
                target.unlink()
        atomic_json(final / "ranking.json", [{"attempt": a["id"], "rating": a["score"]["total"],
                    "critical_errors": a["score"]["critical_errors"],
                    "readiness": a["score"].get("readiness") or readiness(a["score"]),
                    "evidence_summary": a["score"].get("evidence_summary")} for a in candidates])
        (final / "report.md").write_text(report_text(run, state, candidates, reason), encoding="utf-8")
        (final / "errors.md").write_text(error_report_text(run, state), encoding="utf-8")
        contact_sheet(run, candidates, final / "contact-sheet.jpg")
        state.update(best=best["id"], stage="complete", stop_reason=reason)
        event(state, "finalize", best=best["id"], reason=reason)
    return {"best": best["id"], "rating": best["score"]["total"], "image": str(final / "best.png"),
            "report": str(final / "report.md"), "errors": str(final / "errors.md"),
            "readiness": best["score"].get("readiness") or readiness(best["score"]),
            "evidence_summary": best["score"].get("evidence_summary")}


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
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
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
    p.add_argument("--labels"); p.add_argument("--label-review")
    p = sub.add_parser("archive-evidence")
    for name in ("run", "source-id", "locator", "observation"):
        p.add_argument("--" + name, required=True)
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("--file"); group.add_argument("--gap")
    p = sub.add_parser("finalize")
    p.add_argument("--run", required=True); p.add_argument("--reason", required=True)
    p = sub.add_parser("status"); p.add_argument("--run", required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            run = initialize(args.root, args.product_id, args.model, args.url, args.image, args.limit)
            result = {"run": str(run), "input_image": str(run / load(run / "state.json")["input_image"]["path"])}
        elif args.command == "prepare":
            result = prepare(args.run, args.spec, args.checklist, args.sources, args.update)
        elif args.command == "reserve":
            result = reserve(args.run, args.prompt_file, args.ref, args.parent, args.kind)
        elif args.command == "record":
            result = record(args.run, args.attempt, args.image, load(args.metadata) if args.metadata else None)
        elif args.command == "fail":
            result = fail(args.run, args.attempt, args.reason, args.unknown)
        elif args.command == "review":
            result = review_attempt(args.run, args.attempt, args.review_file, args.preview, args.labels, args.label_review)
        elif args.command == "archive-evidence":
            result = archive_evidence(args.run, args.source_id, args.locator, args.observation, args.file, args.gap)
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
