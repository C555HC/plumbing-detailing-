import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import unittest
from PIL import Image

SCRIPTS = Path(__file__).resolve().parents[1] / ".agents/skills/product-cutaway-agent/scripts"


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


c = module("cutaway")
layout = module("compose_png")


class CutawayTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / "source.png"
        Image.new("RGB", (900, 600), "white").save(self.image)
        self.prompt = self.root / "prompt.md"
        self.prompt.write_text("A real test prompt", encoding="utf-8")
        self.sources = {"sources": [{"id": "manual", "kind": "manufacturer_model", "url": "https://example.org/manual",
                          "applicability": "exact model", "verified": True}]}
        self.spec = {"model": "TEST", "nodes": [{"id": "a", "name": "Part", "evidence": "model", "source_ids": ["manual"]}], "gaps": []}
        self.checklist = {"version": "v1", "checks": [
            {"id": block, "block": block, "points": maximum,
             "requirement": "Observable fact", "source_ids": ["manual"], "locator": "PDF page 1",
             "critical": block == "construction", **({"partial_rule": "Part visible, connection partly obscured"} if block == "topology" else {})}
            for block, maximum in c.WEIGHTS.items()]}
        self.run = c.initialize(self.root / "runs", "test", "TEST", "https://example.org", self.image)
        self.write_inputs()
        c.prepare(self.run, self.root / "spec.json", self.root / "checklist.json", self.root / "sources.json")

    def write_inputs(self):
        for name, value in [("spec", self.spec), ("checklist", self.checklist), ("sources", self.sources)]:
            c.atomic_json(self.root / f"{name}.json", value)

    def answer(self, statuses=None):
        statuses = statuses or {}
        return {"checklist_version": self.checklist["version"], "checks": [
            {"id": item["id"], "status": statuses.get(item["id"], "pass"),
             "observation": "Observed in actual test fixture", "region": "centre"}
            for item in self.checklist["checks"]], "summary": "Test review"}

    def candidate(self, statuses=None):
        n = c.reserve(self.run, self.prompt, [self.image])["attempt"]
        c.record(self.run, n, self.image)
        path = self.root / f"review-{n}.json"
        c.atomic_json(path, self.answer(statuses))
        c.review_attempt(self.run, n, path)
        return n

    def test_exact_fractional_score(self):
        score = c.evaluate(self.checklist, self.answer({"topology": "partial", "clarity": "unknown"}))
        self.assertEqual(score["total"], 82.5)
        self.assertEqual(score["blocks"]["topology"], 12.5)

    def test_reference_formats_preserve_bytes_and_real_suffix(self):
        for fmt, suffix in (("JPEG", ".jpg"), ("WEBP", ".webp")):
            with self.subTest(format=fmt):
                source = self.root / ("reference-" + fmt + ".wrong-extension")
                Image.new("RGB", (80, 60), "grey").save(source, format=fmt)
                before = source.read_bytes()
                n = c.reserve(self.run, self.prompt, [source])["attempt"]
                ref = c.load(self.run / "state.json")["attempts"][-1]["refs"][0]
                cached = self.run / ref["path"]
                self.assertEqual(cached.suffix, suffix)
                self.assertEqual(cached.read_bytes(), before)
                self.assertEqual(source.read_bytes(), before)
                self.assertEqual(c.digest(cached), ref["sha256"])
                c.fail(self.run, n, "Synthetic test call not dispatched")

    def test_archive_survives_original_loss_without_spending_attempts(self):
        asset = self.root / "factory.png"
        Image.new("RGB", (80, 60), "grey").save(asset)
        before = asset.read_bytes()
        entry = c.archive_evidence(self.run, "manual", "PDF page 1, figure 2",
                                   "The actual inspected fixture", file=asset)
        asset.unlink()
        self.assertEqual((self.run / entry["path"]).read_bytes(), before)
        state = c.load(self.run / "state.json")
        self.assertEqual(state["attempts"], [])
        self.assertEqual(state["evidence_archives"][0]["inputs_version"], 1)
        self.candidate()
        c.finalize(self.run, "fixture")
        self.assertIn("PDF page 1, figure 2", (self.run / "final/report.md").read_text())

    def test_archive_missing_asset_requires_explicit_gap_and_known_source(self):
        with self.assertRaises(ValueError):
            c.archive_evidence(self.run, "manual", "rear", "Inspected view")
        with self.assertRaisesRegex(ValueError, "Unknown"):
            c.archive_evidence(self.run, "absent", "rear", "Inspected view", gap="No export")
        c.archive_evidence(self.run, "manual", "rear", "Inspected view", gap="No local export available")
        self.candidate()
        c.finalize(self.run, "fixture")
        self.assertIn("No local export available", (self.run / "final/report.md").read_text())

    def test_modified_archive_blocks_generation_and_finalization(self):
        self.candidate()
        entry = c.archive_evidence(self.run, "manual", "page 1", "Inspected page", file=self.image)
        (self.run / entry["path"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "Archived evidence changed"):
            c.reserve(self.run, self.prompt, [self.image])
        with self.assertRaisesRegex(ValueError, "Archived evidence changed"):
            c.finalize(self.run, "fixture")

    def test_modified_evidence_manifest_blocks_use(self):
        c.archive_evidence(self.run, "manual", "page 1", "Inspected page", gap="Unavailable export")
        state = c.load(self.run / "state.json")
        entry = state["evidence_archives"][0]
        (self.run / entry["manifest"]).write_text("{}")
        with self.assertRaisesRegex(ValueError, "manifest changed"):
            c.reserve(self.run, self.prompt, [self.image])

    def caption_fixture(self):
        self.candidate()
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"labels": [{"id": "a", "text": "Двигатель", "position": [.05,.05],
                                          "target_image": [.5,.5], "font_size": 24}]})
        preview = self.root / "preview.png"
        layout.compose(self.image, labels, preview)
        audit = self.root / "label-review.json"
        c.atomic_json(audit, {"base_sha256": c.digest(self.image), "labels_sha256": c.digest(labels),
                             "preview_sha256": c.digest(preview), "title_checked": True, "layout_checked": True,
                             "checks": [{"id": "a", "source_ids": ["manual"], "locator": "page 1",
                                         "text_checked": True, "target_checked": True,
                                         "observation": "Endpoint inspected on fixture centre"}]})
        review = self.root / "caption-review.json"
        c.atomic_json(review, self.answer())
        return labels, preview, audit, review

    def test_caption_protocol_is_bound_to_exact_files_and_preserves_budget(self):
        labels, preview, audit, review = self.caption_fixture()
        c.review_attempt(self.run, 1, review, preview, labels, audit)
        state = c.load(self.run / "state.json")
        self.assertEqual(len(state["attempts"]), 1)
        self.assertIn("caption_audit", state["attempts"][0])
        c.finalize(self.run, "caption fixture")
        self.assertEqual(c.digest(self.run / "final/labels.json"), c.digest(labels))
        self.assertTrue((self.run / "final/label_review.json").exists())

    def test_caption_protocol_rejects_missing_unchecked_or_stale_targets(self):
        labels, preview, audit, review = self.caption_fixture()
        valid = c.load(audit)
        for modification in ("missing", "unchecked", "stale", "unknown-source"):
            with self.subTest(modification=modification):
                value = copy.deepcopy(valid)
                if modification == "missing":
                    value["checks"] = []
                elif modification == "unchecked":
                    value["checks"][0]["target_checked"] = False
                elif modification == "stale":
                    value["preview_sha256"] = "old"
                else:
                    value["checks"][0]["source_ids"] = ["absent"]
                c.atomic_json(audit, value)
                with self.assertRaises(ValueError):
                    c.review_attempt(self.run, 1, review, preview, labels, audit)
                self.assertEqual(len(c.load(self.run / "state.json")["attempts"][0]["reviews"]), 1)

    def test_modified_caption_audit_blocks_finalization(self):
        labels, preview, audit, review = self.caption_fixture()
        c.review_attempt(self.run, 1, review, preview, labels, audit)
        state = c.load(self.run / "state.json")
        saved = state["attempts"][0]["caption_audit"]
        (self.run / saved["labels"]).write_text("{}")
        with self.assertRaisesRegex(ValueError, "Caption audit changed"):
            c.finalize(self.run, "fixture")

    def test_new_preview_cannot_inherit_old_caption_verification(self):
        labels, preview, audit, review = self.caption_fixture()
        c.review_attempt(self.run, 1, review, preview, labels, audit)
        c.review_attempt(self.run, 1, review, preview)
        self.assertNotIn("caption_audit", c.load(self.run / "state.json")["attempts"][0])

    def test_new_sources_invalidate_caption_verification(self):
        labels, preview, audit, review = self.caption_fixture()
        c.review_attempt(self.run, 1, review, preview, labels, audit)
        c.prepare(self.run, self.root / "spec.json", self.root / "checklist.json", self.root / "sources.json", update=True)
        self.assertNotIn("caption_audit", c.load(self.run / "state.json")["attempts"][0])

    def test_score_is_not_a_function_of_attempt_order(self):
        low = self.answer({"clarity": "fail"})
        high = self.answer()
        before = c.evaluate(self.checklist, high)
        c.evaluate(self.checklist, low)
        after = c.evaluate(self.checklist, high)
        self.assertEqual(before, after)
        self.assertEqual(after["total"], 100)
        # This tests arithmetic independence, not independence of the human/model observations.

    def test_jpeg_reference_does_not_allow_jpeg_generated_output(self):
        source = self.root / "approved.jpg"
        Image.new("RGB", (80, 60), "grey").save(source)
        n = c.reserve(self.run, self.prompt, [source])["attempt"]
        with self.assertRaises(ValueError):
            c.record(self.run, n, source)
        state = c.load(self.run / "state.json")
        self.assertEqual(len(state["attempts"]), 1)
        self.assertEqual(state["attempts"][0]["status"], "reserved")
        c.record(self.run, n, self.image)

    def test_style_reference_can_guide_appearance_but_not_construction(self):
        self.sources["sources"].append({"id": "approved", "kind": "style_reference",
                                       "url": "https://example.org/approved.jpg",
                                       "applicability": "appearance approved only", "verified": True})
        check = next(x for x in self.checklist["checks"] if x["block"] == "appearance")
        check["source_ids"] = ["approved"]
        c.validate_inputs(self.spec, self.checklist, self.sources)
        self.checklist["checks"][0]["source_ids"] = ["approved"]
        with self.assertRaises(ValueError):
            c.validate_inputs(self.spec, self.checklist, self.sources)

    def test_critical_partial_rejected(self):
        with self.assertRaises(ValueError):
            c.evaluate(self.checklist, self.answer({"construction": "partial"}))

    def test_partial_without_rule_rejected(self):
        with self.assertRaises(ValueError):
            c.evaluate(self.checklist, self.answer({"clarity": "partial"}))

    def test_unknown_is_not_critical_contradiction(self):
        score = c.evaluate(self.checklist, self.answer({"construction": "unknown"}))
        self.assertEqual(score["critical_unknown"], ["construction"])
        self.assertEqual(score["critical_errors"], [])

    def test_missing_check_rejected(self):
        answer = self.answer()
        answer["checks"].pop()
        with self.assertRaises(ValueError):
            c.evaluate(self.checklist, answer)

    def test_duplicate_check_rejected(self):
        answer = self.answer()
        answer["checks"].append(answer["checks"][0])
        with self.assertRaises(ValueError):
            c.evaluate(self.checklist, answer)

    def test_empty_observation_rejected(self):
        answer = self.answer()
        answer["checks"][0]["observation"] = ""
        with self.assertRaises(ValueError):
            c.evaluate(self.checklist, answer)

    def test_stale_review_version_rejected(self):
        answer = self.answer()
        answer["checklist_version"] = "old"
        with self.assertRaises(ValueError):
            c.evaluate(self.checklist, answer)

    def test_wrong_point_total_rejected(self):
        self.checklist["checks"][0]["points"] = 44
        with self.assertRaises(ValueError):
            c.validate_inputs(self.spec, self.checklist, self.sources)

    def test_nonfinite_points_rejected(self):
        self.checklist["checks"][0]["points"] = float("nan")
        with self.assertRaises(ValueError):
            c.validate_inputs(self.spec, self.checklist, self.sources)

    def test_analog_cannot_prove_target(self):
        self.sources["sources"][0]["kind"] = "analog"
        self.spec["nodes"][0]["evidence"] = "analog"
        with self.assertRaisesRegex(ValueError, "cannot prove"):
            c.validate_inputs(self.spec, self.checklist, self.sources)

    def test_evidence_mismatch_rejected(self):
        self.sources["sources"][0]["kind"] = "analog"
        with self.assertRaisesRegex(ValueError, "provenance"):
            c.validate_inputs(self.spec, self.checklist, self.sources)

    def test_no_eleventh_attempt_after_failures(self):
        for n in range(1, 11):
            self.assertEqual(c.reserve(self.run, self.prompt, [self.image])["attempt"], n)
            c.fail(self.run, n, "simulated failure")
        with self.assertRaisesRegex(ValueError, "limit"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_pending_attempt_blocks_another(self):
        c.reserve(self.run, self.prompt, [self.image])
        with self.assertRaisesRegex(ValueError, "unfinished"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_uncertain_result_can_be_recovered(self):
        c.reserve(self.run, self.prompt, [self.image])
        c.fail(self.run, 1, "lost response", unknown=True)
        c.record(self.run, 1, self.image)
        state = c.load(self.run / "state.json")
        self.assertEqual(len(state["attempts"]), 1)
        self.assertEqual(state["attempts"][0]["status"], "recorded")

    def test_existing_record_is_not_replaced(self):
        c.reserve(self.run, self.prompt, [self.image])
        c.record(self.run, 1, self.image)
        with self.assertRaisesRegex(ValueError, "resolved"):
            c.record(self.run, 1, self.image)

    def test_parallel_runs_are_separate(self):
        other = c.initialize(self.root / "runs", "test", "TEST", "https://example.org", self.image)
        self.assertNotEqual(other, self.run)
        c.reserve(self.run, self.prompt, [self.image])
        self.assertEqual(c.load(other / "state.json")["attempts"], [])

    def test_two_reservations_do_not_share_number(self):
        def task(_):
            try:
                return c.reserve(self.run, self.prompt, [self.image])
            except ValueError:
                return None
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(task, [1, 2]))
        self.assertEqual(sum(value is not None for value in results), 1)
        self.assertEqual(len(c.load(self.run / "state.json")["attempts"]), 1)

    def test_separate_processes_cannot_double_reserve(self):
        command = [sys.executable, str(SCRIPTS / "cutaway.py"), "reserve", "--run", str(self.run),
                   "--prompt-file", str(self.prompt), "--ref", str(self.image)]
        processes = [subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for _ in range(2)]
        outputs = [process.communicate(timeout=15) for process in processes]
        self.assertEqual(sorted(process.returncode for process in processes), [0,1])
        successful = [json.loads(out) for process, (out, err) in zip(processes, outputs) if process.returncode == 0]
        self.assertEqual(successful[0]["attempt"], 1)

    def test_critical_error_loses_to_lower_score_without_one(self):
        # Make the critical fact a small part of construction to test precedence.
        base = self.checklist["checks"][0]
        base["points"] = 1
        self.checklist["checks"].append({**base, "id": "other", "points": 44, "critical": False})
        self.write_inputs()
        c.prepare(self.run, self.root / "spec.json", self.root / "checklist.json", self.root / "sources.json", update=True)
        self.candidate({"construction": "fail"})  # 99, critical fail
        second = self.candidate({"appearance": "fail"})  # 90, no critical fail
        self.assertEqual(c.load(self.run / "state.json")["best"], second)

    def test_last_candidate_is_not_automatic_winner(self):
        first = self.candidate()
        self.candidate({"clarity": "fail"})
        result = c.finalize(self.run, "test completed")
        self.assertEqual(result["best"], first)
        self.assertTrue((self.run / "final/report.md").is_file())
        self.assertIn("clarity / fail", (self.run / "final/errors.md").read_text())
        self.assertTrue((self.run / "attempts/002/image.png").is_file())

    def test_unreviewed_candidate_blocks_final(self):
        self.candidate()
        c.reserve(self.run, self.prompt, [self.image])
        c.record(self.run, 2, self.image)
        with self.assertRaisesRegex(ValueError, "every available"):
            c.finalize(self.run, "premature")

    def test_new_inputs_invalidate_all_old_scores(self):
        self.candidate()
        self.checklist["version"] = "v2"
        self.write_inputs()
        c.prepare(self.run, self.root / "spec.json", self.root / "checklist.json", self.root / "sources.json", update=True)
        state = c.load(self.run / "state.json")
        self.assertIsNone(state["best"])
        self.assertNotIn("score", state["attempts"][0])
        self.assertTrue((self.run / "inputs/v1/checklist.json").exists())
        with self.assertRaises(ValueError):
            c.finalize(self.run, "old scores cannot be used")

    def test_modified_candidate_requires_new_review(self):
        self.candidate()
        Image.new("RGB", (900, 600), "red").save(self.run / "attempts/001/image.png")
        with self.assertRaisesRegex(ValueError, "changed"):
            c.finalize(self.run, "tampering")

    def test_prepare_required_before_generation(self):
        other = c.initialize(self.root / "runs", "other", "TEST", "https://example.org", self.image)
        with self.assertRaisesRegex(ValueError, "Prepare"):
            c.reserve(other, self.prompt, [self.image])

    def test_edit_requires_real_parent(self):
        with self.assertRaises(ValueError):
            c.reserve(self.run, self.prompt, [self.image], kind="edit")

    def test_modified_sources_block_finalization(self):
        self.candidate()
        state = c.load(self.run / "state.json")
        path = self.run / state["inputs_dir"] / "sources.json"
        data = c.load(path)
        data["sources"][0]["applicability"] = "a different product"
        c.atomic_json(path, data)
        with self.assertRaisesRegex(ValueError, "Frozen inputs"):
            c.finalize(self.run, "must not reuse stale evidence")

    def test_modified_spec_blocks_next_generation(self):
        state = c.load(self.run / "state.json")
        path = self.run / state["inputs_dir"] / "spec.json"
        data = c.load(path)
        data["model"] = "DIFFERENT"
        c.atomic_json(path, data)
        with self.assertRaisesRegex(ValueError, "Frozen inputs"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_modified_losing_candidate_blocks_finalization(self):
        self.candidate()
        self.candidate({"clarity": "fail"})
        Image.new("RGB", (900,600), "red").save(self.run / "attempts/002/image.png")
        with self.assertRaisesRegex(ValueError, "changed"):
            c.finalize(self.run, "all compared candidates must remain unchanged")

    def test_label_only_revision_preserves_generation_count(self):
        self.candidate()
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"labels": [{"id": "a", "text": "Двигатель", "position": [.05,.05], "font_size": 24}]})
        preview = self.root / "preview.png"
        layout.compose(self.image, labels, preview)
        review = self.root / "revision.json"
        c.atomic_json(review, self.answer())
        c.review_attempt(self.run, 1, review, preview)
        state = c.load(self.run / "state.json")
        self.assertEqual(len(state["attempts"]), 1)
        self.assertEqual(len(state["attempts"][0]["reviews"]), 2)
        self.assertTrue((self.run / "attempts/001/preview-02.png").is_file())

    def test_cyrillic_png_and_layout_record(self):
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"labels": [{"id": "a", "text": "Давление\nводы", "position": [.1,.1], "target": [.5,.5]}]})
        out = self.root / "composed.png"
        result = layout.compose(self.image, labels, out)
        self.assertFalse(result["semantic_targets_checked"])
        self.assertTrue(out.with_suffix(".layout.json").exists())
        with Image.open(out) as img:
            self.assertNotEqual(img.getbbox(), None)
            self.assertGreater(len(img.getcolors(maxcolors=100000)), 1)

    def test_clipped_label_rejected(self):
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"labels": [{"text": "Long label", "position": [.98,.98]}]})
        with self.assertRaisesRegex(ValueError, "outside"):
            layout.compose(self.image, labels, self.root / "out.png")

    def test_overlapping_labels_rejected(self):
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"labels": [{"id": "a", "text": "One", "position": [.1,.1]},
                                         {"id": "b", "text": "Two", "position": [.1,.1]}]})
        with self.assertRaisesRegex(ValueError, "overlap"):
            layout.compose(self.image, labels, self.root / "out.png")

    def test_coordinate_nan_rejected(self):
        with self.assertRaises(ValueError):
            layout.point([float("nan"), .5], (900,600))

    def test_canvas_adds_label_margins_without_changing_base(self):
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"canvas": {"size": [1200, 900], "image_box": [150,150,1050,750]},
                               "title": {"text": "Двигатель", "position": [.02,.02]}})
        before = c.digest(self.image)
        out = self.root / "out.png"
        layout.compose(self.image, labels, out)
        with Image.open(out) as composed:
            self.assertEqual(composed.size, (1200,900))
        self.assertEqual(c.digest(self.image), before)

    def test_image_box_outside_canvas_rejected(self):
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"canvas": {"size": [1200,900], "image_box": [0,0,1500,900]},
                               "title": {"text": "Test", "position": [.02,.02]}})
        with self.assertRaisesRegex(ValueError, "outside"):
            layout.compose(self.image, labels, self.root / "out.png")

    def test_source_target_accounts_for_letterboxing(self):
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"canvas": {"size": [1200,1200], "image_box": [100,100,1100,1100]},
            "labels": [{"id":"part","text":"Part","position":[.02,.02],"target_image":[0,0]}]})
        result = layout.compose(self.image, labels, self.root / "out.png")
        # 900x600 fitted in a square needs a vertical white band.
        self.assertGreater(result["image_bounds"][1], 100)
        self.assertEqual(result["target_points"]["part"], result["image_bounds"][:2])

    def test_mixed_target_coordinate_spaces_rejected(self):
        labels = self.root / "labels.json"
        c.atomic_json(labels, {"labels":[{"text":"Part","position":[.02,.02],
                                        "target":[.5,.5],"target_image":[.5,.5]}]})
        with self.assertRaisesRegex(ValueError, "not both"):
            layout.compose(self.image, labels, self.root / "out.png")


if __name__ == "__main__":
    unittest.main()
