# Execution and data contract

Helpers require Python 3.10+ and Pillow; file locking currently targets macOS/Linux (`fcntl`). Use an available runtime, or install the project's requirements in a virtual environment. No API key is needed for the built-in generator. `$SCRIPT` below means the actual absolute path to `scripts/cutaway.py`; `$RUN` means the actual returned run directory, not a shell variable to assume already exists.

For a new product first complete [store-card.md](store-card.md). Pass the actual saved card photo to init and the card URL to --url. Init accepts actual PNG/JPEG/WebP bytes, copies them unchanged to input/reference with the correct format suffix and returns input_image as an absolute path. State stores its path/hash/format/size; this does not automatically prove web origin. Save input/store-card.json with the observed title/asset/card provenance before showing the photo and proceeding. Results/previews still require PNG.

```text
python cutaway.py init --root output/cutaways --product-id brand-article --model MODEL --url URL --image PHOTO --limit 5
python cutaway.py prepare --run RUN --spec SPEC.json --checklist CHECKLIST.json --sources SOURCES.json
python cutaway.py archive-evidence --run RUN --source-id manual --locator "PDF page 5, printed page 3, figure 2" --observation "Observed inlet and outlet positions" --file PAGE.png
python cutaway.py reserve --run RUN --prompt-file PROMPT.md --ref PHOTO [--ref DIAGRAM] [--kind edit --parent 1]
# Agent now invokes the built-in image generator with exactly those references and prompt.
python cutaway.py record --run RUN --attempt 1 --image RETURNED.png [--metadata SMALL-METADATA.json]
python compose_png.py --image BASE.png --labels LABELS.json --output PREVIEW.png [--font FONT.ttf]
python cutaway.py review --run RUN --attempt 1 --review-file REVIEW.json [--preview PREVIEW.png --labels LABELS.json --label-review LABEL-REVIEW.json]
python cutaway.py status --run RUN
python cutaway.py finalize --run RUN --reason REASON
```

New runs default to5 and accept an explicit limit1–5; the sixth call is refused. Existing historical states retain their saved limit, including earlier authorized10-call pilots. `reserve` persists the prompt, image references and attempt before a tool call. It refuses an unfinished reserved attempt and exceeding that saved limit. The agent must obey this protocol: the helper cannot intercept unrelated direct tool calls. Reserve copies image references into a SHA256-named cache, avoiding dependence on temporary paths. Failed calls remain in the count. After an actual failure use `fail --run RUN --attempt N --reason TEXT`; for an uncertain response add `--unknown`. Later `record` can attach a recovered result to an unknown attempt without spending a new call. Never blindly re-dispatch it.

If a necessary live viewer screenshot exists only in the conversation, use the generator's conversation-reference mechanism for the smallest sufficient set of images. Before the call, save a context-reference manifest beside the prompt (image order/role, source URL, selected model/article, inspected view, and that the screenshot is not cached). Reserve all local inputs normally. The helper does not cache conversation-only screenshots; never claim a fully reproducible image-reference archive when a source view is missing. Save small execution metadata with `record` as well. Do not mix local-path and conversation-count parameters in one generation call.

State writes are atomic and locked. Copies/prompts are saved before the corresponding state transition; a crash may leave an orphan directory, which blocks the next reservation instead of overwriting evidence. Inspect it and whether a tool call occurred before repairing the state. The automatic tests exercise the count, locks, recovery and ranking, not a guarantee against every power-loss ordering.

## JSON shapes

Sources:
```json
{"sources":[{"id":"manual","kind":"manufacturer_model","url":"https://manufacturer/manual.pdf","title":"Manual","verified":true,"applicability":"Exact model and edition inspected"}]}
```

Spec:
```json
{"model":"MODEL","nodes":[{"id":"motor","name":"Motor","evidence":"model","source_ids":["manual"],"essential":true,"role":"Drive shaft","excluded_aspects":{}}],"connections":[],"gaps":[],"analog_assertions":[]}
```

Checklist (allocate the complete weight of each nonempty block across its checks; this example shows only the shape, not a complete scored checklist):
```json
{"protocol_version":2,"version":"product-v2","checks":[{"id":"motor-type","node_id":"motor","aspect":"type_count","block":"construction","points":9,"requirement":"Documented motor type","source_ids":["manual"],"locator":"PDF page 6, printed page 4","source_fact":"Manual explicitly specifies a synchronous permanent-magnet motor","evidence_level":"model","evidence_supported":true,"essential":true,"critical":true}]}
```

Review:
```json
{"checklist_version":"product-v2","checks":[{"id":"motor-type","status":"unknown","observation":"Rotor type cannot be distinguished in this cut","region":"right motor housing","source_observation":"The manual specifies permanent magnets, but the image does not reveal that feature"}],"summary":"Motor type is unverified","next_changes":["Expose rotor"],"resolved_changes":[]}
```

Optional `partial_rule` belongs to the checklist check and must describe a real partial condition. Every review must contain all check IDs exactly once. `review` returns rating, current leader and critical errors; full observations stay in the file. Integer/fractional point arithmetic is deterministic using Decimal.

New runs require protocol v2, with every essential node's applicable aspects covered (see [review.md](review.md)); the JSON above illustrates one fact, not a complete checklist. Aspect enums are `type_count`, `shape`, `attachment`, `placement_connections`, `material`, `delivery`. Delivery checks need no node_id. Level enums are `model`, `series`, `analog`, `photo`, `style`, `unknown`. The supported level must match a cited source kind. `evidence_supported` and `essential` are required booleans, and source_fact/locator must be nonempty. A node's optional excluded_aspects maps an inapplicable aspect to its reason. Source omissions stay in checks as unsupported facts. Review JSON adds source_observation per check. Outputs from review/finalize/ranking contain readiness and evidence_summary; source-supported ceiling/unavailable points refer to checklist points only. Technical approval always remains false.

New init also saves caption_threshold:80. First use review without preview for the raw base: caption-dependent checks must be unknown, giving0. Checks optionally set caption_dependent:boolean (default true in clarity, false elsewhere); set false explicitly for visible dry/material checks and true for any label-dependent fact outside clarity. A base review returns evaluation_phase:base, base_rating and caption_due. At80+, compose and inspect captions without generator calls, then pass preview/labels/label-review together. The preview requires a current same-checklist base_score at least80; added caption points cannot satisfy that gate. Captioned reviews retain base_rating. Immediately show the draft in chat.

Input updates invalidate base_score eligibility. A new raw-base assessment clears selection of prior previews while preserving files/reviews. Finalization requires registered caption audits for all current eligible bases; it can finish with an unlabelled base below80 and must disclose the missing threshold. Reports/ranking distinguish base/captioned scores. Existing historical states without caption_threshold preserve their prior caption mode and are not migrated automatically.

Historical runs without scoring_protocol_version can use their original v1 inputs. An explicit prepare --update can upgrade them to v2 and invalidate ratings; a v2 run cannot downgrade back to v1. Normal initialization and following edits do not migrate historical pilot data.

Labels use normalized coordinates relative to the base PNG, with manually verified semantic targets:
```json
{"color":"#073C76","title":{"text":"MODEL","position":[0.04,0.03],"font_size":48},"labels":[{"id":"motor","text":"Двигатель","position":[0.75,0.75],"line_start":[0.74,0.75],"elbow":[0.71,0.70],"target":[0.65,0.60],"font_size":30}]}
```

The composition helper rejects clipped/overlapping text and invalid coordinates, saves a layout report, and refuses replacing the base. It does not detect every line crossing, text over product, missing Cyrillic glyph in an arbitrary supplied font, or a wrong semantic target: inspect the PNG.

### Caption verification protocol

For new composed captions, visually inspect the finished preview and record every label ID exactly once in a separate JSON:
```json
{"base_sha256":"SHA256-OF-BASE","labels_sha256":"SHA256-OF-LABELS","preview_sha256":"SHA256-OF-PREVIEW","layout_checked":true,"title_checked":true,"checks":[{"id":"motor","source_ids":["manual"],"locator":"PDF page 6, printed page 4","text_checked":true,"target_checked":true,"observation":"Name matches the manual; endpoint is on the exposed motor housing, not its cable"}]}
```

Compute hashes from the actual files; true flags are the inspecting agent's claims and must only be recorded after visual checks. Source IDs must be applicable sources, not style references. Unsupported or hidden features should have their callout removed/reworded rather than falsely marking an endpoint checked. The title flag covers model/article and title layout; layout flag covers readability, clipping, text/line conflicts. A leader endpoint check is required for each label with a target. The script cannot recognize parts, and this protocol is not independent expert approval.

Pass preview, labels and protocol together. `review` validates coverage, source IDs and hashes and saves immutable copies beside the preview. `finalize` checks the copies and exports the selected labels and protocol. A new preview clears the old caption audit; updated inputs invalidate it too. Historical previews can still be reviewed without these flags, but reports explicitly say no structured caption audit was registered.

For labels outside the product, optionally set `canvas: {"size":[2000,1800],"image_box":[300,270,1650,1620]}`. The source is fitted with its aspect ratio preserved. Prefer `target_image: [x,y]` relative to the source PNG for leader endpoints; `position`, `line_start` and `elbow` remain relative to the output canvas. This automatically accounts for white bands around non-square images. Use either target_image or target, not both. The layout report records actual image_bounds and target_points. Changing a cut plane still requires identifying new semantic targets; geometry conversion is not object recognition.

## Changing evidence / finishing

`prepare --update` creates a new immutable input version, preserves previous inputs and score history, and removes active ratings. Re-review every available image under the new checklist before finalizing. Never edit frozen inputs in place.

`finalize` refuses pending generations and unreviewed images, sorts candidates without critical fails first, copies the leader to final/best.png, writes report.md/ranking.json and a comparison sheet. It does not assert expert approval, require exactly 10 attempts, or automatically generate new images. Previous reviews/previews persist when the same candidate is reassessed.

Keep runtime results outside Git by default. For an explicitly authorized pilot archive, publish selected/all attempts, reviews, prompts, labels and reports intentionally; avoid blindly committing downloaded complete manuals or raw HTML. Preserve source URLs so another run can fetch them. Development failures go in `docs/development-v0.1.md`.

### Evidence archive

`archive-evidence --run RUN --source-id ID --locator VIEW --observation FACT --file ASSET` copies original bytes into `evidence/files/` and writes a hashed manifest under `evidence/`. Use `--gap REASON` instead of `--file` if no local asset is available. Exactly one is required. Unknown source IDs are rejected. Records bind to the current frozen input version, preserve original URLs/applicability, and consume no generation attempt. `reserve`, `review` and `finalize` check that registered manifests/assets have not changed. Final reports link local assets and disclose missing archive records. The helper imports files; it does not download pages, operate a viewer or make screenshots.

## Approved visual references

Use `kind: style_reference` for an image approved for appearance. Record whether technical review occurred. It may guide visual/completeness checks, but cannot prove a model/series node or earn construction evidence; construction still requires manufacturer sources. `reserve` accepts actual PNG/JPEG/WebP references, validates their bytes and caches them unchanged under the matching format extension. Generated results and composed previews still require PNG. An external prior-run edit seed is recorded as the first candidate in the new run, with its actual edit intent/roles in execution metadata and a `revision-of.json`; it is not an in-run parent attempt.
