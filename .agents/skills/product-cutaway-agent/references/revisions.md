# Follow-up edits

Read the saved run, chosen parent, inputs, and report. Save the user's wording. Decide if it changes labels/exterior or technical structure. If the request conflicts with an applicable document, explain the concrete conflict and clarify rather than silently inventing a different product.

For only labels under composed mode: copy the labels JSON to a versioned sibling, change text/coordinates, render a new preview, inspect every changed name/target and the entire layout, and re-review its parent using `--preview --labels --label-review` with newly bound hashes. This creates a new review/preview while preserving old ones; no image-generator call is needed. Save the revision request and archive the prior final before finalizing again. Never reuse an old caption audit for a changed preview.

In new thresholded runs, retain the eligible current base_score for caption-only edits. A new generated base needs its own raw review and80+ before composition; do not borrow the parent's rating. Historical caption edits keep their recorded caption mode. Show each newly captioned80+ draft promptly to allow user corrections during the run.

For a technical image edit within a non-exhausted run: reserve with `--kind edit --parent N`, use the chosen base image, record, review and finalize again. The old best stays in attempts and review history. Never overwrite image.png of an existing attempt.

To continue after final delivery or exhaustion, use the user's explicit request to start a linked revision with at most5 calls. Initialize it with the prior chosen PNG, revalidate sources and protocol v2 checks, and save revision-of.json linking the earlier run and request. A plain request to continue uses the default5 unless a smaller budget was specified. The helper does not silently replenish an old run; preserve the old counter and all outputs. If inputs change within a run, use prepare --update, which preserves old inputs and invalidates prior ratings until re-reviewed. Historical10-call budgets remain historical, not the default for new revisions.

If a tool is unavailable, store the exact failure and available outputs. No automatic paid API fallback. During authorized development, record the bug, patch the appropriate project code, run affected tests, and continue where possible. Unresolved issues belong in the v0.1 development log with their practical effect.
