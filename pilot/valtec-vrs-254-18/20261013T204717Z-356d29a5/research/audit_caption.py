from pathlib import Path
import json,hashlib,sys
r=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vrs-254-18/20261013T204717Z-356d29a5")
n=sys.argv[1] if len(sys.argv)>1 else "002"
label=r/f"research/labels-{n}.json";preview=r/f"research/preview-{n}.png"
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
labels=json.loads(label.read_text())
audit={"base_sha256":h(r/f"attempts/{n}/image.png"),"labels_sha256":h(label),"preview_sha256":h(preview),"layout_checked":True,"title_checked":True,"checks":[]}
obs={"housing":"Endpoint on grey castiron inner neck wall, not background; corrected misplaced firstdraftendpoint.","impeller":"Endpoint on pale polymer wheel web, not retainingplate.","plate":"Endpoint on perforated metaldisc, matches item7.","frontbearing":"Endpoint on palecollar/blackEPDM assembly, matches3–5; combined functionalcaption.","shaft":"Endpoint on exposed pale ceramic-lined axialslot, not rotor metalwall.","rotor":"Endpoint on grey cylindricalrotor wall above inspectionwindow.","stator":"Endpoint on fixed laminationstack contiguous to visible coilendturns.","can":"Endpoint on thin metalcan boundary outside rotor and inside stator.","rear":"Endpoint on pale rearbearingcollar at shaftend.","box":"Endpoint on rotaryswitch on blackterminalbox.","vent":"Endpoint on retained main slotted ventplug; secondplug defect inbase noted separately for draft002."}
for x in labels["labels"]:
 audit["checks"].append({"id":x["id"],"text_checked":True,"target_checked":True,"source_ids":[x["source_id"]],"locator":"PDF2 §4 illustration/§6.4 ventplug" if x["source_id"]=="manual" else "PDF13 printed12 figure1–7 and text","observation":obs[x["id"]]})
(r/f"research/label-review-{n}.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2))
review=json.loads((r/f"research/review-{n}.json").read_text())
for x in review["checks"]:
 if x["id"]=="captions":
  x.update(status="pass",observation="11 Russian labels composed and each endpoint/source checked; title/layout inspected.",source_observation="Named functionalparts in factorymanual/assembly; no unsupportedprecisebladecount caption.")
(r/f"research/review-captioned-{n}.json").write_text(json.dumps(review,ensure_ascii=False,indent=2))

