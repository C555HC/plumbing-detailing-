#!/usr/bin/env python3
"""Render editable Russian labels and leader lines onto a generated base PNG."""
import argparse
import json
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps


def font_path(explicit=None):
    candidates = [explicit] if explicit else [
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"]
    for path in candidates:
        if path and Path(path).is_file():
            return str(Path(path).resolve())
    raise ValueError("Supply --font pointing to a TrueType font with Cyrillic glyphs")


def point(value, size):
    if not isinstance(value, list) or len(value) != 2 or any(
            isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) or not 0 <= v <= 1 for v in value):
        raise ValueError("Coordinates must be two finite values in 0..1")
    return tuple(round(v * (n - 1)) for v, n in zip(value, size))


def compose(image, labels_path, output, font=None):
    labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    with Image.open(image) as img:
        base = Image.new("RGB", img.size, "white")
        if img.mode == "RGBA":
            base.paste(img, mask=img.getchannel("A"))
        else:
            base.paste(img.convert("RGB"))
    config = labels.get("canvas")
    source_size = list(base.size)
    image_bounds = [0, 0, base.width, base.height]
    if config:
        size = config.get("size")
        box = config.get("image_box")
        if not isinstance(size, list) or len(size) != 2 or any(type(v) is not int or not 32 <= v <= 8192 for v in size):
            raise ValueError("Invalid canvas size")
        if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
            raise ValueError("Invalid image_box")
        if not (0 <= box[0] < box[2] <= size[0] and 0 <= box[1] < box[3] <= size[1]):
            raise ValueError("image_box outside canvas")
        canvas = Image.new("RGB", size, "white")
        placed = ImageOps.contain(base, (box[2]-box[0], box[3]-box[1]))
        offset = (box[0]+(box[2]-box[0]-placed.width)//2,
                  box[1]+(box[3]-box[1]-placed.height)//2)
        canvas.paste(placed, offset)
        image_bounds = [offset[0], offset[1], offset[0]+placed.width, offset[1]+placed.height]
    else:
        canvas = base
    path = font_path(font or labels.get("font"))
    draw = ImageDraw.Draw(canvas)
    color = labels.get("color", "#073C76")
    items = ([labels["title"]] if labels.get("title") else []) + labels.get("labels", [])
    if not items:
        raise ValueError("No title or labels")
    boxes, seen, warnings, target_points = [], set(), [], {}
    for i, item in enumerate(items):
        identifier = item.get("id", "title" if i == 0 and labels.get("title") else str(i))
        if identifier in seen:
            raise ValueError("Duplicate label ID")
        seen.add(identifier)
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Labels need nonempty text")
        size = item.get("font_size", 30)
        if isinstance(size, bool) or not isinstance(size, int) or not 8 <= size <= 200:
            raise ValueError("Invalid font_size")
        face = ImageFont.truetype(path, size)
        origin = point(item["position"], canvas.size)
        box = draw.multiline_textbbox(origin, text, font=face, spacing=6)
        if box[0] < 0 or box[1] < 0 or box[2] >= canvas.width or box[3] >= canvas.height:
            raise ValueError(f"Text outside canvas: {identifier}")
        for previous, other in boxes:
            if box[0] < other[2] and box[2] > other[0] and box[1] < other[3] and box[3] > other[1]:
                raise ValueError(f"Text overlap: {identifier} / {previous}")
        boxes.append((identifier, box))
        if "target" in item or "target_image" in item:
            if "target" in item and "target_image" in item:
                raise ValueError("Choose target (canvas) or target_image (source), not both")
            if "target_image" in item:
                local = point(item["target_image"], (image_bounds[2]-image_bounds[0], image_bounds[3]-image_bounds[1]))
                target = (image_bounds[0]+local[0], image_bounds[1]+local[1])
            else:
                target = point(item["target"], canvas.size)
            target_points[identifier] = list(target)
            start = point(item.get("line_start", item["position"]), canvas.size)
            route = [start]
            if "elbow" in item:
                route.append(point(item["elbow"], canvas.size))
            route.append(target)
            draw.line(route, fill=color, width=3)
            r = 6
            draw.ellipse((target[0]-r, target[1]-r, target[0]+r, target[1]+r), fill=color, outline="white", width=2)
            for previous, other in boxes:
                if previous != identifier and other[0] <= target[0] <= other[2] and other[1] <= target[1] <= other[3]:
                    warnings.append(f"Target {identifier} is inside text {previous}")
        draw.multiline_text(origin, text, font=face, fill=color, spacing=6)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.resolve() == Path(image).resolve():
        raise ValueError("Output must not replace the base image")
    canvas.save(output, format="PNG")
    result = {"image": str(output.resolve()), "font": path,
              "label_boxes": {key: list(box) for key, box in boxes}, "warnings": warnings,
              "source_size": source_size, "image_bounds": image_bounds, "target_points": target_points,
              "semantic_targets_checked": False}
    output.with_suffix(".layout.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("image", "labels", "output"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--font")
    args = parser.parse_args()
    try:
        print(json.dumps(compose(args.image, args.labels, args.output, args.font), ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
