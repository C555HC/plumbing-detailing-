from pathlib import Path
import json
r=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vrs-254-18/20261013T204717Z-356d29a5")
d=json.loads((r/"research/review-001.json").read_text())
changes={
"shaft-placement_connections":("pass","Axial ceramic-lined empty slot now exposed through rotor and pale front/rearshaft stubs, all on commonaxis."),
"cooling-path":("pass","Empty slot runs longitudinally within ceramic shaft; large platehole opens chamber, nofluid."),
"controls":("pass","Black speedknob box restored to motor upperleft, matching relative store side; wiring and cableentry visible."),
"silhouette":("fail","Two silver slotted ventplugs now generated on right end; storephoto/manual shows one, nottwo."),
"impeller-placement_connections":("unknown","Central wheel eye exposed, but lower inlet cavity still opens peripheral volute; hidden eye inlet passage not established.")
}
for x in d["checks"]:
 if x["id"] in changes:
  x["status"],x["observation"]=changes[x["id"]]; x["source_observation"]=next(c["source_fact"] for c in json.loads((r/"input/checklist-draft.json").read_text())["checks"] if c["id"]==x["id"])+" Comparison: "+x["observation"]
 # current-frame observation refresh rather than pretending previous output independently validated
 if x["id"]=="impeller-shape": x["observation"]="Wheel partlysectioned to show centraleye and radialpassages; exactcurrentbladeprofile stillunavailable."
 if x["id"]=="shaft-shape": x["observation"]="Annular palecollars and straight ceramicshaft partlywindowed, lumen distinguishable."
d["summary"]="Shaftbore and terminalbox improved; duplicate ventplug regression, central inlet-to-eye still unverified."
d["next_changes"]=["Remove second silver ventplug","Clarify lower suction passage to central impellereye"]
d["resolved_changes"]=["Longitudinal shaft lumen exposed","Terminalbox leftupperposition restored"]
(r/"research/review-002.json").write_text(json.dumps(d,ensure_ascii=False,indent=2))

