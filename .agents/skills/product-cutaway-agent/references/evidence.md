# Evidence and reconstruction

Use the product page/photo for identification and exterior. Prefer a manufacturer manual, sectional drawing, exploded view, service catalogue or internal CAD for construction. Record URL, edition, PDF page index AND printed page/figure, and why the document applies to this exact model. Inspect relevant rendered pages: extracted text can miss diagram associations.

Sources JSON uses `manufacturer_model`, `manufacturer_series`, `analog`, `product_photo`, or `style_reference`. `verified: true` means the agent actually inspected the source and checked applicability; it does not constitute independent expert validation. A reseller cannot be upgraded to manufacturer evidence; appearance approval cannot prove construction.

Before reconstructing from analogs, inspect the exact manufacturer's service/parts catalogue and interactive 3D viewer. Text search can miss iframe content (AQUARIO pilot: the exact model was present in the 3D catalogue despite an incomplete initial search). Record lookup route, article/revision and inspected parts. If an observed embedded viewer cannot be operated in its frame, open its actual observed URL directly; do not guess endpoints. Screenshots can be image references when no export exists; save their source/role and never claim an unavailable screenshot file was cached.

Separate source capabilities: internal section, exploded assembly, exterior CAD/BIM, dimension drawing and text-only manual. Exterior BIM gives placement/ports/dimensions, not proof of hidden rotor, valve or diaphragm geometry. An exploded assembly proves named components and arrangement only to the extent visible; it need not reveal internal passages. If a catalogue groups suppliers, identify the actual product brand (e.g. Gidrox/Aquastrong under Гидроконтракт), not just the supplier label.

The spec lists functional nodes, roles/connections, `evidence` (`model`, `series`, `analog`, `unknown`) and source IDs. Separate evidence for existence/type/count from evidence for precise internal geometry. A documented permanent-magnet motor does not prove magnet count or bearing dimensions.

If original documents omit geometry, find an analogous mechanism in another manufacturer's documentation. Record exactly what transfers (e.g. impeller/diffuser relationship or diaphragm separation) and what does not (number of stages, ports, materials, dimensions). Do not copy a different pump's self-priming chamber into a non-self-priming product. Put assumptions and still unknown details in `gaps` / `analog_assertions`. The final report discloses them, while the PNG remains a clean teaching illustration.

For an inaccessible store page, the user's supplied product photograph is an acceptable fallback with explicit provenance in the report. Do not claim it was downloaded from the store. If source revisions disagree, preserve the conflict and use the applicable manufacturer edition; a technically consequential unresolved variant ambiguity requires clarification.

Create product-specific checks before seeing candidates. Use atomic observable facts; main nodes and working principle matter more than every screw. Never reuse the pilot pump's fixed node list for a valve or a pipe.

## Preserve the evidence actually inspected

After preparing inputs and before relying on a source, use `archive-evidence` to save the relevant rendered PDF page, original document, photograph or actual exported viewer screenshot. Each record links a source ID, immutable input version, exact page/figure or selected model/view, and the observation it supports. Keep local files and manifests hashed. Prefer relevant pages to repeatedly loading full documents; preserve the document URL/edition too.

For each relied-on source, archive the inspected views/pages, not just one arbitrary file. Rotated views should describe camera side and mating faces. If export or local capture is unavailable, record `--gap` with the concrete limitation and describe the inspected view. Do not invent a screenshot path or bypass browser restrictions to obtain a file. A context-only view remains incomplete archival evidence. A source archive does not automatically award any score.

After `prepare --update`, re-inspect applicability and register the supporting archives for the new input version; previous records stay historical. Final reports show absent registrations and explicit gaps. Default output directories are outside Git; archive assets may include complete third-party documents and should not be blindly published with project code.
