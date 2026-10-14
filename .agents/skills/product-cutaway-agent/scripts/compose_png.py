#!/usr/bin/env python3
"""Compose Russian callouts with deterministic wrapping/placement; never infer part identities."""
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


def intersects(a, b, gap=0):
    return a[0] < b[2] + gap and a[2] + gap > b[0] and a[1] < b[3] + gap and a[3] + gap > b[1]


def wrap_text(draw, text, face, width, break_long_words=False):
    """Prefer word boundaries; long words may widen a gutter rather than become unreadable fragments."""
    lines = []
    for paragraph in text.split("\n"):
        line = ""
        for word in paragraph.split():
            proposed = (line + " " + word).strip()
            if draw.textbbox((0, 0), proposed, font=face)[2] <= width:
                line = proposed
                continue
            if line:
                lines.append(line)
                line = ""
            if not break_long_words:
                line = word
                continue
            for char in word:
                if line and draw.textbbox((0, 0), line + char, font=face)[2] > width:
                    lines.append(line)
                    line = ""
                line += char
        lines.append(line)
    return "\n".join(lines)


def prepare_items(labels, draw, path, canvas_size, image_bounds, mode, margin, gap):
    raw = ([labels["title"]] if labels.get("title") else []) + labels.get("labels", [])
    if not raw:
        raise ValueError("No title or labels")
    result, seen = [], set()
    for i, item in enumerate(raw):
        title = i == 0 and bool(labels.get("title"))
        identifier = item.get("id", "title" if title else str(i))
        if not isinstance(identifier, str) or not identifier or identifier in seen:
            raise ValueError("Duplicate or invalid label ID")
        seen.add(identifier)
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Labels need nonempty text")
        size = item.get("font_size", 30)
        if type(size) is not int or not 8 <= size <= 200:
            raise ValueError("Invalid font_size")
        face = ImageFont.truetype(path, size)
        desired = point(item["position"], canvas_size)
        max_width = canvas_size[0] - 2 * margin if title else min(420, max(80, round(canvas_size[0] * .30)))
        # Use the existing gutter when the caller has explicitly provided one.
        if not title and desired[0] < image_bounds[0]:
            gutter = image_bounds[0] - 2 * margin - gap
            if gutter >= 80:
                max_width = min(max_width, gutter)
        elif not title and desired[0] >= image_bounds[2]:
            gutter = canvas_size[0] - image_bounds[2] - 2 * margin - gap
            if gutter >= 80:
                max_width = min(max_width, gutter)
        max_width = item.get("max_width", max_width)
        if type(max_width) is not int or max_width < 8:
            raise ValueError("max_width must be a positive pixel width (at least 8)")
        break_words = item.get("break_long_words", False)
        if type(break_words) is not bool:
            raise ValueError("break_long_words must be a boolean")
        rendered = wrap_text(draw, text, face, max_width, break_words) if mode == "auto" else text
        bbox = draw.multiline_textbbox((0, 0), rendered, font=face, spacing=6)
        target = None
        if "target" in item and "target_image" in item:
            raise ValueError("Choose target (canvas) or target_image (source), not both")
        if "target_image" in item:
            local = point(item["target_image"], (image_bounds[2]-image_bounds[0], image_bounds[3]-image_bounds[1]))
            target = (image_bounds[0]+local[0], image_bounds[1]+local[1])
        elif "target" in item:
            target = point(item["target"], canvas_size)
        # Validate supplied routing hints even though auto mode recomputes the route.
        for key in ("line_start", "elbow"):
            if key in item:
                point(item[key], canvas_size)
        result.append({"id": identifier, "item": item, "title": title, "text": rendered, "face": face,
                       "bbox": bbox, "width": bbox[2]-bbox[0], "height": bbox[3]-bbox[1],
                       "desired": (desired[0]+bbox[0], desired[1]+bbox[1]), "target": target})
    return result


def place_items(items, canvas_size, image_bounds, margin, gap, avoid_image):
    """Nearest non-overlapping placements; return None when a larger gutter is needed."""
    width, height = canvas_size
    placed = []
    targets = [r["target"] for r in items if r["target"] is not None]
    for entry in items:
        w, h = entry["width"], entry["height"]
        if w > width - 2*margin or h > height - 2*margin:
            return None
        desired_x, desired_y = entry["desired"]
        x = min(max(margin, desired_x), width-margin-w)
        y = min(max(margin, desired_y), height-margin-h)
        xs = {x, margin, width-margin-w}
        if entry["title"]:
            xs.add((width-w)//2)
        xs.update((image_bounds[0]-gap-w, image_bounds[2]+gap))
        ys = {y, margin, height-margin-h, image_bounds[1]-gap-h, image_bounds[3]+gap}
        for other in placed:
            xs.update((other["box"][0]-gap-w, other["box"][2]+gap))
            ys.update((other["box"][1]-gap-h, other["box"][3]+gap))
        # Dense vertical alternatives are cheap for the small number of product callouts.
        ys.update(range(margin, max(margin+1, height-margin-h+1), max(8, gap)))
        desired_box = (desired_x, desired_y, desired_x+w, desired_y+h)
        repair = (not (margin <= desired_x <= width-margin-w and margin <= desired_y <= height-margin-h)
                  or any(intersects(desired_box, other["box"], gap) for other in placed)
                  or (avoid_image and intersects(desired_box, image_bounds, gap)))
        if entry["target"] is not None:
            ys.add(min(max(margin, entry["target"][1]-h//2), height-margin-h))
        choices = []
        for px in sorted(xs):
            if not margin <= px <= width-margin-w:
                continue
            for py in sorted(ys):
                if not margin <= py <= height-margin-h:
                    continue
                box = (px, py, px+w, py+h)
                if repair and entry["target"] is not None:
                    # Damaged hints use the nearest side column, not a cluster above/below the device.
                    left_side = entry["target"][0] < (image_bounds[0]+image_bounds[2])/2
                    if (left_side and box[2]+gap > image_bounds[0]) or (not left_side and box[0]-gap < image_bounds[2]):
                        continue
                if any(intersects(box, other["box"], gap) for other in placed):
                    continue
                if avoid_image and intersects(box, image_bounds, gap):
                    continue
                if any(box[0]-gap <= target[0] <= box[2]+gap and box[1]-gap <= target[1] <= box[3]+gap for target in targets):
                    continue
                distance = (px-desired_x)**2 + (py-desired_y)**2
                if repair and entry["target"] is not None:
                    tx, ty = entry["target"]
                    near_x, near_y = min(max(tx, box[0]), box[2]), min(max(ty, box[1]), box[3])
                    distance = .15*distance + .85*((tx-near_x)**2 + (ty-near_y)**2)
                choices.append((distance, py, px, box))
        if not choices:
            return None
        box = min(choices)[3]
        placed.append({**entry, "box": box, "origin": (box[0]-entry["bbox"][0], box[1]-entry["bbox"][1])})
    return placed


def expand_canvas(canvas, items, image_bounds, margin, gap):
    """Add white gutters, translating targets with the unchanged image instead of shrinking text."""
    body = [r for r in items if not r["title"]]
    gutter = max(240, max(r["width"] for r in body) + 2*margin + gap) if body else margin
    titles = [r for r in items if r["title"]]
    header = sum(r["height"]+gap for r in titles) + 2*margin
    width = max(canvas.width+2*gutter, max((r["width"]+2*margin for r in titles), default=0))
    left, right = [], []
    for entry in items:
        if not entry["title"]:
            side = left if (entry["target"][0] if entry["target"] is not None else entry["desired"][0]) < (image_bounds[0]+image_bounds[2])/2 else right
            side.append(entry)
    height = max(canvas.height+header+2*margin,
                 header+sum(r["height"]+gap for r in left)+margin,
                 header+sum(r["height"]+gap for r in right)+margin)
    if width > 8192 or height > 8192:
        raise ValueError("Callouts need a canvas larger than 8192px; reduce content or choose a larger initial layout")
    dx, dy = (width-canvas.width)//2, header
    expanded = Image.new("RGB", (width, height), "white")
    expanded.paste(canvas, (dx, dy))
    for entry in items:
        if entry["target"] is not None:
            entry["target"] = (entry["target"][0]+dx, entry["target"][1]+dy)
        if entry["title"]:
            entry["desired"] = (margin, margin)
        else:
            side_x = margin if entry in left else dx+canvas.width+gap
            desired_y = entry["target"][1]-entry["height"]//2 if entry["target"] is not None else entry["desired"][1]+dy
            entry["desired"] = (side_x, desired_y)
    return expanded, [image_bounds[0]+dx, image_bounds[1]+dy, image_bounds[2]+dx, image_bounds[3]+dy], [dx, dy]


def segment_hits_box(a, b, box):
    """Liang–Barsky segment/rectangle intersection, including boundary contact."""
    low, high = 0., 1.
    dx, dy = b[0]-a[0], b[1]-a[1]
    for p, q in ((-dx, a[0]-box[0]), (dx, box[2]-a[0]), (-dy, a[1]-box[1]), (dy, box[3]-a[1])):
        if p == 0:
            if q < 0:
                return False
        else:
            ratio = q/p
            if p < 0:
                low = max(low, ratio)
            else:
                high = min(high, ratio)
            if low > high:
                return False
    return True


def segments_cross(a, b, c, d):
    def side(p, q, r):
        return (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
    # Proper crossings; shared endpoints are not counted as crossings.
    return side(a, b, c)*side(a, b, d) < 0 and side(c, d, a)*side(c, d, b) < 0


def route_callout(entry, placed, earlier, gap):
    box, target = entry["box"], entry["target"]
    x, y = (box[0]+box[2])//2, (box[1]+box[3])//2
    starts = [(box[0]-4, y), (box[2]+4, y), (x, box[1]-4), (x, box[3]+4)]
    options = []
    for start in starts:
        candidates = [[start, target], [start, (target[0], start[1]), target], [start, (start[0], target[1]), target]]
        # Side corridors help route around adjacent labels instead of drawing through text.
        for px in (box[0]-gap, box[2]+gap):
            candidates.append([start, (px, start[1]), (px, target[1]), target])
        for route in candidates:
            route = [p for i, p in enumerate(route) if not i or p != route[i-1]]
            hits = sum(any(segment_hits_box(a, b, other["box"]) for a, b in zip(route, route[1:]))
                       for other in placed)
            crosses = sum(segments_cross(a, b, c, d) for a, b in zip(route, route[1:])
                          for old in earlier for c, d in zip(old, old[1:]))
            length = sum(math.dist(a, b) for a, b in zip(route, route[1:]))
            options.append(((hits, crosses, length, len(route)), route))
    return min(options, key=lambda item: item[0])[1]


def compose(image, labels_path, output, font=None, mode=None):
    labels = json.loads(Path(labels_path).read_text(encoding="utf-8"))
    mode = mode or labels.get("layout_mode", "auto")
    if mode not in {"auto", "strict"}:
        raise ValueError("layout_mode must be auto or strict")
    output = Path(output)
    if output.resolve() == Path(image).resolve():
        raise ValueError("Output must not replace the base image")
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
        size, box = config.get("size"), config.get("image_box")
        if not isinstance(size, list) or len(size) != 2 or any(type(v) is not int or not 32 <= v <= 8192 for v in size):
            raise ValueError("Invalid canvas size")
        if not isinstance(box, list) or len(box) != 4 or any(type(v) is not int for v in box):
            raise ValueError("Invalid image_box")
        if not (0 <= box[0] < box[2] <= size[0] and 0 <= box[1] < box[3] <= size[1]):
            raise ValueError("image_box outside canvas")
        canvas = Image.new("RGB", size, "white")
        fitted = ImageOps.contain(base, (box[2]-box[0], box[3]-box[1]))
        offset = (box[0]+(box[2]-box[0]-fitted.width)//2, box[1]+(box[3]-box[1]-fitted.height)//2)
        canvas.paste(fitted, offset)
        image_bounds = [offset[0], offset[1], offset[0]+fitted.width, offset[1]+fitted.height]
    else:
        canvas = base
    path = font_path(font or labels.get("font"))
    draw = ImageDraw.Draw(canvas)
    margin, gap = labels.get("margin", 16), labels.get("label_gap", 12)
    if any(type(v) is not int or v < 0 for v in (margin, gap)):
        raise ValueError("margin and label_gap must be nonnegative integers")
    items = prepare_items(labels, draw, path, canvas.size, image_bounds, mode, margin, gap)
    adjustments, translation = [], [0, 0]
    if mode == "strict":
        placed = []
        for entry in items:
            x, y = entry["desired"]
            box = (x, y, x+entry["width"], y+entry["height"])
            # Pillow text bboxes use exclusive right/bottom coordinates.
            if box[0] < 0 or box[1] < 0 or box[2] > canvas.width or box[3] > canvas.height:
                raise ValueError(f"Text outside canvas: {entry['id']}")
            if any(intersects(box, other["box"]) for other in placed):
                raise ValueError(f"Text overlap: {entry['id']}")
            placed.append({**entry, "box": box, "origin": (x-entry["bbox"][0], y-entry["bbox"][1])})
    else:
        # Without a part mask the whole source rectangle is protected; prefer white gutters.
        placed = place_items(items, canvas.size, image_bounds, margin, gap, True)
        if placed is None:
            canvas, image_bounds, translation = expand_canvas(canvas, items, image_bounds, margin, gap)
            placed = place_items(items, canvas.size, image_bounds, margin, gap, True)
            if placed is None:
                raise ValueError("Cannot fit all callouts without overlap; use fewer words or a different layout")
            adjustments.append("Added white gutters; preserved image scale and translated targets with the image")
        for entry in placed:
            if entry["text"] != entry["item"]["text"]:
                adjustments.append(f"Wrapped text: {entry['id']}")
            if entry["box"][:2] != entry["desired"]:
                adjustments.append(f"Moved text: {entry['id']}")
    routes, warnings = {}, []
    for entry in placed:
        if entry["target"] is None:
            continue
        if mode == "strict":
            item = entry["item"]
            route = [point(item.get("line_start", item["position"]), canvas.size)]
            if "elbow" in item:
                route.append(point(item["elbow"], canvas.size))
            route.append(entry["target"])
        else:
            route = route_callout(entry, placed, list(routes.values()), gap)
        routes[entry["id"]] = route
    # Validate against ALL text, including boxes placed after a leader was planned.
    for identifier, route in routes.items():
        for entry in placed:
            if any(segment_hits_box(a, b, entry["box"]) for a, b in zip(route, route[1:])):
                warnings.append(f"Leader {identifier} intersects text {entry['id']}")
        for other_id, other in routes.items():
            if identifier < other_id and any(segments_cross(a, b, c, d) for a, b in zip(route, route[1:]) for c, d in zip(other, other[1:])):
                warnings.append(f"Leaders cross: {identifier} / {other_id}")
    draw = ImageDraw.Draw(canvas)
    color = labels.get("color", "#073C76")
    for route in routes.values():
        draw.line(route, fill=color, width=3)
        target = route[-1]
        draw.ellipse((target[0]-6, target[1]-6, target[0]+6, target[1]+6), fill=color, outline="white", width=2)
    for entry in placed:
        draw.multiline_text(entry["origin"], entry["text"], font=entry["face"], fill=color, spacing=6)
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output, format="PNG")
    result = {"image": str(output.resolve()), "font": path, "layout_mode": mode,
              "canvas_size": list(canvas.size), "canvas_translation": translation, "adjustments": adjustments,
              "label_boxes": {r["id"]: list(r["box"]) for r in placed},
              "rendered_text": {r["id"]: r["text"] for r in placed},
              "label_origins": {r["id"]: list(r["origin"]) for r in placed},
              "leader_paths": {key: [list(p) for p in route] for key, route in routes.items()},
              "warnings": warnings, "source_size": source_size, "image_bounds": image_bounds,
              "target_points": {r["id"]: list(r["target"]) for r in placed if r["target"] is not None},
              "semantic_targets_checked": False}
    output.with_suffix(".layout.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("image", "labels", "output"):
        parser.add_argument("--" + name, required=True)
    parser.add_argument("--font")
    parser.add_argument("--mode", choices=("auto", "strict"))
    args = parser.parse_args()
    try:
        print(json.dumps(compose(args.image, args.labels, args.output, args.font, args.mode), ensure_ascii=False))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
