# Prompts

## Create

Use case: scientific-educational. Asset: educational product cutaway PNG.
Input roles: product photo = exterior identity/pose; manufacturer drawings = applicable topology; analogy = only the declared internal relationships; style example = formatting only.

Read [construction-plan.md](construction-plan.md). A style example is optional. Compile the saved plan into the following product-specific prompt structure; fill each applicable field from inspected evidence or the declared reconstruction, omit genuinely inapplicable fields, and never submit placeholders:

```text
PRODUCT AND INPUTS: exact model/revision; role of each attached image.
EXTERIOR: preserve these observed features and store-photo pose/proportions: …
ASSEMBLY: [node A] is [position/orientation], inside/surrounding [node B],
attached to [mating feature]; [documented count/profile]. Repeat for main nodes.
CONNECTIONS: [port/node A] connects to [node B] via [physical opening/channel];
[seal/wall] separates [chamber A] from [chamber B]. Include drive relationships
where applicable. Use concrete renderable spatial descriptions.
CUT PLAN: remove these surfaces; expose these distinguishing shapes and
connections; retain these covers/supports. Do not float or disconnect parts.
SELECTED RECONSTRUCTION: render this chosen shape/arrangement for the specified
gap; retain target-specific count/ports/mechanism. Do not import other analog parts.
FORBIDDEN: conflicting variant parts, unsupported extra mechanism, liquid,
flow arrows, painted cut bands, decoration, generated text/callouts.
PRESENTATION: white background, natural section materials, legible functional
nodes, composition leaving compact space for separately composed labels.
```

Attach the useful technical views themselves when possible. A link or “follow factory documentation” is not a replacement for visible references and explicit assembly constraints. Preserve the actual submitted prompt, not only a generic prompt template.

Name exact model. Preserve silhouette, ports, controller, proportions, perspective and plausible materials. Open the housing selectively to reveal the required functional nodes. Insert only confirmed constraints and explicitly chosen reconstruction, never a generic detailed mechanism without a basis. Specify working path and exact stage count when documented. No extra turbine, unrelated chamber, unnecessary exploded components, or invented electronics.

White background, clean textbook/museum lighting, readable cut surfaces. For composed labels: no generated text/callouts; reserve margins for title and Russian labels. Request a single image. Tool dimensions/quality are controlled only through parameters it actually supports.

Mandatory dry-master constraint: empty air-filled passages and neutral cut surfaces; no depicted water or other liquid, blue volume fill, bubbles, droplets, spray, or flow arrows. Do not fill unknown passages to disguise geometry. Explain connections by visible physical walls/openings; a flow overlay is optional and separate from generation.

Cut-face constraint: continue the actual substrate across the section. No red/colored bands, contour strokes, painted section faces or decorative repeating texture. Use neutral metallic faces for metal and appropriate polymer/elastomer faces for confirmed nonmetal parts. Exterior paint may remain on the exterior; do not invent substrate material from paint color.

An optional approved reference is a separate input role: visual target, with recorded technical-review status. Compare and correct individual nodes; do not copy its water, outlines, stage count, valve position or hidden mechanism when contradicted by current constraints/sources. Choose windows and disclosed reconstruction for the actual mechanism. Avoid both unsupported elaborate detail and smooth placeholders that conceal the defining mechanism; retain the reconstruction gap and do not call hidden connections verified.

## Review

Given the actual candidate, applicable source excerpts/figures and fixed checklist, inspect every check. Write observed facts, region, status, and the source relationship. Distinguish invisible from contradicted. Ignore expected score, earlier praise and desired improvement. Include errors introduced outside the edited region.

## Revise

State parent image and precise defect, cite the applicable fact, specify required replacement and preserve the already correct nodes/exterior/pose/background. One related problem per pass is preferred; regenerate from the product photo if the structure or cut plane is globally wrong. Save the exact submitted prompt and references before calling the tool.

If the same defect survives an edit, narrow the target region, change the cut visibility or replace the faulty shape/relationship explicitly rather than repeating vague requests. Inspect all other nodes after each such edit. Pilot-specific successful wording is not a universal geometry rule.
