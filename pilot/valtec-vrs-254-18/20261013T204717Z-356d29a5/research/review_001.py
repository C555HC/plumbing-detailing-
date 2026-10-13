from pathlib import Path
import json
r=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vrs-254-18/20261013T204717Z-356d29a5")
c=json.loads((r/"input/checklist-draft.json").read_text())
observations={
"housing":["Single left volute castiron body with upper/lower opposing connections.","Deep curved dark hydraulic cavity and threaded vertical necks.","Body joins motor through vertical mating flange, no floating gap.","Lower cavity shown continuous peripheral around wheel; central-eye connection not established.","Grey rough cut substrate and exterior red paint."],
"impeller":["One pale shallow polymer centrifugal wheel at left.","Precise curved-blade profile cannot be compared to manufacturer; omitted there.","White shaft enters central wheel hub through plate.","Wheel behind perforatedplate at left hydraulicend, but lower inlet connection to central eye obscured.","Pale nonmetal wheel contrasting metalplate, consistent PP-GF appearance only."],
"rotor":["One central smooth cylindrical rotor, not permanentmagnet cup.","Grey cylinder extends axially between ceramic collars.","Rotor coaxial to white shaft, same drive axis as wheel.","Cylinder inside thin enclosing can; stator outside can.","Exact rotor alloy unconfirmed."],
"stator":["Upper/lower winding/core portions of one annular fixed stator.","Section of surrounding ring, winding end turns and long lamination stack.","Fixed core rests within outermotorcasing, not floating onshaft.","Coils outside thin metalcan; no intrusion into rotor cavity.","Copper-looking winding and grey stack, materials not specified in relied-on source."],
"barrier":["One thin metal separator surrounding rotor.","U-shaped axial cut outline round rotor, coherent cylindrical sleeve.","Sleeve wall closes outer compartment boundary; small end opening represented.","Thin sleeve between rotor and stator clearly visible above/below.","Neutral polished thin metalwall; specific stainless grade not distinguishable, fits general appearance."],
"shaft":["Pale shaft, front/rear pale collars and small black elastic ring visible.","Straight shaft and annular collars at both ends; bore hidden.","Front blackcuff backed with palethrust element against plate; rear collar mates to shaft.","Common horizontal axis, but longitudinal shaft channel not exposed.","Offwhite supports/shaft, blackelastic cuff consistent ceramic/EPDM visual roles."]
}
fail={"controls":"fail","cooling-path":"fail","shaft-placement_connections":"unknown","impeller-placement_connections":"unknown"}
delivery={
"nodes-visible":"Housing/wheel/rotor/stator/can/shaft/collars clearly separated in readable full window.",
"cooling-path":"Plate apertures are visible, but solid-looking shaft has no visible hollow returnbore.",
"no-extra":"No tank/fan/multistage stack, one wetrotor assembly.",
"silhouette":"Red compact inline body/opposed necks/vent screw preserved, although view shifted to profile.",
"controls":"Terminalbox migrated to far right ofmotor rather than frontleft store position; cable shortened offcrop.",
"dry":"Empty cavities; no water. Blue terminal wire is electrical insulation, not liquid.",
"natural":"Neutralmetal/polymer/ceramic sectionfaces without coloredcontourstrip; exteriorredpaint allowed.",
"captions":"Unlabelledbase, captioncheck unknown."
}
checks=[]
for x in c["checks"]:
 nid=x.get("node_id");i=["type_count","shape","attachment","placement_connections","material"].index(x["aspect"]) if nid else None
 o=observations[nid][i] if nid else delivery[x["id"]]
 status="unknown" if not x["evidence_supported"] or x.get("caption_dependent") else fail.get(x["id"],"pass")
 checks.append({"id":x["id"],"status":status,"observation":o,"region":nid or "whole frame / relevant delivery region","source_observation":x["source_fact"]+" Comparison: "+o})
(r/"research/review-001.json").write_text(json.dumps({"checklist_version":c["version"],"checks":checks,"summary":"Nested wetrotor mechanism distinguishable. Hollow shaft/inlet eye path unverified and terminalbox moved; no captiongate yet.","next_changes":["Expose hollow ceramic shaft and inlet central-eye connection","Restore terminalbox toward storephoto left-front while preserving corecut"],"resolved_changes":[]},ensure_ascii=False,indent=2))
