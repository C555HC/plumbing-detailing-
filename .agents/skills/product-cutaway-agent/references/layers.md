# Dry master and optional flow overlay

The generated base is a dry cutaway: physical components, empty passages, neutral materials and readable cut faces. No liquid, blue-filled channels, bubbles, droplets or flow arrows. This is a generation constraint and a critical review check, not an automatic image-recognition feature of the helper.

Keep three resources separate: base PNG; caption/layout JSON composed into an ordinary flattened final PNG; and, only when requested, an optional flow overlay. Save a separate dry final even if a flow illustration is later requested. Caption leaders identify parts; they are not flow arrows.

For v1.2, review bases first and compose captions only for the chosen technical90+ result. Losing candidates need no captions. Composition uses no image-generator call and cannot increase the technical rating. Export one flattened final PNG; retain the unlabelled base and caption coordinates for later edits. If the technical score stays below90, return the best raw draft and its actual gaps. Historical80+ pilots keep their original policy.

For a flow overlay, first verify the physical path and save route/arrow coordinates, source IDs and remaining uncertainty. Compose arrows or water tint in a separately named output without changing the dry master. Use deterministic drawing for the overlay when useful; never ask image generation to invent it or imply that arrows prove continuity. Overlay editing must not secretly consume/reset generation budget.

The current skill provides base and caption composition. A dedicated flow-overlay CLI is not implemented; the agent may create an explicitly requested separate overlay using ordinary drawing tools and inspect it. Do not advertise a nonexistent helper command.


## Automatic caption layout

Use compose_png.py in its default auto mode for captions. It wraps text by words, tries the requested canvas without collisions, and adds white gutters when necessary. Font sizes are preserved and words are not truncated. The source-image rectangle stays clear of text; it is not a semantic product mask. Existing target/target_image coordinates identify the same source point after letterboxing and any added canvas translation. Auto mode recalculates line starts/routes; strict mode preserves manual routing.

Read the generated `.layout.json` for actual boxes, wrapped text, target points, routes and warnings. Inspect the PNG: automatic routing reduces intersections but does not guarantee none in complex layouts. Correct/recompose warnings before claiming layout_checked:true. This is deterministic caption drawing, without a new imagegen call or a higher technical score. Changing source geometry still needs a new base review.
