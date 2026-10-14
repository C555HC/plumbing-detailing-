"""v1.2 contract regressions. All images/facts are synthetic, not engineering approval."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

import test_cutaway as fixtures
from test_cutaway import SCRIPTS, c, module

sys.path.insert(0, str(SCRIPTS))
cache = module("source_cache")


class V12Tests(unittest.TestCase):
    def setUp(self):
        # Reuse only fixture construction, not the historical tests or legacy policy.
        fixtures.ScoringV2Tests.setUp(self)
        self.run = c.initialize(self.root / "modern", "test", "TEST", "https://example.org/card", self.image)
        self.sources["sources"].append({"id": "photo", "kind": "product_photo", "url": "https://example.org/photo.png",
                                        "applicability": "Synthetic exterior", "verified": True})
        self.origin = self.root / "origin.json"
        c.atomic_json(self.origin, {"source_kind": "store", "model": "TEST", "sku": "SKU-1", "title_verbatim": "Test product",
                                   "source_url": "https://example.org/card", "image_url": "https://example.org/photo.png"})
        c.register_intake(self.run, self.origin)
        (self.run / "input/construction-plan.md").write_text("Synthetic membrane topology and cut plane; not a factory source")

    check = fixtures.ScoringV2Tests.check
    answer = fixtures.ScoringV2Tests.answer

    def prepare(self, update=False, evidence=True):
        result = fixtures.ScoringV2Tests.prepare(self, update)
        if evidence:
            for source in self.sources["sources"]:
                c.archive_evidence(self.run, source["id"], "Synthetic fixture", "Synthetic evidence only", file=self.image)
        return result

    def generated(self):
        n = c.reserve(self.run, self.prompt, [self.image])["attempt"]
        c.dispatch(self.run, n)
        c.record(self.run, n, self.image)
        return n

    def reviewed(self, n, statuses=None, reason=None, **kwargs):
        review = self.answer({"captions": "unknown", **(statuses or {})})
        if reason:
            review["reassessment_reason"] = reason
        path = self.root / "review.json"
        c.atomic_json(path, review)
        return c.review_attempt(self.run, n, path, **kwargs)

    def captioned(self, n, statuses=None):
        labels = self.root / "labels.json"
        audit = self.root / "audit.json"
        preview = self.root / "preview.png"
        preview.write_bytes(self.image.read_bytes())
        c.atomic_json(labels, {"labels": [{"id": "membrane", "text": "Membrane", "position": [0.1, 0.1], "target": [0.5, 0.5]}]})
        c.atomic_json(audit, {"base_sha256": c.digest(self.image), "labels_sha256": c.digest(labels), "preview_sha256": c.digest(preview),
                              "layout_checked": True, "title_checked": True, "checks": [{"id": "membrane", "source_ids": ["manual"],
                              "locator": "fixture", "text_checked": True, "target_checked": True, "observation": "Synthetic target audit"}]})
        return self.reviewed(n, {"captions": "pass", **(statuses or {})}, preview=preview, labels_path=labels, label_review_path=audit)

    def test_caption_composition_cannot_promote_geometry(self):
        self.prepare()
        n = self.generated()
        base = self.reviewed(n, {"attachment": "unknown"})
        self.assertGreaterEqual(base["rating"], 90)
        with self.assertRaisesRegex(ValueError, "cannot change non-caption"):
            self.captioned(n)
        after = self.captioned(n, {"attachment": "unknown"})
        self.assertEqual(base["rating"], after["rating"])
        self.assertEqual(after["caption_status"], "checked")

    def test_reassessment_requires_reason_and_preserves_review(self):
        self.prepare(); n = self.generated()
        self.reviewed(n, {"shape": "unknown"})
        with self.assertRaisesRegex(ValueError, "reassessment reason"):
            self.reviewed(n)
        self.reviewed(n, reason="Re-inspected the visible fixture against saved diagram")
        a = c.load(self.run / "state.json")["attempts"][0]
        self.assertEqual(len(a["reviews"]), 2)
        self.assertEqual(len(a["score_history"]), 1)

    def test_only_selected_candidate_requires_captions(self):
        self.prepare()
        a = self.generated(); self.reviewed(a, {"attachment": "unknown"})
        b = self.generated(); self.reviewed(b)
        self.captioned(b)
        result = c.finalize(self.run, "Synthetic completed fixture")
        self.assertEqual(result["best"], b)
        self.assertFalse(c.load(self.run / "state.json")["attempts"][0].get("caption_audit"))

    def test_selected_90_requires_caption_audit(self):
        self.prepare(); n = self.generated(); self.reviewed(n)
        with self.assertRaisesRegex(ValueError, "Compose and inspect captions"):
            c.finalize(self.run, "Fixture")

    def test_below_90_returns_honest_unlabelled_result(self):
        self.prepare(); n = self.generated()
        result = self.reviewed(n, {"shape": "unknown"})
        self.assertLess(result["rating"], 90)
        with self.assertRaisesRegex(ValueError, "90 or above"):
            self.captioned(n, {"shape": "unknown"})
        self.assertEqual(c.finalize(self.run, "Evidence insufficient; stop") ["rating"], result["rating"])

    def test_fixed_denominator_unknown_and_appearance(self):
        self.prepare()
        answer = self.answer({"captions": "unknown", "shape": "unknown", "exterior": "fail"})
        score = c.evaluate(self.checklist, answer, separate_ratings=True)
        self.assertAlmostEqual(score["total"], 70 / 85 * 100)
        self.assertEqual(score["appearance_rating"], 0)
        answer["checks"][-2]["status"] = "pass"
        self.assertEqual(score["total"], c.evaluate(self.checklist, answer, separate_ratings=True)["total"])

    def test_analog_construction_is_reconstruction_not_factory_approval(self):
        self.sources["sources"][0]["kind"] = "analog"
        self.spec["nodes"][0]["evidence"] = "analog"
        for check in self.checklist["checks"]:
            check["evidence_level"] = "analog"
        self.prepare(); n = self.generated(); result = self.reviewed(n)
        self.assertEqual(result["rating"], 100)
        self.assertEqual(result["readiness"]["status"], "needs_technical_review")
        self.assertFalse(result["readiness"]["technical_approval"])

    def test_technical_checks_cannot_depend_on_captions(self):
        self.check("shape")["caption_dependent"] = True
        with self.assertRaisesRegex(ValueError, "cannot depend on captions"):
            self.prepare()

    def test_provenance_plan_and_evidence_required(self):
        other = c.initialize(self.root / "empty", "test", "TEST", "https://example.org", self.image)
        original = self.run
        self.run = other
        with self.assertRaisesRegex(ValueError, "Register product origin"):
            self.prepare()
        c.register_intake(self.run, self.origin)
        with self.assertRaises(FileNotFoundError):
            self.prepare()
        self.run = original
        self.prepare(evidence=False)
        with self.assertRaisesRegex(ValueError, "Archive evidence"):
            c.reserve(self.run, self.prompt, [self.image])
        for source in self.sources["sources"]:
            c.archive_evidence(self.run, source["id"], "fixture", "Inspected fixture, local asset unavailable", gap="Synthetic archive gap")
        self.assertEqual(c.reserve(self.run, self.prompt, [self.image])["attempt"], 1)

    def test_manufacturer_photo_fallback(self):
        origin = c.load(self.origin); origin["source_kind"] = "manufacturer"
        c.atomic_json(self.origin, origin)
        with self.assertRaisesRegex(ValueError, "fallback reason"):
            c.register_intake(self.run, self.origin)
        origin.update(fallback_reason="Exact SKU not listed at store; official model photo verified", sku=None)
        c.atomic_json(self.origin, origin)
        c.register_intake(self.run, self.origin)
        self.prepare()

    def test_origin_and_plan_integrity(self):
        self.prepare()
        (self.run / "inputs/v1/construction-plan.md").write_text("changed")
        with self.assertRaisesRegex(ValueError, "Frozen inputs changed"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_cache_corruption_blocks_reserve_and_dispatch(self):
        self.prepare()
        n = c.reserve(self.run, self.prompt, [self.image])["attempt"]
        state = c.load(self.run / "state.json"); ref = self.run / state["attempts"][0]["refs"][0]["path"]
        ref.write_bytes(b"corrupt")
        with self.assertRaisesRegex(ValueError, "Cached reference changed"):
            c.dispatch(self.run, n)
        c.fail(self.run, n, "Pre-dispatch corrupt cache", not_sent=True)
        with self.assertRaisesRegex(ValueError, "Cached reference changed"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_changed_review_blocks_finalization(self):
        self.prepare(); n = self.generated(); self.reviewed(n, {"shape": "unknown"})
        a = c.load(self.run / "state.json")["attempts"][0]
        review_path = self.run / a["reviews"][0]
        review = c.load(review_path); review["summary"] = "tampered"
        c.atomic_json(review_path, review)
        with self.assertRaisesRegex(ValueError, "Saved review changed"):
            c.finalize(self.run, "Fixture")

    def test_changed_score_blocks_finalization(self):
        self.prepare(); n = self.generated(); self.reviewed(n, {"shape": "unknown"})
        path = self.run / "state.json"; state = c.load(path)
        state["attempts"][0]["score"]["total"] = 100
        c.atomic_json(path, state)
        with self.assertRaisesRegex(ValueError, "Saved score changed"):
            c.finalize(self.run, "Fixture")

    def test_unknown_response_blocks_new_call_and_finalization(self):
        self.prepare(); n = self.generated(); self.reviewed(n, {"shape": "unknown"})
        n = c.reserve(self.run, self.prompt, [self.image])["attempt"]; c.dispatch(self.run, n)
        c.fail(self.run, n, "No response yet", unknown=True)
        with self.assertRaisesRegex(ValueError, "unfinished"):
            c.reserve(self.run, self.prompt, [self.image])
        with self.assertRaisesRegex(ValueError, "unfinished"):
            c.finalize(self.run, "Fixture")
        c.resolve_unknown(self.run, n, "Tool job explicitly returned an error; checked for late image")
        c.reserve(self.run, self.prompt, [self.image])

    def test_recovered_unknown_reuses_same_attempt(self):
        self.prepare(); n = c.reserve(self.run, self.prompt, [self.image])["attempt"]; c.dispatch(self.run, n)
        c.fail(self.run, n, "Timed out", unknown=True)
        c.record(self.run, n, self.image)
        self.assertEqual(len(c.load(self.run / "state.json")["attempts"]), 1)

    def test_five_received_plus_two_failures_seven_calls(self):
        self.prepare()
        for _ in range(2):
            n = c.reserve(self.run, self.prompt, [self.image])["attempt"]; c.dispatch(self.run, n)
            c.fail(self.run, n, "Confirmed backend error")
        for _ in range(5):
            self.generated()
        state = c.load(self.run / "state.json"); summary = c.status_summary(state)
        self.assertEqual((summary["used"], summary["remaining"], summary["calls_dispatched"]), (5, 0, 7))
        with self.assertRaisesRegex(ValueError, "limit exhausted"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_third_failure_exhausts_retries(self):
        self.prepare()
        for _ in range(3):
            n = c.reserve(self.run, self.prompt, [self.image])["attempt"]; c.dispatch(self.run, n)
            c.fail(self.run, n, "Confirmed error")
        with self.assertRaisesRegex(ValueError, "limit exhausted"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_dispatch_boundary_no_duplicate_or_false_not_sent(self):
        self.prepare(); n = c.reserve(self.run, self.prompt, [self.image])["attempt"]
        with self.assertRaisesRegex(ValueError, "Record dispatch"):
            c.record(self.run, n, self.image)
        c.dispatch(self.run, n)
        with self.assertRaisesRegex(ValueError, "already dispatched"):
            c.dispatch(self.run, n)
        with self.assertRaisesRegex(ValueError, "cannot be declared not sent"):
            c.fail(self.run, n, "Not sent", not_sent=True)

    def test_packet_contains_facts_and_assets_but_no_iteration_hints(self):
        self.prepare(); n = self.generated(); self.reviewed(n, {"shape": "unknown"})
        result = c.review_packet(self.run, n, self.root / "packets")
        packet = Path(result["packet"])
        facts = c.load(packet / "facts.json")
        forbidden = {"total", "rating", "score", "prompt", "points", "attempt", "summary", "reviews"}
        def inspect(value):
            if isinstance(value, dict):
                self.assertFalse(set(value) & forbidden)
                for v in value.values(): inspect(v)
            elif isinstance(value, list):
                for v in value: inspect(v)
        inspect(facts)
        self.assertEqual(c.digest(packet / "candidate.png"), c.digest(self.image))
        self.assertNotIn("captions", [check["id"] for check in facts["checks"]])
        self.assertTrue(facts["evidence"])
        self.assertNotIn("attempts", str(packet))

    def test_continuation_preserves_parent_and_reuses_frozen_assets(self):
        self.prepare(); n = self.generated(); self.reviewed(n, {"shape": "unknown"})
        before = c.load(self.run / "state.json")
        result = c.continue_run(self.run, self.root / "continued", "User asks to correct the membrane", n)
        child = Path(result["run"]); state = c.load(child / "state.json")
        self.assertEqual(state["attempts"], [])
        self.assertEqual(state["input_hashes"], before["input_hashes"])
        self.assertEqual(c.digest(result["edit_seed"]), c.digest(self.image))
        c.reserve(child, self.prompt, [result["edit_seed"]])
        self.assertEqual(len(c.load(self.run / "state.json")["attempts"]), 1)

    def test_source_cache_keys_include_model_revision_and_locator(self):
        args = ("https://example.org/manual", "TEST", "rev-1", "page-1")
        result = cache.put(self.root / "cache", self.image, *args, "Applies to synthetic model TEST only")
        self.assertEqual(cache.get(self.root / "cache", *args)["sha256"], c.digest(self.image))
        with self.assertRaises(FileNotFoundError):
            cache.get(self.root / "cache", args[0], "OTHER", *args[2:])
        Path(result["file"]).write_bytes(b"broken")
        with self.assertRaisesRegex(ValueError, "integrity mismatch"):
            cache.get(self.root / "cache", *args)

    def test_loser_is_not_captioned(self):
        self.prepare()
        loser = self.generated(); self.reviewed(loser, {"attachment": "unknown"})
        best = self.generated(); self.reviewed(best)
        with self.assertRaisesRegex(ValueError, "currently selected"):
            self.captioned(loser, {"attachment": "unknown"})

    def test_worse_later_candidate_does_not_replace_leader(self):
        self.prepare()
        best = self.generated(); self.reviewed(best)
        later = self.generated(); result = self.reviewed(later, {"type_count": "fail", "shape": "unknown"})
        self.assertLess(result["rating"], 100)
        self.assertEqual(result["best"], best)

    def test_reserved_prompt_integrity(self):
        self.prepare(); n = c.reserve(self.run, self.prompt, [self.image])["attempt"]
        a = c.load(self.run / "state.json")["attempts"][0]
        (self.run / a["prompt"]).write_text("accidentally changed prompt")
        with self.assertRaisesRegex(ValueError, "prompt changed"):
            c.dispatch(self.run, n)

    def test_prepare_bundle_uses_same_guards_and_freezes_plan(self):
        bundle = self.root / "bundle.json"
        c.atomic_json(bundle, {"spec": self.spec, "sources": self.sources, "checklist": self.checklist,
                              "construction_plan": "Explicit synthetic mating and cut plan"})
        result = c.prepare_bundle(self.run, bundle)
        self.assertEqual(result["inputs_version"], 1)
        self.assertIn("mating", (self.run / "inputs/v1/construction-plan.md").read_text())
        with self.assertRaisesRegex(ValueError, "Archive evidence"):
            c.reserve(self.run, self.prompt, [self.image])

    def test_input_update_invalidates_scores_but_keeps_history(self):
        self.prepare(); n = self.generated(); self.reviewed(n)
        self.checklist["version"] = "fixture-v2-revised"
        self.prepare(update=True)
        state = c.load(self.run / "state.json"); a = state["attempts"][0]
        self.assertNotIn("score", a)
        self.assertTrue(a["score_history"])
        with self.assertRaisesRegex(ValueError, "Review every available"):
            c.finalize(self.run, "Fixture")
        self.reviewed(n, {"shape": "unknown"})
        c.finalize(self.run, "Revised facts insufficient")

    def test_readiness_precedes_number_for_modern_selection(self):
        self.prepare(); state = c.load(self.run / "state.json")
        def candidate(number, score, status):
            return {"id": number, "score": {"checklist_sha256": state["checklist_sha256"], "total": score,
                    "critical_errors": [], "readiness": {"status": status}}}
        state["attempts"] = [candidate(1, 99, "needs_technical_review"), candidate(2, 92, "ready_for_technical_review")]
        self.assertEqual(c.scored_candidates(state)[0]["id"], 2)

    def test_concurrent_source_cache_writes_preserve_one_asset(self):
        from concurrent.futures import ThreadPoolExecutor
        args = (self.root / "cache", self.image, "https://example.org/doc", "TEST", "rev-1", "page-1", "Synthetic fixture only")
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda _: cache.put(*args), range(4)))
        self.assertEqual(len({result["sha256"] for result in results}), 1)

    def test_caption_before_base_is_rejected_cleanly(self):
        self.prepare(); n = self.generated()
        with self.assertRaisesRegex(ValueError, "currently selected"):
            self.captioned(n)

    def test_cli_roundtrip(self):
        def cli(*args):
            result = subprocess.run([sys.executable, str(SCRIPTS / "cutaway.py"), *map(str, args)],
                                    capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        bundle = self.root / "bundle.json"
        c.atomic_json(bundle, {"spec": self.spec, "checklist": self.checklist, "sources": self.sources,
                              "construction_plan": "Synthetic shape, attachment, cut and passage plan"})
        cli("prepare", "--run", self.run, "--bundle", bundle)
        for source in self.sources["sources"]:
            cli("archive-evidence", "--run", self.run, "--source-id", source["id"], "--locator", "fixture",
                "--observation", "Synthetic source fixture", "--gap", "Synthetic test: no live source")
        n = cli("reserve", "--run", self.run, "--prompt-file", self.prompt, "--ref", self.image)["attempt"]
        cli("dispatch", "--run", self.run, "--attempt", n)
        cli("record", "--run", self.run, "--attempt", n, "--image", self.image)
        review = self.root / "review-cli.json"
        c.atomic_json(review, self.answer({"captions": "unknown", "shape": "unknown"}))
        cli("review", "--run", self.run, "--attempt", n, "--review-file", review)
        result = cli("finalize", "--run", self.run, "--reason", "Synthetic evidence insufficient")
        self.assertTrue(Path(result["image"]).exists())
        self.assertLess(result["rating"], 90)
        report = Path(result["report"]).read_text()
        self.assertIn("Технический рейтинг", report)
        self.assertNotIn("Баллы, добавленные за подписи", report)
        self.assertEqual(c.load(self.run / "final/ranking.json")[0]["rating_policy"], "technical_85_normalized_v1.2")

    def test_cli_modern_defaults_and_intake(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "cutaway.py"), "status", "--run", str(self.run), "--compact"],
                                capture_output=True, text=True, check=True)
        state = json.loads(result.stdout)
        self.assertEqual((state["workflow_version"], state["retry_limit"], state["caption_threshold"]), ("1.2", 2, 90))


if __name__ == "__main__":
    unittest.main()
