# Follow-up edits

Read the saved run, chosen parent, inputs, and report. Save the user's wording. Decide if it changes labels/exterior or technical structure. If the request conflicts with an applicable document, explain the concrete conflict and clarify rather than silently inventing a different product.

For only labels under composed mode: copy the labels JSON to a versioned sibling, change text/coordinates, render a new preview, inspect it and re-review its parent using `--preview`. This creates a new review/preview while preserving old ones; no image-generator call is needed. Save the revision request separately before finalizing again.

For a technical image edit within a non-exhausted run: reserve with `--kind edit --parent N`, use the chosen base image, record, review and finalize again. The old best stays in attempts and review history. Never overwrite image.png of an existing attempt.

After the initial budget is exhausted, obtain a new explicit generation budget for a revision. A new run can be initialized with the prior chosen PNG, copied/revalidated current sources, and a saved `revision-of.json` linking the earlier run and request; its limit is the authorized revision budget (maximum 10 per run). The helper does not silently replenish an old run. If inputs change, use `prepare --update`, which preserves old inputs and invalidates prior ratings until re-reviewed.

If a tool is unavailable, store the exact failure and available outputs. No automatic paid API fallback. During authorized development, record the bug, patch the appropriate project code, run affected tests, and continue where possible. Unresolved issues belong in the v0.1 development log with their practical effect.
