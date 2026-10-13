from pathlib import Path
import json
r=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vtc-586-emnx-0606/20261013T212259Z-be780207")
checklist=json.loads((r/"input/checklist-draft.json").read_text())
obs={
"headers":["Twoheaders andsixbranches each, counted individually.","Twoopened rectangularrails with continuouslongitudinalcavities.","Twooffsetsteelbracketsholdbothrails.","No fluidbridge,solidbracketsseparate.","Greybrushed railmetalwithoutcoloredsection."],
"flowmeters":["Six transparenttubes/redbases onlowerheader.","Tube/innerstemshown, precisefactoryrestrictionprofile unavailable.","Threadedbrassbodyjoins toprailport.","Longsolidmetalposts span entirecavity underallmeters; no discernibleannularregulatinggap.","Lowerfirst rod appearsmetallic, notpalePP-Rdescribed in table."],
"returnvalves":["Sixwhitecaps/valves upperheader.","Detailedglandshape notpreciselydocumented, notscored.","Firstwhitecap surrounds threadgland/attachedmetalstem.","Five intact branches shownassolidmetalposts reachingbottomwall, notstem/padmeetingopenbranchseat.","Yellowbrassbody/blackpadandwhitecontrol matchgeneral documentedmaterialclasses."],
"outlets":["Twelvebottomthreadednipples, sixperheader.","Firstcut nipple hasannularshoulder andconical-lookingmouth; borepartlyhidden.","Nipples attached below each matchingcartridge, notfloating.","Solidposts seemblockbranchopenings, no visibleworkingannulargapfrom commoncavity into eachnipple.","Yellowbrassendsthreadwithsilversurface shoulders, consistentnickelplatedbrass."],
"vents":["Two upright endvents, oneeachrail.","Two floatwindowsadded despiteplanone; actualrevisiongeometryunknown.","Eachvent sits onownhexshutoffadapter.","Eachvent openchamber connects down to ownrail, no crossconnection.","Silverouter/yellowcutbody withpalepolymerfloat; exactpolymergradecannotbe visuallyproved."],
"drains":["Twoblackcappeddrain assemblies,oneeachrightend.","Closedouterdrainbody; exactinternalgeometryunknown.","Bothdrains attachedbelowownrailend.","Separateownheaderports, no fluidbridge; concealeddrainvalveinternals notverified.","Silveryfittingsblackcap, substrate mostlyclosed, no contradicting material cue."]
}
delivery={
"functional-open":"Firstreturn/supply sectionshowsstem blackrings, but no clear actualseat/openannularpassage; otherbranches resembleclosedsolidposts.",
"independent":"Twoisolated commoncavities, brackets mechanical no fluidbridge.",
"all-service":"Two vents,two drains,two brackets; no inventedpump/tank.",
"exterior":"Two rectangularpolishedrails,upperreturn/lowerfrontsupply, sixpairs, rightservicepreserved; camera nearerfrontal thanstorepose.",
"controls":"Sixupperwhitecaps andsixlowerredtransparentmeters; colors/rowscorrect.",
"dry":"Cavities andtubes dry/empty, no bluefill/flowarrows.",
"natural":"Naturalgrey/yellowmetal andpolymercutfaces; redrealprotectivecovers, nosectionstrip.",
"captions":"Baseunlabelled."
}
statuses={"flowmeters-placement_connections":"fail","flowmeters-material":"fail","returnvalves-placement_connections":"fail","outlets-placement_connections":"fail","functional-open":"fail"}
aspects=["type_count","shape","attachment","placement_connections","material"]
checks=[]
for c in checklist["checks"]:
 n=c.get("node_id");o=obs[n][aspects.index(c["aspect"])] if n else delivery[c["id"]]
 status="unknown" if not c["evidence_supported"] or c.get("caption_dependent") else statuses.get(c["id"],"pass")
 checks.append({"id":c["id"],"status":status,"region":n or "wholeframe / relevantdeliveryregion","observation":o,"source_observation":c["source_fact"]+" Compare: "+o})
(r/"research/review-001.json").write_text(json.dumps({"checklist_version":checklist["version"],"checks":checks,"summary":"Countsandassemblyrecognizable, but solidposts obscure/contradict workingseat/passages andflowrodmaterial wrong.","next_changes":["Replace solidposts with valve stems,pads,annularseats and emptybranchbores","Show palePP-Rflowmeterrods"],"resolved_changes":[]},ensure_ascii=False,indent=2))
