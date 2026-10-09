# Evidence and reconstruction

Use the product page/photo for identification and exterior. Prefer a manufacturer manual, sectional drawing, exploded view, service catalogue or internal CAD for construction. Record URL, edition, PDF page index AND printed page/figure, and why the document applies to this exact model. Inspect relevant rendered pages: extracted text can miss diagram associations.

Sources JSON uses `manufacturer_model`, `manufacturer_series`, `analog`, or `product_photo`. `verified: true` means the agent actually inspected the source and checked applicability; it does not constitute independent expert validation. A reseller cannot be upgraded to manufacturer evidence.

The spec lists functional nodes, roles/connections, `evidence` (`model`, `series`, `analog`, `unknown`) and source IDs. Separate evidence for existence/type/count from evidence for precise internal geometry. A documented permanent-magnet motor does not prove magnet count or bearing dimensions.

If original documents omit geometry, find an analogous mechanism in another manufacturer's documentation. Record exactly what transfers (e.g. impeller/diffuser relationship or diaphragm separation) and what does not (number of stages, ports, materials, dimensions). Do not copy a different pump's self-priming chamber into a non-self-priming product. Put assumptions and still unknown details in `gaps` / `analog_assertions`. The final report discloses them, while the PNG remains a clean teaching illustration.

For an inaccessible store page, the user's supplied product photograph is an acceptable fallback with explicit provenance in the report. Do not claim it was downloaded from the store. If source revisions disagree, preserve the conflict and use the applicable manufacturer edition; a technically consequential unresolved variant ambiguity requires clarification.

Create product-specific checks before seeing candidates. Use atomic observable facts; main nodes and working principle matter more than every screw. Never reuse the pilot pump's fixed node list for a valve or a pipe.
