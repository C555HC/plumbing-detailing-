# Visual review and scoring

Weights: construction 45, topology 25, completeness 15, exterior 10, clarity 5. Allocate each block's points among applicable checks before generation. Empty blocks stay unrated/zero, without shifting evidence points to attractive appearance. All candidates use the same checklist version and content.

Every check contains ID, requirement, maximum points, source IDs, source/figure locator, critical flag and optional partial_rule. Construction checks require applicable manufacturer evidence; analogs can support reconstruction checks in topology/completeness, never documentary proof of this model.

Review the full frame and then important nodes at readable scale. State what is visibly present and where; compare to the source. A caption does not establish the actual part. Do not use the previous rating or the generator's assurance as evidence. `pass`=1; `partial`=.5 only with a predefined noncritical partial_rule; `fail`=0; `unknown`=0 with a reason. Count/type/critical position checks are binary. The script sums points; it does not recognize the mechanism.

Review JSON must cover every ID exactly once. Include concise `summary`, `next_changes`, and `resolved_changes` when appropriate. Do not report an improvement unless visible. Score the same form of deliverable for all candidates: with captions generated in-image, or with a composed, inspected caption preview. If captions are absent, clarity points cannot be awarded for hypothetical future labels.

Critical fail means an observed contradiction against an applicable fact (wrong mechanism, stage count, motor type, important valve position, impossible flow). Critical unknown means not verified; keep it separate. Select candidates with zero critical fails before numeric score. If none qualify, return the best available but explicitly state defects. Even a candidate without critical fails can remain incompletely verified.

Before finalization, review two leaders without earlier ratings when available. Same-model repeated passes are not independent expert reviews. If facts change, update inputs explicitly and re-review every existing candidate; stale ratings are invalidated. Don't average unexplained disagreements or force scores to increase.
