from pathlib import Path
import json
r=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vtc-586-emnx-0606/20261013T212259Z-be780207")
def xy(x,y):return[x/2800,y/2100]
items=[
("cap","Ручка регулирующего\nклапана",40,320,380,350,[.215,.12],"manual"),
("stem","Шток клапана",40,520,380,545,[.214,.224],"manual"),
("return","Обратный коллектор\nиз нержавеющей стали",40,710,410,745,[.166,.263],"manual"),
("seal","Уплотнение клапана\nи седло",40,930,380,965,[.215,.276],"manual"),
("flow","Расходомер\n(ротаметр)",40,1180,380,1215,[.224,.531],"flow"),
("rod","Полимерный шток\nрасходомера",40,1450,380,1485,[.217,.665],"manual"),
("vent","Автоматический\nвоздухоотводчик",2330,320,2300,355,[.789,.072],"manual"),
("float","Поплавок\nвоздухоотводчика",2330,520,2300,555,[.79,.155],"manual"),
("isolator","Отсекающий клапан\nвоздухоотводчика",2330,720,2300,755,[.79,.218],"manual"),
("drain","Дренажный кран",2330,950,2300,975,[.77,.419],"manual"),
("bracket","Крепёжный\nкронштейн",2330,1180,2300,1215,[.884,.555],"manual"),
("adjust","Настроечный клапан\nрасходомера",2330,1450,2300,1485,[.666,.678],"manual"),
("supply","Подающий коллектор\nиз нержавеющей стали",500,1860,720,1835,[.60,.77],"manual"),
("outlets","Выходы контуров\n3/4″ «евроконус»",1450,1860,1680,1835,[.576,.869],"manual")]
labels={"color":"#073C76","canvas":{"size":[2800,2100],"image_box":[470,330,2290,1730]},"title":{"text":"VALTEC VTc.586.EMNX.0606\nКоллекторная группа · 6 контуров\nВнутреннее устройство","position":xy(55,35),"font_size":43},"labels":[]}
for i,t,x,y,sx,sy,target,src in items:labels["labels"].append({"id":i,"text":t,"position":xy(x,y),"font_size":29,"line_start":xy(sx,sy),"target_image":target,"source_id":src})
(r/"research/labels-002.json").write_text(json.dumps(labels,ensure_ascii=False,indent=2))
