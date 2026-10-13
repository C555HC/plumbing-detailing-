from pathlib import Path
import json,hashlib
r=Path("/Users/nikitas/Documents/ChatGPT/Ворк/plumbing-detailing-/output/cutaways/valtec-vrs-254-18/20261013T204717Z-356d29a5")
def xy(x,y):return[x/2400,y/1800]
items=[
("housing","Чугунный корпус\nнасоса",40,360,350,395,[.15,.6],"manual"),
("impeller","Рабочее колесо\n(крыльчатка)",40,590,350,625,[.255,.41],"manual"),
("plate","Прижимная\nпластина",40,810,350,845,[.337,.421],"assembly"),
("frontbearing","Керамическая опора\nи EPDM-манжета",40,1030,370,1065,[.373,.505],"assembly"),
("shaft","Керамический вал\nс осевым каналом",370,1560,540,1530,[.507,.535],"assembly"),
("rotor","Ротор\nэлектродвигателя",900,1560,1070,1530,[.53,.475],"manual"),
("stator","Статор\nс обмоткой",1960,730,1930,765,[.585,.375],"manual"),
("can","Разделительная\nобойма",1960,970,1930,1005,[.69,.53],"assembly"),
("rear","Керамическая\nопора вала",1960,1200,1930,1235,[.66,.555],"assembly"),
("box","Клеммная коробка\nи переключатель скоростей",1000,210,1250,300,[.441,.15],"manual"),
("vent","Пробка выпуска\nвоздуха",1530,1560,1700,1530,[.75,.587],"manual")]
labels={"color":"#073C76","canvas":{"size":[2400,1800],"image_box":[410,350,1920,1483]},"title":{"text":"VALTEC VRS 25/4-180\nВнутреннее устройство","position":xy(55,45),"font_size":49},"labels":[]}
for i,t,x,y,sx,sy,target,src in items: labels["labels"].append({"id":i,"text":t,"position":xy(x,y),"font_size":30,"line_start":xy(sx,sy),"target_image":target,"source_id":src})
(r/"research/labels-002.json").write_text(json.dumps(labels,ensure_ascii=False,indent=2))
