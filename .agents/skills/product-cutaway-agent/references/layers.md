# Dry master and optional flow overlay

The generated base is a dry cutaway: physical components, empty passages, neutral materials and readable cut faces. No liquid, blue-filled channels, bubbles, droplets or flow arrows. This is a generation constraint and a critical review check, not an automatic image-recognition feature of the helper.

Keep three resources separate: base PNG; caption/layout JSON composed into an ordinary flattened final PNG; and, only when requested, an optional flow overlay. Save a separate dry final even if a flow illustration is later requested. Caption leaders identify parts; they are not flow arrows.

For new runs, create the unlabelled base first and review it. At base80+ compose captions, inspect sources/targets and show that draft in chat immediately; further corrections can continue within the remaining five-call budget. Caption composition consumes no image-generation call. Preserve separate base and captioned scores and never award hypothetical caption points. At final delivery one main PNG is selected, with all alternatives retained. If the source-supported base stays below80, report the shortfall and preserve the best raw result instead of inventing a higher score.

For a flow overlay, first verify the physical path and save route/arrow coordinates, source IDs and remaining uncertainty. Compose arrows or water tint in a separately named output without changing the dry master. Use deterministic drawing for the overlay when useful; never ask image generation to invent it or imply that arrows prove continuity. Overlay editing must not secretly consume/reset generation budget.

Current v0.1 provides base and caption composition. A dedicated flow-overlay CLI is not implemented; the agent may create an explicitly requested separate overlay using ordinary drawing tools and inspect it. Do not advertise a nonexistent helper command.
