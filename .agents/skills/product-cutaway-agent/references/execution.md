# Execution and data contract

Helpers require Python 3.10+ and Pillow; file locking currently targets macOS/Linux (`fcntl`). Use an available runtime, or install the project's requirements in a virtual environment. No API key is needed for the built-in generator. `$SCRIPT` below means the actual absolute path to `scripts/cutaway.py`; `$RUN` means the actual returned run directory, not a shell variable to assume already exists.

```text
python cutaway.py init --root output/cutaways --product-id brand-article --model MODEL --url URL --image PHOTO --limit 10
python cutaway.py prepare --run RUN --spec SPEC.json --checklist CHECKLIST.json --sources SOURCES.json
python cutaway.py reserve --run RUN --prompt-file PROMPT.md --ref PHOTO [--ref DIAGRAM] [--kind edit --parent 1]
# Agent now invokes the built-in image generator with exactly those references and prompt.
python cutaway.py record --run RUN --attempt 1 --image RETURNED.png [--metadata SMALL-METADATA.json]
python compose_png.py --image BASE.png --labels LABELS.json --output PREVIEW.png [--font FONT.ttf]
python cutaway.py review --run RUN --attempt 1 --review-file REVIEW.json [--preview PREVIEW.png]
python cutaway.py status --run RUN
python cutaway.py finalize --run RUN --reason REASON
```

`reserve` persists the prompt, image references and attempt before a tool call. It refuses an unfinished reserved attempt and the 11th attempt. The agent must obey this protocol: the helper cannot intercept unrelated direct tool calls. Reserve copies image references into a SHA256-named cache, avoiding dependence on temporary paths. Failed calls remain in the count. After an actual failure use `fail --run RUN --attempt N --reason TEXT`; for an uncertain response add `--unknown`. Later `record` can attach a recovered result to an unknown attempt without spending a new call. Never blindly re-dispatch it.

If a necessary live viewer screenshot exists only in the conversation, use the generator's conversation-reference mechanism for the smallest sufficient set of images. Before the call, save a context-reference manifest beside the prompt (image order/role, source URL, selected model/article, inspected view, and that the screenshot is not cached). Reserve all local inputs normally. The helper does not cache conversation-only screenshots; never claim a fully reproducible image-reference archive when a source view is missing. Save small execution metadata with `record` as well. Do not mix local-path and conversation-count parameters in one generation call.

State writes are atomic and locked. Copies/prompts are saved before the corresponding state transition; a crash may leave an orphan directory, which blocks the next reservation instead of overwriting evidence. Inspect it and whether a tool call occurred before repairing the state. The automatic tests exercise the count, locks, recovery and ranking, not a guarantee against every power-loss ordering.

## JSON shapes

Sources:
```json
{"sources":[{"id":"manual","kind":"manufacturer_model","url":"https://manufacturer/manual.pdf","title":"Manual","verified":true,"applicability":"Exact model and edition inspected"}]}
```

Spec:
```json
{"model":"MODEL","nodes":[{"id":"motor","name":"Motor","evidence":"model","source_ids":["manual"],"role":"Drive shaft"}],"connections":[],"gaps":[],"analog_assertions":[]}
```

Checklist (allocate the complete weight of each nonempty block across its checks; this example shows only the shape, not a complete scored checklist):
```json
{"version":"product-v1","checks":[{"id":"motor-type","block":"construction","points":9,"requirement":"Documented motor type","source_ids":["manual"],"locator":"PDF page 6, printed page 4","critical":true}]}
```

Review:
```json
{"checklist_version":"product-v1","checks":[{"id":"motor-type","status":"unknown","observation":"Rotor type cannot be distinguished in this cut","region":"right motor housing"}],"summary":"Motor type is unverified","next_changes":["Expose rotor"],"resolved_changes":[]}
```

Optional `partial_rule` belongs to the checklist check and must describe a real partial condition. Every review must contain all check IDs exactly once. `review` returns rating, current leader and critical errors; full observations stay in the file. Integer/fractional point arithmetic is deterministic using Decimal.

Labels use normalized coordinates relative to the base PNG, with manually verified semantic targets:
```json
{"color":"#073C76","title":{"text":"MODEL","position":[0.04,0.03],"font_size":48},"labels":[{"id":"motor","text":"Двигатель","position":[0.75,0.75],"line_start":[0.74,0.75],"elbow":[0.71,0.70],"target":[0.65,0.60],"font_size":30}]}
```

The composition helper rejects clipped/overlapping text and invalid coordinates, saves a layout report, and refuses replacing the base. It does not detect every line crossing, text over product, missing Cyrillic glyph in an arbitrary supplied font, or a wrong semantic target: inspect the PNG.

For labels outside the product, optionally set `canvas: {"size":[2000,1800],"image_box":[300,270,1650,1620]}`. The source is fitted with its aspect ratio preserved. Prefer `target_image: [x,y]` relative to the source PNG for leader endpoints; `position`, `line_start` and `elbow` remain relative to the output canvas. This automatically accounts for white bands around non-square images. Use either target_image or target, not both. The layout report records actual image_bounds and target_points. Changing a cut plane still requires identifying new semantic targets; geometry conversion is not object recognition.

## Changing evidence / finishing

`prepare --update` creates a new immutable input version, preserves previous inputs and score history, and removes active ratings. Re-review every available image under the new checklist before finalizing. Never edit frozen inputs in place.

`finalize` refuses pending generations and unreviewed images, sorts candidates without critical fails first, copies the leader to final/best.png, writes report.md/ranking.json and a comparison sheet. It does not assert expert approval, require exactly 10 attempts, or automatically generate new images. Previous reviews/previews persist when the same candidate is reassessed.

Keep runtime results outside Git by default. For an explicitly authorized pilot archive, publish selected/all attempts, reviews, prompts, labels and reports intentionally; avoid blindly committing downloaded complete manuals or raw HTML. Preserve source URLs so another run can fetch them. Development failures go in `docs/development-v0.1.md`.

## Approved visual references

Use `kind: style_reference` for an image approved for appearance. Record whether technical review occurred. It may guide visual/completeness checks, but cannot prove a model/series node or earn construction evidence; construction still requires manufacturer sources. `reserve` accepts actual PNG/JPEG/WebP references, validates their bytes and caches them unchanged under the matching format extension. Generated results and composed previews still require PNG. An external prior-run edit seed is recorded as the first candidate in the new run, with its actual edit intent/roles in execution metadata and a `revision-of.json`; it is not an in-run parent attempt.
