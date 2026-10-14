"""Real text rendering and geometry checks for automatic callout layout."""
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw, ImageFont
from test_cutaway import SCRIPTS, c, layout


class AutoLayoutTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.image = self.root / "base.png"
        # Coloured source makes accidental edits/resizing/covering visible in pixel comparisons.
        Image.new("RGB", (600, 400), (70, 100, 130)).save(self.image)
        self.labels = self.root / "labels.json"
        self.output = self.root / "out.png"

    def render(self, items, **kwargs):
        payload = {"canvas": {"size": [1100, 700], "image_box": [250, 140, 850, 540]},
                   "labels": items, **kwargs}
        c.atomic_json(self.labels, payload)
        return layout.compose(self.image, self.labels, self.output)

    def assert_valid(self, result):
        width, height = result["canvas_size"]
        boxes = list(result["label_boxes"].values())
        for box in boxes:
            self.assertTrue(0 <= box[0] < box[2] <= width)
            self.assertTrue(0 <= box[1] < box[3] <= height)
            self.assertFalse(layout.intersects(box, result["image_bounds"]))
        for i, box in enumerate(boxes):
            for other in boxes[i+1:]:
                self.assertFalse(layout.intersects(box, other))

    def test_overlapping_hints_are_repositioned(self):
        result = self.render([{"id": "a", "text": "Корпус", "position": [.02, .3]},
                              {"id": "b", "text": "Рабочее колесо", "position": [.02, .3]}])
        self.assert_valid(result)
        self.assertNotEqual(result["label_boxes"]["a"], result["label_boxes"]["b"])
        self.assertTrue(any("Moved" in note for note in result["adjustments"]))

    def test_clipped_hints_move_inside_canvas(self):
        result = self.render([{"id": "a", "text": "Встроенный обратный клапан", "position": [1, 1]}])
        self.assert_valid(result)

    def test_wraps_long_russian_text_without_losing_words(self):
        text = "Многоступенчатая гидравлическая часть из нержавеющей стали"
        result = self.render([{"id": "a", "text": text, "position": [.02, .2], "max_width": 160}])
        self.assertIn("\n", result["rendered_text"]["a"])
        self.assertEqual(result["rendered_text"]["a"].split(), text.split())
        self.assert_valid(result)

    def test_unbreakable_sku_preserves_every_character(self):
        text = "VTc.586.EMNX.0606-12345678901234567890"
        result = self.render([{"id": "a", "text": text, "position": [.02, .2], "max_width": 150, "break_long_words": True}])
        self.assertEqual(result["rendered_text"]["a"].replace("\n", ""), text)
        self.assert_valid(result)

    def test_targets_do_not_move_when_only_text_moves(self):
        result = self.render([{"id": "a", "text": "Двигатель", "position": [1, 1], "target_image": [.4, .6]},
                              {"id": "b", "text": "Ротор", "position": [1, 1], "target": [.6, .4]}])
        self.assertEqual(result["canvas_translation"], [0, 0])
        self.assertEqual(result["target_points"]["a"], [250+round(.4*599), 140+round(.6*399)])
        self.assertEqual(result["target_points"]["b"], list(layout.point([.6, .4], (1100, 700))))
        self.assert_valid(result)

    def test_crowded_layout_adds_white_space_not_smaller_text(self):
        items = [{"id": str(i), "text": "Регулирующий клапан контура " + str(i), "font_size": 28,
                  "position": [.02, .2], "target_image": [.2 + i*.01, .3]} for i in range(40)]
        result = self.render(items)
        self.assertNotEqual(result["canvas_translation"], [0, 0])
        self.assertGreater(result["canvas_size"][1], 700)
        self.assert_valid(result)
        for i in range(40):
            expected = [250+round((.2+i*.01)*599)+result["canvas_translation"][0],
                        140+round(.3*399)+result["canvas_translation"][1]]
            self.assertEqual(result["target_points"][str(i)], expected)

    def test_raw_source_gets_gutters_and_remains_pixel_identical(self):
        before = c.digest(self.image)
        c.atomic_json(self.labels, {"labels": [{"id": "a", "text": "Корпус", "position": [.01, .01], "font_size": 30}]})
        result = layout.compose(self.image, self.labels, self.output)
        self.assert_valid(result)
        self.assertNotEqual(result["canvas_translation"], [0, 0])
        self.assertEqual(before, c.digest(self.image))
        with Image.open(self.output) as out, Image.open(self.image) as original:
            self.assertEqual(out.crop(result["image_bounds"]).tobytes(), original.tobytes())

    def test_routes_reanchor_at_moved_text_and_keep_endpoint(self):
        result = self.render([{"id": "a", "text": "Двигатель", "position": [1, 1],
                               "line_start": [1, 1], "elbow": [1, .5], "target_image": [.5, .5]}])
        path = result["leader_paths"]["a"]
        self.assertEqual(path[-1], result["target_points"]["a"])
        self.assertNotEqual(path[0], list(layout.point([1, 1], result["canvas_size"])))
        self.assertFalse(result["warnings"])

    def test_strict_mode_accepts_exclusive_right_and_bottom_boundary(self):
        face = ImageFont.truetype(layout.font_path(), 30)
        box = ImageDraw.Draw(Image.new("RGB", (200, 200))).textbbox((0, 0), "TEST", font=face)
        shift = max(0, -box[0])
        width = box[2] + shift
        Image.new("RGB", (width, box[3]), "white").save(self.image)
        c.atomic_json(self.labels, {"layout_mode": "strict", "labels": [{"text": "TEST", "font_size": 30, "position": [shift/(width-1), 0]}]})
        result = layout.compose(self.image, self.labels, self.output)
        self.assertEqual(result["label_boxes"]["0"][2:], [width, box[3]])

    def test_auto_preserves_font_size(self):
        result = self.render([{"id": "a", "text": "Очень длинная подпись с переносами строк", "position": [1, 1], "font_size": 38}])
        face = ImageFont.truetype(result["font"], 38)
        expected = ImageDraw.Draw(Image.new("RGB", (500,500))).multiline_textbbox((0,0), result["rendered_text"]["a"], font=face, spacing=6)
        self.assertEqual(result["label_boxes"]["a"][3]-result["label_boxes"]["a"][1], expected[3]-expected[1])

    def test_bad_data_still_rejected_without_output(self):
        for entry in [{"text": "A", "position": [float("nan"), 0]},
                      {"text": "A", "position": [0, 0], "max_width": -1},
                      {"text": "A", "position": [0, 0], "target": [.5,.5], "target_image": [.5,.5]}]:
            with self.subTest(entry=entry), self.assertRaises(ValueError):
                self.render([entry])
            self.assertFalse(self.output.exists())

    def test_repeat_render_is_deterministic(self):
        items = [{"id": str(i), "text": "Корпус клапана " + str(i), "position": [.02,.4]} for i in range(7)]
        first = self.render(items)
        checksum = c.digest(self.output)
        second = self.render(items)
        self.assertEqual(first, second)
        self.assertEqual(checksum, c.digest(self.output))

    def test_cli_defaults_to_auto(self):
        c.atomic_json(self.labels, {"labels": [{"text": "Насос", "position": [1,1]}]})
        completed = subprocess.run([sys.executable, str(SCRIPTS/'compose_png.py'), '--image', str(self.image),
                                   '--labels', str(self.labels), '--output', str(self.output)], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(completed.stdout)["layout_mode"], "auto")


if __name__ == "__main__":
    unittest.main()
