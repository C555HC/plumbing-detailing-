---
name: product-cutaway-agent
description: Create and revise educational cutaway PNGs of real plumbing products using the store photograph, manufacturer documentation, explicit reconstruction gaps, scored visual checks, and saved versions.
---

# Product cutaway agent

Produce a recognizable product cutaway showing its main functional nodes and how they connect. Use a white background and Russian labels unless the user specifies otherwise. Deliver the best PNG, all variants, and a source-backed report. Execute in an active Codex task; this skill is not a background service.

Generate a DRY device only: no water/liquid, blue-filled passages, droplets, bubbles, or flow arrows baked into the base image. Label leaders are allowed in the separate caption composition. A requested flow explanation is a separate editable overlay/output, after physical passages are verified; preserve the dry master. Read [layers.md](references/layers.md).

Cut faces retain the part's material: metal at a metal section, polymer at a polymer section, elastomer at a membrane. No red/colored contour bands, painted cut faces, neon rims or decorative surface patterns unless specifically requested. Preserve readable edges through lighting and real wall thickness.

## Start or resume

- Identify the exact model from the URL/article and photo. Ask only when a consequential ambiguity blocks identification. Read [evidence.md](references/evidence.md) to gather applicable manufacturer sources and reconstruction gaps. Consult the matching entry in [manufacturer-sources.md](references/manufacturer-sources.md) and check the manufacturer's service/parts/3D viewer before analogs. Record which source types were inspected or unavailable. Do not assume brand-wide coverage or internal detail in a BIM model.
- Use the built-in image generation/editing tool; inspect local reference images before passing them. Do not switch to an external paid API without authorization. Python helpers save state and calculate scores; they do not invoke this tool.
- Use `scripts/cutaway.py` through a Python with Pillow. For commands and JSON formats, read [execution.md](references/execution.md). Create a unique run and freeze spec, sources, and checklist before the first call. For resume, read existing state and current inputs rather than reconstructing from chat.
- Archive inspected source pages/views with `archive-evidence` after preparing inputs; record an explicit gap when no local asset can be saved. Read [evidence.md](references/evidence.md). Do not confuse a URL with a preserved view or claim that legacy uncached views were recovered.

## Iteration

1. Create one initial variant from the source photo and technical constraints. Use [prompts.md](references/prompts.md). Before EVERY generation/editor call reserve one attempt with its actual prompt and references. Initial limit is 10, including failed calls; never reset it to continue a stalled run.
2. Save the returned PNG immediately with `record`. A lost/uncertain response uses `fail --unknown`; seek an existing result before issuing another distinct call. Keep all outputs. Copy tool output into the run; never leave the only copy in the tool's default folder.
3. Inspect the new complete image and each functional node at readable scale against the frozen checks. Read [review.md](references/review.md). Compare an approved reference by node when supplied, recording its provenance and technical approval status. Save concrete observations, not a guessed overall score; `review` computes the score. Missing/hidden details are unknown. Reconstruction from analogs never proves this model's geometry.
4. In composed-label mode, keep base PNG and labels JSON, render a preview with `compose_png.py`, and inspect every name and endpoint against its source. Register it with `review --preview --labels --label-review`; see [execution.md](references/execution.md). The final PNG is flattened; editable intermediate sources remain separate. The helper validates coverage and file hashes, not the truth of visual observations. Preview-only review remains for legacy/other modes and cannot inherit a caption audit.
5. Write the next corrective prompt from actual defects and sources; preserve correct parts. Edit the current candidate or a previous leader. A new candidate is allowed when the cut plane fails. Re-check the whole new image after edits. Ratings can decrease.
6. Stop at the limit or earlier when no substantial defensible correction remains. Re-review the top two when available without past ratings. Use `finalize` to select the best candidate without critical contradictions first, then by score. If every candidate has critical errors, label the output best available and list them.

## Brief communication and revisions

During generation say: `Генерируется 3/10. Картинка 2: 70/100. Исправляю: …` using actual numbers. Keep detailed observations and prompts in files. Cache sources/spec and load relevant pages rather than entire PDFs or all prior images each time. Whole-image regression inspection remains necessary.

At completion show the best PNG inline, its rating, a compact table of other versions, and links to all variants/report. Disclose analogs and missing evidence in the adjacent report, not on the image. A score is a comparative rating, never a probability of correctness. Human technical approval is a separate status.

For follow-up edits preserve the chosen version and read [revisions.md](references/revisions.md). During explicitly authorized skill development, fix code/process failures, run relevant regression tests, and log unresolved failures; a routine product run does not authorize rewriting the installed skill. Never publish to a store as part of this skill.
