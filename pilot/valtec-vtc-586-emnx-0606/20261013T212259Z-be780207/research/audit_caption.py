from pathlib import Path
import json,hashlib
r=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vtc-586-emnx-0606/20261013T212259Z-be780207");base=r/"attempts/002/image.png";labelsfile=r/"research/labels-002.json";preview=r/"research/preview-002.png"
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
labels=json.loads(labelsfile.read_text());audit={"base_sha256":h(base),"labels_sha256":h(labelsfile),"preview_sha256":h(preview),"layout_checked":True,"title_checked":True,"checks":[]}
obs={"cap":"Endpoint on retainedwhitecapwall, correctedfrom brassinnerstem.","stem":"Endpoint on movingmetalsteminsideuppercartridge.","return":"Endpoint on upperrailcavitywall; upperwhitevalverow isreturnperPDF2.","seal":"Endpoint onblackpad atlowerannularseat ofrepresentativeupperbranch; combinedfunctionalcaption notprecisegeometryclaim.","flow":"Endpoint onindicatorwasherinsidefirsttransparenttube, supportsrotametername.","rod":"Endpoint onpalepolymerrodinsidefirstcutbrassflowcartridge.","vent":"Endpoint onupperventcasingcap, venttype/nameperassembly; exactinnervalvegeometryunverified.","float":"Endpoint onpalefloat in illustrativeupperventwindow, existence/materialpergroupmanual; exactprofileisreconstructed.","isolator":"Endpoint onhexadapterbelowvent, item11; hiddencheckvalve not claimed.","drain":"Endpoint onblackdrainbody/capbelowupperend; nameofwholepart only.","bracket":"Endpoint onrightzincsteelstrip, correctedfrommountinghole.","adjust":"Endpoint onredprotectivebaseofadjustableflowcartridge; wholevalveunitnamed, notredplasticcalledseal.","supply":"Endpoint onlowerrailwall, lowerflowrowonlysupplypermanual.","outlets":"Endpoint onone lowerthreadedbranchnipple, commonEKconnectornameperPDF2."}
for x in labels["labels"]:
 audit["checks"].append({"id":x["id"],"source_ids":[x["source_id"]],"locator":"AC674manufacturerdescription" if x["source_id"]=="flow" else "586passportPDF2parts,PDF3materials,PDF6service","text_checked":True,"target_checked":True,"observation":obs[x["id"]]})
(r/"research/label-review-002.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2))
review=json.loads((r/"research/review-002.json").read_text())
for x in review["checks"]:
 if x["id"]=="captions":x.update(status="pass",observation="14labels/titlecomposed, everyendpoint/name inspectedagainst applicableevidence;3initialtargets correctedbeforeaudit.",source_observation="Names inPDF2–3andAC674card;exactgeometryuncertaintykeptinreport.")
(r/"research/review-captioned-002.json").write_text(json.dumps(review,ensure_ascii=False,indent=2))
