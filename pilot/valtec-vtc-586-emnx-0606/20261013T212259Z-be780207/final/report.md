# VALTEC VTc.586.EMNX.0606: итог пилота

Лучший вариант: **2**, рейтинг **94/100**.
Рейтинг сравнивает варианты, а не измеряет вероятность технической правильности.
Скрипт складывает наблюдения проверяющего агента и не распознаёт изображение: ошибочные отметки могут дать высокий балл неверному разрезу.
Попытки: 2/5. Причина остановки: Selected002: sixpairs, isolatedheaders andreadablevalvestems/seats; stop2/5, preciseprofiles/revisionunknown, same-agent source rereview..
Технический специалист ещё не подтвердил результат.

![Лучший вариант](best.png)

## Проверка выбранного варианта

- Конструкция: 39/45.
- Расположение и связи: 25/25.
- Функциональная полнота: 15/15.
- Внешнее сходство: 10/10.
- Ясность и выноски: 5/5.
- Этап оценки: captioned; разрез без подписей: 91/100.
Баллы, добавленные за подписи, не означают улучшение внутренней конструкции.

Критические противоречия: не обнаружены в проведённой проверке.
Непроверенные критические пункты: нет.
- flowmeters-shape (unknown): Pale shaft/indicator/spring distinguishable; exactfactoryvalveprofile not sectionalinspected.
- returnvalves-shape (unknown): Detailedglandshape notpreciselydocumented, notscored.
- vents-shape (unknown): Two floatwindowsadded despiteplanone; actualrevisiongeometryunknown.
- drains-shape (unknown): Closedouterdrainbody; exactinternalgeometryunknown.

## Состояние результата

Нужна техническая проверка: существенные признаки не подтверждены.
Основания статуса: flowmeters-shape, returnvalves-shape, vents-shape, drains-shape.
Этот статус не означает одобрение специалистом или разрешение публикации.

## Подтверждение отдельных признаков

Счётчики относятся к существенным внутренним признакам, а не к проценту достоверности всего изделия. Потолок баллов учитывает весь checklist.
- Основание model: 4 (headers-type_count, flowmeters-type_count, returnvalves-type_count, outlets-type_count).
- Основание series: 22 (headers-shape, headers-attachment, headers-placement_connections, headers-material, flowmeters-attachment, flowmeters-placement_connections, flowmeters-material, returnvalves-attachment, returnvalves-placement_connections, returnvalves-material, outlets-shape, outlets-attachment, outlets-placement_connections, outlets-material, vents-type_count, vents-attachment, vents-placement_connections, vents-material, drains-type_count, drains-attachment, drains-placement_connections, drains-material).
- Основание analog: 0 (нет).
- Основание unknown: 4 (flowmeters-shape, returnvalves-shape, vents-shape, drains-shape).
- Совпадение изображения с основанием model: 4 (headers-type_count, flowmeters-type_count, returnvalves-type_count, outlets-type_count).
- Совпадение изображения с основанием series: 22 (headers-shape, headers-attachment, headers-placement_connections, headers-material, flowmeters-attachment, flowmeters-placement_connections, flowmeters-material, returnvalves-attachment, returnvalves-placement_connections, returnvalves-material, outlets-shape, outlets-attachment, outlets-placement_connections, outlets-material, vents-type_count, vents-attachment, vents-placement_connections, vents-material, drains-type_count, drains-attachment, drains-placement_connections, drains-material).
- Совпадение изображения с основанием analog: 0 (нет).
- unverified: flowmeters-shape, returnvalves-shape, vents-shape, drains-shape.
- contradicted: нет.
- partial: нет.
Недоступные по текущим источникам баллы: 6; пункты: flowmeters-shape, returnvalves-shape, vents-shape, drains-shape.
Потолок по имеющимся основаниям: 94/100. Это не обещание получить данный балл.

| Пункт | Узел / признак | Основание | Статус | Источник / локатор | Сопоставление |
|---|---|---|---|---|---|
| headers-type_count | headers / type_count | model | pass | card: Exactmodeltable0606 | Exactmanufacturer0606table and manualPDF2twoheaders. Compare: Twoheaders andsixbranches each, counted individually. |
| headers-shape | headers / shape | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | ManualPDF2slenderrectangularmanifoldbodies and portthreadlist; preciseboreprofileunknown. Compare: Twoopened rectangularrails with continuouslongitudinalcavities. |
| headers-attachment | headers / attachment | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2assemblyitem9,PDF3count2. Compare: Twooffsetsteelbracketsholdbothrails. |
| headers-placement_connections | headers / placement_connections | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF1separate supply/return,PDF2eachownparts; bracketsmechanical. Compare: No fluidbridge,solidbracketsseparate. |
| headers-material | headers / material | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3materials AISI304. Compare: Greybrushed railmetalwithoutcoloredsection. |
| flowmeters-type_count | flowmeters / type_count | model | pass | card: Exactmodeltable0606 | Exact0606N6,PDF2item3on supply only. Compare: Six transparenttubes/redbases onlowerheader. |
| flowmeters-shape | flowmeters / shape | unknown | unknown | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF6disassemblyphotos showstem/tube, notprecisioninternalrestriction. Compare: Tube/innerstemshown, precisefactoryrestrictionprofile unavailable. |
| flowmeters-attachment | flowmeters / attachment | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF6service brassnut unscrewed,removablestem/colb. Compare: Threadedbrassbodyjoins toprailport. |
| flowmeters-placement_connections | flowmeters / placement_connections | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2nipple6seat,PDF6stem/tube arrangement,flowcardindicatorwasher. Compare: Six pale slenderrods now extendthroughcartridges to smallblackpad aboveannularlowerseat; firstcutbranchshows emptyspace around centralplug to nipplebore. |
| flowmeters-material | flowmeters / material | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3PP-Rrod/ABSflowmeter/AISI316spring,brassbody/EPDM. Compare: Firstrotameter palepolymerrod andotherexposedpalerods, metalcoils separate; yellowbrassbodies/blackEPDM/redABS. |
| returnvalves-type_count | returnvalves / type_count | model | pass | card: Exactmodeltable0606 | 0606N6;PDF2items2,4. Compare: Sixwhitecaps/valves upperheader. |
| returnvalves-shape | returnvalves / shape | unknown | unknown | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2exteriorcartridgephotos only; internalsectionabsent. Compare: Detailedglandshape notpreciselydocumented, notscored. |
| returnvalves-attachment | returnvalves / attachment | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2item2,2.1,4 shows threadedcartridge/stem/pad. Compare: Firstwhitecap surrounds threadgland/attachedmetalstem. |
| returnvalves-placement_connections | returnvalves / placement_connections | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2item2movesunderhandle,5nipplehasseat. Compare: Six thin stems nowendin smallblackdiscs alignedto sixbottomannularseats; firstcut exposes space aroundplug in exitnipple, no solidpillar. |
| returnvalves-material | returnvalves / material | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3brassCW617N/EPDM. Compare: Yellowbrassbody/blackpadandwhitecontrol matchgeneral documentedmaterialclasses. |
| outlets-type_count | outlets / type_count | model | pass | card: Exactmodeltable0606 | PDF2items5/6N each;0606N6. Compare: Twelvebottomthreadednipples, sixperheader. |
| outlets-shape | outlets / shape | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2nipples5/6photographs. Compare: Firstcut nipple hasannularshoulder andconical-lookingmouth; borepartlyhidden. |
| outlets-attachment | outlets / attachment | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2assemblyphotos and2Nports. Compare: Nipples attached below each matchingcartridge, notfloating. |
| outlets-placement_connections | outlets / placement_connections | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2items5/6seatmatchingvalve and loopfitting. Compare: Firsttwo cutnipples nowshow openemptybore around centraltaper/plug; otherbranches have slimstems/pads atownseat, sharedrailcavity free. |
| outlets-material | outlets / material | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3CW617Nfits. Compare: Yellowbrassendsthreadwithsilversurface shoulders, consistentnickelplatedbrass. |
| vents-type_count | vents / type_count | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3item7count2 andassembly. Compare: Two upright endvents, oneeachrail. |
| vents-shape | vents / shape | unknown | unknown | manual: PDF2 parts/assembly,PDF3materials,PDF6service | Inspected502Nsection differsfrom stockphoto topoutlet; no exactsection. Compare: Two floatwindowsadded despiteplanone; actualrevisiongeometryunknown. |
| vents-attachment | vents / attachment | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3item11VT539count2; PDF2item11. Compare: Eachvent sits onownhexshutoffadapter. |
| vents-placement_connections | vents / placement_connections | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2separateendservice foreachheader, not linkingthem. Compare: Eachvent openchamber connects down to ownrail, no crossconnection. |
| vents-material | vents / material | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3brassnickelbody andPP-Rfloat; exactinnerseatmaterial omitted. Compare: Silverouter/yellowcutbody withpalepolymerfloat; exactpolymergradecannotbe visuallyproved. |
| drains-type_count | drains / type_count | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3item8count2. Compare: Twoblackcappeddrain assemblies,oneeachrightend. |
| drains-shape | drains / shape | unknown | unknown | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3describesrotatingdrain externalonly, no exactinternalsection. Compare: Closedouterdrainbody; exactinternalgeometryunknown. |
| drains-attachment | drains / attachment | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF2item8andPDF3description. Compare: Bothdrains attachedbelowownrailend. |
| drains-placement_connections | drains / placement_connections | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3fill/drainrole andseparatepair. Compare: Separateownheaderports, no fluidbridge; concealeddrainvalveinternals notverified. |
| drains-material | drains / material | series | pass | manual: PDF2 parts/assembly,PDF3materials,PDF6service | PDF3fittings/valvedetails/EPDM. Compare: Silveryfittingsblackcap, substrate mostlyclosed, no contradicting material cue. |
| functional-open | оформление / delivery | series | pass | manual: PDF2assembly/PDF3materials | PDF2valvematingseat andPDF6flowstem, distinctfunctionalnodes required. Compare: Two representativebranchcuts distinguish threadedcartridge, thinrod, blackpad, lowerannularseat andemptydownwardbore. Remainingcontrols seat-specificpreciseprofiles are reconstructed. |
| independent | оформление / delivery | series | pass | manual: PDF2assembly/PDF3materials | Twoheaders serve separateloopends, bracketnotflowpipe. Compare: Twoisolated commoncavities, brackets mechanical no fluidbridge. |
| all-service | оформление / delivery | series | pass | manual: PDF2assembly/PDF3materials | PDF2–3servicecounts. Compare: Two vents,two drains,two brackets; no inventedpump/tank. |
| exterior | оформление / delivery | photo | pass | photo: Live0606card primaryphoto | Twohorizontalrectangularsteelheaders,upperwhitecaps,lowerredflowmeters,rightservice. Compare: Two rectangularpolishedrails,upperreturn/lowerfrontsupply, sixpairs, rightservicepreserved; camera nearerfrontal thanstorepose. |
| controls | оформление / delivery | photo | pass | photo: Live0606card primaryphoto | Photo upperwhite/lowertransparentred, supplierphotoimageexactlook. Compare: Sixupperwhitecaps andsixlowerredtransparentmeters; colors/rowscorrect. |
| dry | оформление / delivery | series | pass | manual: PDF2assembly/PDF3materials | Userdryrule andphysicalemptychannels. Compare: Cavities andtubes dry/empty, no bluefill/flowarrows. |
| natural | оформление / delivery | series | pass | manual: PDF2assembly/PDF3materials | Usernaturalsubstrate,PDF3materialclasses. Compare: Naturalgrey/yellowmetal andpolymercutfaces; redrealprotectivecovers, nosectionstrip. |
| captions | оформление / delivery | series | pass | manual: PDF2assembly/PDF3materials | Names inPDF2–3andAC674card;exactgeometryuncertaintykeptinreport. |

## Основания и реконструкция

- model: нет.
- series: Два независимых коллектора, Настроечные клапаны с расходомерами, Регулирующие клапаны обратки, Выходные ниппели евроконус, Воздухоотводчики, Дренажные краны.
- analog: нет.
- unknown: нет.
- Ограничение: Precise AC674 inner profile/restriction/clearance not documented in inspectedviews.
- Ограничение: Precise returnvalve gland/seats currentrevision not sectionalinspected.
- Ограничение: Installed airvent topoutlet differs from newer502N sideoutletpassport; its float/uppervalve reconstruction not exact.
- Ограничение: Drain innergeometry not shown; render modestgenericshutoff/emptybore, not exactproved.
- Ограничение: CAD321.7MB availablelink but not sectionrendered; no assertion allCADexterior.
- Реконструкция по аналогам: Vent floatprinciple only, not exact current vent mechanismgeometry.

## История вариантов

| Версия | Рейтинг | Этап / база | Критические ошибки | Замечания и исправления |
|---|---:|---|---|---|
| 1 | 70 | base / 70 | flowmeters-placement_connections, returnvalves-placement_connections | Countsandassemblyrecognizable, but solidposts obscure/contradict workingseat/passages andflowrodmaterial wrong. |
| 2 | 94 | captioned / 91 | — | Count/topology andreadability improved, palePP-R rods. Exactfourinternalprofiles remainunknown; highscoreis notexactsectionproof. Исправлено: Solidcolumn placeholders replaced; PalePP-Rflowrods exposed; Seatandnipple relationships readable |

## Источники

- [Original477477 gallery](https://477477.ru/images/products/_alpha-fixed-v2/vtc.586.emnx.0602-a7a02dbcf5b2d87d-detail-46e7bcf538f9262d-62263b38a87c-detail.webp): product_photo; Actual0606 card mainphoto sixpairs; sharedgallery not SKU-specific naming, silhouette/outerfeatures only
- [VTc.586 exactmodeltable](https://valtec.ru/catalog/sistemy_vodyanogo_teplogo_pola/kollektornye_bloki/kollektornyj_blok_iz_nerjaveyushej_stali_so_vstroennymi_rashodomerami_vtc586emnx.html): manufacturer_model; 0606 row confirms6outlets, assemblytypes and material; CADlinks discovered not interiorinspected
- [ПС47514,1024,IVAR](https://valtec.ru/document/technical/VTc.586.EMNX-1024.pdf): manufacturer_series; Exact586series2–12, PDF2parts/photos,3materials,6flowmeterdisassembly; assemblyshowsdifferentendserviceorientation, preservestorephoto
- [VT.AC674](https://valtec.ru/catalog/kollektornye_sistemy/komplektuyuschie_dlya_kollektorov/rashodomer_kollektornyj_vtac674.html): manufacturer_model; Exactlistedcompatiblepart, indicatorwasher, transparenttube, 0.5–5scale; no precisioninternalsection linked
- [VT.VTC30.N](https://valtec.ru/catalog/kollektornye_sistemy/komplektuyuschie_dlya_kollektorov/zapornyj_klapan_dlya_kollektornyh_blokov_vtvtc30n.html): manufacturer_model; Compatibilitytableincludes586; exactreplacement revision notproved forstockphoto, commonpartrole only
- [VT.502.N sectionalpassport](https://valtec.ru/document/technical/VT.502.N-0924.pdf): analog; Samepartfamilyname butdifferenttop/sideventshape and maker than586IVAR; floatprinciple/springmechanism reconstructionaid ONLY, not exactstockgeometry.

## Архив доказательств

- photo, inputs v1, Live0606primarygallery: Sixpaired outlets andstorepose; [файл](../evidence/files/a9f0889cfeccc792692ae84cac0c1e93e68fca4f9132d92f9829b0c109d77c12.webp).
- manual, inputs v1, PDF2section2: Parts/seatnipples/assembly; [файл](../evidence/files/39afd30610fa2845b5129f3a9e00b7578712d2055a51ff5cad74428ec24df7b1.png).
- manual, inputs v1, PDF3section3: Materials and servicecounts; [файл](../evidence/files/0457b297d819c60fc93529de4b0f5b0cabde3246697dfd18ffdd42c63980f0f7.png).
- manual, inputs v1, PDF6section7: AC674stem/tuberemoval; [файл](../evidence/files/a29122f7b92cc37c3f2e6e230e50168509ab9ef1d4473d0e33b2fbc3dddd4899.png).
- card, inputs v1, Exact0606rowandCADlinks: Model6outlets,components,CADnotsectioninspected; [файл](../evidence/files/e44cd75f7b2c772a883af928b4d0d871d97e5466d736d96e33146b23e58c6440.txt).
- flow, inputs v1, AC674manufacturerdescription: Rodindicatorandcompatiblepart; [файл](../evidence/files/fe0efc0db5899cc875b859d13e33daad735ad94b2ff9a787cce6f3f7b7850720.txt).
- valve, inputs v1, VTC30compatibilitycard: Commonrole,exactrevisionunknown; [файл](../evidence/files/fe0efc0db5899cc875b859d13e33daad735ad94b2ff9a787cce6f3f7b7850720.txt).
- vent-analogy, inputs v1, 502N0924PDF2: Differentventgeometry, ONLYfloatprinciplereconstructionaid; [файл](../evidence/files/f7206824c5f7fb54e1cd33c8fafde9c3ff773ddff9a9307346d7c9c2e23c0c6d.png).

## Проверка подписей

По всем выноскам зарегистрированы проверка названия и визуальный осмотр конечных точек. Это проверка агентом, не автоматическое распознавание деталей.
