# Universal construction-to-image workflow

Read before preparing a new product's spec, checklist and initial prompt. The agent owns research, reference selection, spatial planning and corrections. A user-supplied style image is optional; never require one to make an ordinary product run work. AQUARIO is a historical test fixture, not a universal component list, pose or cut plane.

## Identify and classify

Resolve URL, article, name or image to the exact store card. For an image, use visible model markings, silhouette, ports and dimensions to search the store; do not claim exact identity from similarity alone. Distinguish consequential variants. Select the construction family from applicable evidence: rotating machinery, valve/regulator, filter/media assembly, heat exchanger/heater, vessel, fitting/pipe, or another supported mechanism. Family knowledge supplies search terms and candidate relationships, never evidence of this article's parts.

Choose a representation that explains this mechanism: longitudinal/transverse section, selective windows, layered media view or restrained assembly separation. Do not force every product into the pump's large cut windows. A simple fitting may only need its bore, wall, thread and seal; more invented components do not make it more complete.

## Extract a construction, not a collection of URLs

Inspect the exact manufacturer's section/service parts/internal CAD and manual. Complement omitted relationships with applicable series documents, official disassembly/assembly animations or videos, then declared analogs. Search for a concrete missing fact rather than endlessly collecting general manuals. Do not require every source format when one applicable section already answers the construction questions.

For each evidence asset record the exact revision and what is visible. In an operable 3D model inspect selected parts, reverse views, mating faces and sections when available. Exterior-only CAD cannot establish internals. For videos record publisher, exact product identification, timestamp and actually inspected frames; titles/transcripts cannot establish geometry. Third-party teardown can contribute an explicitly qualified observation; it does not become manufacturer-model proof. If the available tools cannot inspect a video/format, record that limit and use another source, without claiming playback or silently installing an external workflow.

Save `input/construction-plan.md` before generation, with source IDs already in sources.json. It must contain:

1. **Identity and representation:** exact article/revision, construction family, store-photo pose, selected cut plane/windows and why they reveal the main mechanism.
2. **Nodes:** functional name, type/count, visible shape/profile, material if supported, approximate position/orientation, contained/surrounding components, attachment and role. Separate confirmed existence from reconstructed geometry. Use relative positions when dimensions are absent; never invent precise measurements.
3. **Relations:** concrete pairs and relationships, such as attached-to, inside, surrounds, along-axis, separated-by, connected-by-passage. Include the mechanical/transmission path and physical fluid/gas passages where applicable, plus boundaries/seals that keep chambers separated. No universal requirement for a motor, liquid path or membrane.
4. **Evidence ledger:** each consequential node/relation fact → source ID/page/view/timestamp → model/series/reconstruction/unknown → what the source actually shows. Preserve contradictions and resolve revision applicability before choosing a fact. A style reference is never geometry evidence.
5. **Visibility plan:** which relationships and distinguishing geometries must be visible in the final cut; which covers remain; how to reveal important nodes without disconnecting them. A hidden critical relationship stays unverified rather than passing because the part has a label.
6. **Reconstruction decisions:** exact missing fact, compatible analog and why its mechanism applies, limited geometry being borrowed and target-specific properties that must remain unchanged. Do not transfer an analog wholesale. If no source supports an exact shape, use the most defensible educational reconstruction and disclose it in the adjacent report. Unknown does not authorize arbitrary detail or omission of the whole functional mechanism.
7. **Exterior lock:** store-photo silhouette, ports, caps, controls, cables and supports to preserve, except surfaces intentionally removed by the documented cut.
8. **Observable checks:** distinguishable part geometry/count, actual mating and passage connections, separation/sealing, exterior and cut clarity. State what visible evidence would pass or fail each important check before seeing a generated image.

Reuse compatible verified series facts across products only after checking model/revision applicability. Cache useful assets and record the current match. A cached source or family template is not blanket proof for all products of a brand.

## Compile the generator prompt

Use [prompts.md](prompts.md). Translate the plan into explicit spatial assembly constraints, not just part names or “follow the manual.” Send only useful inspected image references with clear roles: exact product exterior, exact technical views, declared analogous mechanism, optional style. Do not expect the image generator to browse URLs, read unavailable CAD/PDF files or infer the complete construction from a photo.

Write the actual prompt in the generation attempt archive. It must state required nodes/counts, positions/orientations, nesting and mating, physical connections, cut visibility, protected exterior and prohibited additions. Describe chosen reconstructed geometry concretely for rendering; keep its uncertainty in the saved plan/report rather than asking the renderer to decide what is true. Do not mix contradictory source views or incompatible camera directions without explaining them.

## Check and repair

Inspect the candidate against the evidence ledger and relation map, not against its prompt's assertions. For each substantial defect save: observed region/shape → applicable source view → violated relation/fact → explicit replacement → features to preserve. Check the whole image after a local edit. A caption never repairs geometry.

Separate three findings: documented match, documented contradiction, and unverified/reconstructed appearance. Scores remain a legacy checklist diagnostic, not a statement of physical accuracy. Apply [review.md](review.md); do not call a high-scoring render technically verified. A self-review by the same agent remains correlated with its generation decisions.

When the initial cut hides a defining mechanism, revise the plane/window or expose a better supported geometry instead of awarding completeness for smooth shapes. When more generation cannot resolve an evidence gap, stop spending calls to chase a number; return the best complete educational reconstruction with specific gaps in the report.
