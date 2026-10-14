---
name: product-cutaway-agent
description: Turn a plumbing product URL, name, article or image into an educational cutaway PNG by identifying its store card, researching its construction, planning visible assembly relations, and checking saved versions against applicable evidence.
---

# Product cutaway agent — v1.2

Own the process from product identification to a recognizable cutaway of its main functional nodes and connections. Deliver one best PNG on white with Russian labels, saved variants and a source-backed report. A pilot product is a test, not a mechanism template. Execute in the active Codex task; this is not an unattended background service.

The generated master is DRY: no liquid, blue-filled channels, bubbles, droplets or flow arrows. Cut faces retain the actual material, without red/colored bands or decorative outlines. Caption leaders are separate from flow arrows. Preserve the dry master if a flow overlay is requested; see [layers.md](references/layers.md).

## Identify and research

1. Find and open the exact 477477.ru card from the user's URL, SKU, name or image. Copy its full visible title and actual gallery photo, verify the modification, and show title, source link and saved photo in chat. This checkpoint does not require approval. If the card/photo is unavailable or the product is absent, an exact official manufacturer photo is already allowed: record the fallback reason and its real origin. Do not invent a store SKU or call an attachment a store download. Ask about consequential identity ambiguity; see [store-card.md](references/store-card.md).
2. Inspect applicable manufacturer sections, service/parts diagrams, internal CAD/3D views and manuals. Consult [manufacturer-sources.md](references/manufacturer-sources.md); coverage is model-specific. Videos/disassembly or analogs may fill gaps with qualified provenance. Exterior BIM and a parts list do not establish hidden geometry. Read [evidence.md](references/evidence.md).
3. Read [construction-plan.md](references/construction-plan.md). Build an evidence-linked map of nodes, nesting, mating, barriers and passages. Compile explicit spatial constraints for this mechanism, not a generic “plausible cutaway” prompt. Cover each essential node's applicable type/count, shape, attachment, placement/connections and material. Keep unsupported facts unknown; documented analog reconstruction is allowed but never becomes proof of exact model geometry.
4. Use `scripts/cutaway.py` with Python/Pillow; read [execution.md](references/execution.md). Register intake, freeze plan/spec/checklist/sources, then archive relevant views or explicit archival gaps. `prepare --bundle` avoids custom builder code. Freeze checks before generation; changed facts need a versioned update and re-review. Sources can be reused with [source-cache.md](references/source-cache.md) after checking applicability.

## Generate, inspect and correct

Use the built-in imagegen tool by default, after reading its available skill and inspecting local references. Browser ChatGPT Images remains an explicitly selected experimental route only; see [chatgpt-images.md](references/chatgpt-images.md). No automatic paid API fallback. Helpers save state and calculate observations; they do not invoke models.

1. Use [prompts.md](references/prompts.md). Before every generation/edit, `reserve` its actual prompt/references, then `dispatch` immediately before the tool call. New v1.2 rounds allow **5 received images + 2 technical retries, at most 7 calls**. A bad received image counts. Repeated pre-send failures are also bounded. Historical runs retain their saved policy.
2. `record` each returned PNG immediately. A confirmed failure uses `fail`; an uncertain response uses `fail --unknown`. Resolve/recover it before a new call; never blindly retry. Keep outputs in the run, not only temporary tool storage.
3. Inspect the whole image and each functional node against saved source views, not prior scores or generator claims. Read [review.md](references/review.md). Record visible distinguishing features, actual conflicts and unknowns; `review` computes the technical rating from these observations. The helper cannot recognize image semantics or validate the truth of a pass. Ratings may fall. No score is a probability of correctness.
4. Technical rating uses construction, topology and functional completeness only. Appearance and captions are separate. Correct substantial source-supported defects by editing the best suitable parent, preserving correct parts and checking the whole new frame. After the second received image, continue only with a concrete substantial correction; do not consume all five for a rising score or minor cosmetics.
5. Choose the strongest candidate by critical contradictions, readiness, then technical rating. **Compose captions only for the chosen 90+ technical result**, using `compose_png.py` without another image-generation call. Verify every term/endpoint and full layout, then `review --preview --labels --label-review`. Caption composition cannot change non-caption assessments or technical rating. A technical reassessment is a new base review with `reassessment_reason`, preserving history. Losers need no captions. Review the captioned image for accidental visual regressions too; discard/recompose if the base changed.
6. Stop at the saved budget or earlier if no defensible substantial edit remains. If below 90, return the best unlabelled draft with concrete gaps; never fabricate success or restart a budget automatically. `finalize` exports the chosen PNG and reports. A 90+ candidate with unresolved construction gaps is still not expert-approved.

## Communication, follow-up and limits

During work: `Генерируется 3/5. Предыдущая: техника 82/100. Исправляю: …`. Keep prompts/observations in files. Use `status --compact` and relevant pages rather than dumping history or rereading all manuals. Show the chosen captioned PNG, technical rating, readiness, main confirmed facts/gaps, a small variants table and report links. Disclose analogs in the adjacent report, not on the image.

Independent review is **not enabled**. `review-packet` exports candidate + frozen facts + source assets without scores/prompts/attempt history; it launches no agent. [reviewer.md](references/reviewer.md) describes the proposed cheaper reviewer, pending user selection. Self-review remains labelled self-review; do not describe a repeated pass as independent validation.

For revisions read [revisions.md](references/revisions.md). The `continue` helper preserves the original identity photo, selected base, evidence and prior history in a visibly linked new round only after a user request. Historical runs need explicit v1.2 intake/plan, not silent migration. During authorized skill development, fix demonstrated code/process failures and record unresolved errors. Routine product work does not authorize changing the installed skill or publishing to the store.

Cleanup is a project idea only: delete no product data automatically. Future cleanup must show scope and ask a separate explicit confirmation while preserving the agreed final PNG. Ask contextual questions when a consequential choice is unresolved; do not repeatedly ask about already authorized defaults.
