# Execution and data contract

Helpers require Python 3.10+ and Pillow; file locking currently targets macOS/Linux (`fcntl`). Use an available runtime, or install the project's requirements in a virtual environment. No API key is needed for the built-in generator. `$SCRIPT` below means the actual absolute path to `scripts/cutaway.py`; `$RUN` means the actual returned run directory, not a shell variable to assume already exists.

For a new product first complete [store-card.md](store-card.md). Pass the actual saved store photo or authorized exact manufacturer fallback photo to init, with its true source URL. Init accepts actual PNG/JPEG/WebP bytes, copies them unchanged to input/reference with the correct format suffix and returns input_image as an absolute path. State stores its path/hash/format/size; this does not automatically prove web origin. Register the observed origin JSON with intake before prepare; this is validated provenance metadata, not automated web verification. Results/previews still require PNG.

```text
python cutaway.py init --root output/cutaways --product-id brand-article --model MODEL --url URL --image PHOTO --limit 5
python cutaway.py intake --run RUN --record ORIGIN.json
python cutaway.py prepare --run RUN --spec SPEC.json --checklist CHECKLIST.json --sources SOURCES.json --plan PLAN.md
python cutaway.py archive-evidence --run RUN --source-id manual --locator "PDF page 5, printed page 3, figure 2" --observation "Observed inlet and outlet positions" --file PAGE.png
python cutaway.py reserve --run RUN --prompt-file PROMPT.md --ref PHOTO [--ref DIAGRAM] [--kind edit --parent 1]
python cutaway.py dispatch --run RUN --attempt 1
# Agent now invokes the selected image backend with exactly those references and prompt.
python cutaway.py record --run RUN --attempt 1 --image RETURNED.png [--metadata SMALL-METADATA.json]
python compose_png.py --image BASE.png --labels LABELS.json --output PREVIEW.png [--font FONT.ttf]
python cutaway.py review --run RUN --attempt 1 --review-file REVIEW.json [--preview PREVIEW.png --labels LABELS.json --label-review LABEL-REVIEW.json]
python cutaway.py status --run RUN --compact
python cutaway.py finalize --run RUN --reason REASON
```

New v1.2 runs default to5 received images and retry_limit2. A bad returned image counts. At most7 reservations/calls are possible; two confirmed failures permit two extra calls to reach five images. A third failure ends retry eligibility. Pre-dispatch failures also consume the bounded recovery allowance, conservatively limiting repeated preparation failures. `--limit` accepts1–5 and `--retry-limit`0–2. Historical v1.0 states preserve their saved budget; `--workflow-version 1.0` exists for regression/legacy reconstruction only, not bypassing current product requirements.

`reserve` persists prompt/references before a call. `dispatch` checks integrity and marks the send boundary immediately before the tool; it invokes nothing and cannot prove a remote send occurred. It cannot be dispatched twice. `record` attaches the returned real PNG. After a confirmed sent failure use `fail --reason`; an explicitly unsent pre-dispatch failure uses `fail --not-sent`. An ambiguous result uses `fail --unknown`, blocking new reservations and finalization. Recover with `record` on the same attempt, or `resolve --reason` only after establishing the original operation failed/no output exists. Record that evidence honestly. Both real failures and retries may consume platform limits. Do not mark an uncertain response as a free failure.

Origin JSON fields: source_kind (store/manufacturer), title_verbatim, model, sku (null when unavailable), source_url, image_url, retrieved_at, and fallback_reason for manufacturer photos. The helper binds the original photo hash and requires a matching product_photo source URL. Before reserve it requires a nonempty frozen plan and an archive entry or explicit gap for every source used by checks/nodes and every product photo. A gap records missing local evidence, not proof that a source was inspected.

Alternatively, `prepare --run RUN --bundle INPUTS.json` accepts one JSON with spec, checklist, sources and construction_plan (Markdown text) and performs the same validations. Do not combine bundle and individual paths. This replaces per-product builder scripts, not the research step.

These helpers remain backend-neutral. For an explicitly selected ordinary ChatGPT Images request, use [chatgpt-images.md](chatgpt-images.md): reserve before each browser send, save the actual prompt/files/conversation, and record the downloaded real PNG before reviewing it. Browser failures use the same saved counter; the scripts do not sign in, send messages or download images themselves.

If a necessary live viewer screenshot exists only in the conversation, use the generator's conversation-reference mechanism for the smallest sufficient set of images. Before the call, save a context-reference manifest beside the prompt (image order/role, source URL, selected model/article, inspected view, and that the screenshot is not cached). Reserve all local inputs normally. The helper does not cache conversation-only screenshots; never claim a fully reproducible image-reference archive when a source view is missing. Save small execution metadata with `record` as well. Do not mix local-path and conversation-count parameters in one generation call.

State writes are atomic and locked. Copies/prompts are saved before the corresponding state transition; a crash may leave an orphan directory, which blocks the next reservation instead of overwriting evidence. Inspect it and whether a tool call occurred before repairing the state. The automatic tests exercise the count, locks, recovery and ranking, not a guarantee against every power-loss ordering.

## JSON shapes

Block enums are exactly `construction`, `topology`, `completeness`, `appearance`, `clarity`. Exterior similarity is `appearance` in JSON, not `exterior`. Scores include `assessment_method.image_semantics_checked_by_helper: false`: calculation validates submitted observations and arithmetic, not whether the depicted mechanism is correct. A deliberately false pass review can produce a high score for a defective image. Keep such isolated evaluator probes outside registered production reviews and preserve their failure finding.

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

New v1.2 init saves caption_threshold90. The technical rating is the earned construction/topology/completeness total normalized by the fixed85-point denominator; appearance is separate. Captions never increase technical points. Empty/unknown technical checks still count against the denominator. Technical checks cannot be caption-dependent; clarity defaults caption-dependent unless explicitly false (e.g. dry constraints). Raw-base reviews keep absent caption checks unknown. review returns caption_eligible, technical rating, appearance rating and caption_status.

Compose only the selected technical90+ result. Pass preview/labels/label-review together; every non-caption status must equal the current base assessment. If inspection changes a technical conclusion, submit a new base review with reassessment_reason, preserving the prior review. This clears the active preview/audit until captioned again. `finalize` requires the selected eligible candidate's caption audit, not audits for losing candidates. It can deliver a below90 unlabelled draft with its shortfall disclosed. Unknown/failing captions cannot be finalized as checked.

New saved review JSON and score objects are hashed and checked before reuse/finalization. Changed observations need a new immutable review, not an edit in place. This detects accidental inconsistency; it is not cryptographic authentication against somebody rewriting state and all hashes. Existing v1.0 states remain on the original total/80+ gate and all-eligible caption rule, unchanged by the new default.

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

Use `status --compact` for normal resume/progress. It preserves attempt accounting, pending/uncertain calls, current input paths/hash, leader, ratings and readiness while omitting full observations and history. Read the relevant immutable review/spec files only when needed. The historical `status` without the flag still returns the full saved state; do not routinely load that large output into context.

`prepare --update` creates a new immutable input version, preserves previous inputs and score history, and removes active ratings. Re-review every available image under the new checklist before finalizing. Never edit frozen inputs in place.

`finalize` refuses pending generations and unreviewed images, sorts v1.2 candidates by critical fails, readiness, then technical rating, copies the leader to final/best.png, writes report.md/ranking.json and a comparison sheet. It does not assert expert approval, require exactly 10 attempts, or automatically generate new images. Previous reviews/previews persist when the same candidate is reassessed.

Keep runtime results outside Git by default. For an explicitly authorized pilot archive, publish selected/all attempts, reviews, prompts, labels and reports intentionally; avoid blindly committing downloaded complete manuals or raw HTML. Preserve source URLs so another run can fetch them. Current development failures go in `docs/development-v1.2.md`; older logs remain historical.

### Evidence archive

`archive-evidence --run RUN --source-id ID --locator VIEW --observation FACT --file ASSET` copies original bytes into `evidence/files/` and writes a hashed manifest under `evidence/`. Use `--gap REASON` instead of `--file` if no local asset is available. Exactly one is required. Unknown source IDs are rejected. Records bind to the current frozen input version, preserve original URLs/applicability, and consume no generation attempt. `reserve`, `review` and `finalize` check that registered manifests/assets have not changed. Final reports link local assets and disclose missing archive records. The helper imports files; it does not download pages, operate a viewer or make screenshots.

## Approved visual references

Use `kind: style_reference` for an image approved for appearance. Record whether technical review occurred. It may guide visual/completeness checks, but cannot prove a model/series node or earn construction evidence; v1.2 construction uses manufacturer facts or explicitly marked analog reconstruction, never the style reference itself. `reserve` accepts actual PNG/JPEG/WebP references, validates their bytes and caches them unchanged under the matching format extension. Generated results and composed previews still require PNG. An external prior-run edit seed is recorded as the first candidate in the new run, with its actual edit intent/roles in execution metadata and a `revision-of.json`; it is not an in-run parent attempt.


## Reuse and optional separate review

`continue --run RUN --root OUTPUT --request TEXT [--attempt N]` creates a linked v1.2 round using original provenance, frozen facts/evidence and the chosen base seed. It requires explicit user continuation and does not migrate legacy runs automatically. See [revisions.md](revisions.md). `source_cache.py` offers a URL/model/revision/locator cache; see [source-cache.md](source-cache.md).

`review-packet --run RUN --attempt N --output OUTPUT` copies the actual candidate and applicable source assets into an opaque directory, with a whitelisted score-free facts.json. The parent state retains its binding and file hashes. It launches no reviewer. Separate-agent/model selection is pending; see [reviewer.md](reviewer.md). Default reviews identify themselves as self_review. Optional assessor metadata is an author claim, not verification that another model actually inspected anything.
