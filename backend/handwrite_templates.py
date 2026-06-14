"""手写儿童简笔画模板（针对评审不过的动物/自然/食物）
覆盖 35 个高频模板，替换 aliases.json 中的对应条目。
"""
import json
from pathlib import Path

path = Path(__file__).parent / "aliases.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

shapes = data.setdefault("complex_shapes", {})

# ── 手写模板 ─────────────────────────────────────────

HANDMADE = {

# ═══ 动物 ═══

"兔子": {
  "aliases": ["兔子","兔兔","小兔","小白兔","rabbit","bunny","兔","tu tu"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":300,"radiusX":40,"radiusY":38,"color":"#f5f5f5"},
    {"action":"drawEllipse","x":375,"y":230,"radiusX":14,"radiusY":30,"color":"#f5f5f5"},
    {"action":"drawEllipse","x":425,"y":230,"radiusX":14,"radiusY":30,"color":"#f5f5f5"},
    {"action":"drawEllipse","x":375,"y":235,"radiusX":10,"radiusY":22,"color":"pink"},
    {"action":"drawEllipse","x":425,"y":235,"radiusX":10,"radiusY":22,"color":"pink"},
    {"action":"drawCircle","x":383,"y":295,"radius":6,"color":"black"},
    {"action":"drawCircle","x":417,"y":295,"radius":6,"color":"black"},
    {"action":"drawCircle","x":383,"y":293,"radius":2,"color":"white"},
    {"action":"drawCircle","x":417,"y":293,"radius":2,"color":"white"},
    {"action":"drawCircle","x":400,"y":308,"radius":4,"color":"pink"},
    {"action":"drawArc","x":400,"y":318,"radius":8,"startAngle":0.15,"endAngle":2.99,"color":"black"},
    {"action":"drawEllipse","x":400,"y":390,"radiusX":38,"radiusY":35,"color":"#f5f5f5"},
    {"action":"drawLine","x1":370,"y1":400,"x2":358,"y2":440,"color":"black"},
    {"action":"drawLine","x1":430,"y1":400,"x2":442,"y2":440,"color":"black"},
    {"action":"drawCircle","x":443,"y":378,"radius":8,"color":"#f5f5f5"},
  ]
},

"狗": {
  "aliases": ["狗","狗狗","小狗","汪汪","dog","doggie","gou gou"],
  "actions": [
    {"action":"drawCircle","x":400,"y":270,"radius":45,"color":"#d4a574"},
    {"action":"drawEllipse","x":360,"y":245,"radiusX":20,"radiusY":28,"color":"#d4a574"},
    {"action":"drawEllipse","x":440,"y":245,"radiusX":20,"radiusY":28,"color":"#d4a574"},
    {"action":"drawCircle","x":375,"y":260,"radius":8,"color":"black"},
    {"action":"drawCircle","x":425,"y":260,"radius":8,"color":"black"},
    {"action":"drawCircle","x":400,"y":278,"radius":10,"color":"black"},
    {"action":"drawCircle","x":400,"y":275,"radius":6,"color":"pink"},
    {"action":"drawArc","x":400,"y":295,"radius":12,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawLine","x1":395,"y1":285,"x2":395,"y2":289,"color":"black"},
    {"action":"drawLine","x1":405,"y1":285,"x2":405,"y2":289,"color":"black"},
    {"action":"drawEllipse","x":400,"y":370,"radiusX":50,"radiusY":40,"color":"#d4a574"},
    {"action":"drawLine","x1":358,"y1":380,"x2":340,"y2":430,"color":"#d4a574"},
    {"action":"drawLine","x1":442,"y1":380,"x2":460,"y2":430,"color":"#d4a574"},
    {"action":"drawLine","x1":380,"y1":385,"x2":375,"y2":430,"color":"#d4a574"},
    {"action":"drawLine","x1":420,"y1":385,"x2":425,"y2":430,"color":"#d4a574"},
    {"action":"drawArc","x":455,"y":350,"radius":20,"startAngle":0.5,"endAngle":2.5,"color":"#d4a574"},
  ]
},

"鱼": {
  "aliases": ["鱼","小鱼","鱼儿","鱼鱼","yu yu","金鱼"],
  "actions": [
    {"action":"drawEllipse","x":380,"y":300,"radiusX":70,"radiusY":38,"color":"#4fc3f7"},
    {"action":"drawPolygon","points":[{"x":445,"y":300},{"x":500,"y":265},{"x":500,"y":335}],"color":"#4fc3f7"},
    {"action":"drawCircle","x":340,"y":288,"radius":8,"color":"black"},
    {"action":"drawCircle","x":342,"y":286,"radius":3,"color":"white"},
    {"action":"drawPolygon","points":[{"x":350,"y":275},{"x":370,"y":260},{"x":380,"y":278}],"color":"#4fc3f7"},
    {"action":"drawPolygon","points":[{"x":350,"y":325},{"x":370,"y":340},{"x":380,"y":322}],"color":"#4fc3f7"},
    {"action":"drawArc","x":355,"y":300,"radius":40,"startAngle":0.15,"endAngle":0.8,"color":"black"},
  ]
},

"鸟": {
  "aliases": ["鸟","小鸟","鸟儿","niao niao","啾啾","小鳥"],
  "actions": [
    {"action":"drawEllipse","x":380,"y":310,"radiusX":35,"radiusY":28,"color":"#66bb6a"},
    {"action":"drawCircle","x":350,"y":280,"radius":22,"color":"#66bb6a"},
    {"action":"drawCircle","x":345,"y":275,"radius":4,"color":"black"},
    {"action":"drawPolygon","points":[{"x":328,"y":280},{"x":300,"y":290},{"x":328,"y":285}],"color":"orange"},
    {"action":"drawEllipse","x":420,"y":300,"radiusX":50,"radiusY":18,"color":"#81c784"},
    {"action":"drawLine","x1":380,"y1":340,"x2":378,"y2":380,"color":"orange"},
    {"action":"drawLine","x1":400,"y1":338,"x2":402,"y2":378,"color":"orange"},
    {"action":"drawLine","x1":378,"y1":380,"x2":368,"y2":390,"color":"orange"},
    {"action":"drawLine","x1":402,"y1":378,"x2":412,"y2":390,"color":"orange"},
  ]
},

"蝴蝶": {
  "aliases": ["蝴蝶","蝴蝶蝶","hú dié","蝶蝶","花蝴蝶"],
  "actions": [
    {"action":"drawLine","x1":400,"y1":220,"x2":400,"y2":380,"color":"black"},
    {"action":"drawCircle","x":400,"y":215,"radius":10,"color":"black"},
    {"action":"drawPolygon","points":[{"x":400,"y":240},{"x":340,"y":200},{"x":300,"y":260},{"x":360,"y":280}],"color":"#e91e63"},
    {"action":"drawPolygon","points":[{"x":400,"y":240},{"x":460,"y":200},{"x":500,"y":260},{"x":440,"y":280}],"color":"#e91e63"},
    {"action":"drawPolygon","points":[{"x":400,"y":300},{"x":350,"y":280},{"x":320,"y":340},{"x":370,"y":360}],"color":"#9c27b0"},
    {"action":"drawPolygon","points":[{"x":400,"y":300},{"x":450,"y":280},{"x":480,"y":340},{"x":430,"y":360}],"color":"#9c27b0"},
    {"action":"drawCircle","x":340,"y":230,"radius":6,"color":"#f06292"},
    {"action":"drawCircle","x":460,"y":230,"radius":6,"color":"#f06292"},
    {"action":"drawLine","x1":395,"y1":215,"x2":370,"y2":200,"color":"black"},
    {"action":"drawLine","x1":405,"y1":215,"x2":430,"y2":200,"color":"black"},
  ]
},

"乌龟": {
  "aliases": ["乌龟","龟龟","小乌龟","wū guī","王八"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":310,"radiusX":60,"radiusY":50,"color":"#4caf50"},
    {"action":"drawArc","x":400,"y":305,"radius":50,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawCircle","x":340,"y":270,"radius":20,"color":"#81c784"},
    {"action":"drawCircle","x":335,"y":265,"radius":4,"color":"black"},
    {"action":"drawArc","x":330,"y":278,"radius":6,"startAngle":0.15,"endAngle":2.99,"color":"black"},
    {"action":"drawEllipse","x":370,"y":370,"radiusX":10,"radiusY":5,"color":"#4caf50"},
    {"action":"drawEllipse","x":430,"y":370,"radiusX":10,"radiusY":5,"color":"#4caf50"},
    {"action":"drawEllipse","x":350,"y":360,"radiusX":12,"radiusY":6,"color":"#4caf50"},
    {"action":"drawEllipse","x":450,"y":360,"radiusX":12,"radiusY":6,"color":"#4caf50"},
    {"action":"drawCircle","x":450,"y":310,"radius":5,"color":"#388e3c"},
    {"action":"drawLine","x1":340,"y1":280,"x2":340,"y2":340,"color":"#4caf50"},
    {"action":"drawLine","x1":360,"y1":250,"x2":340,"y2":260,"color":"#4caf50"},
  ]
},

"大象": {
  "aliases": ["大象","象象","dà xiàng","小象","大象象"],
  "actions": [
    {"action":"drawEllipse","x":420,"y":330,"radiusX":80,"radiusY":60,"color":"#9e9e9e"},
    {"action":"drawCircle","x":340,"y":250,"radius":45,"color":"#9e9e9e"},
    {"action":"drawEllipse","x":340,"y":300,"radiusX":18,"radiusY":50,"color":"#9e9e9e"},
    {"action":"drawCircle","x":318,"y":240,"radius":12,"color":"white"},
    {"action":"drawCircle","x":325,"y":238,"radius":6,"color":"black"},
    {"action":"drawEllipse","x":310,"y":230,"radiusX":22,"radiusY":18,"color":"#bdbdbd"},
    {"action":"drawEllipse","x":370,"y":230,"radiusX":22,"radiusY":18,"color":"#bdbdbd"},
    {"action":"drawLine","x1":300,"y1":380,"x2":300,"y2":460,"color":"#9e9e9e"},
    {"action":"drawLine","x1":360,"y1":380,"x2":360,"y2":460,"color":"#9e9e9e"},
    {"action":"drawLine","x1":450,"y1":380,"x2":450,"y2":460,"color":"#9e9e9e"},
    {"action":"drawLine","x1":490,"y1":380,"x2":490,"y2":460,"color":"#9e9e9e"},
    {"action":"drawLine","x1":280,"y1":455,"x2":310,"y2":455,"color":"#9e9e9e"},
    {"action":"drawLine","x1":340,"y1":455,"x2":370,"y2":455,"color":"#9e9e9e"},
    {"action":"drawLine","x1":440,"y1":455,"x2":460,"y2":455,"color":"#9e9e9e"},
    {"action":"drawLine","x1":480,"y1":455,"x2":500,"y2":455,"color":"#9e9e9e"},
    {"action":"drawLine","x1":470,"y1":350,"x2":520,"y2":340,"color":"#9e9e9e"},
  ]
},

"熊猫": {
  "aliases": ["熊猫","滚滚","panda","大熊猫","猫熊"],
  "actions": [
    {"action":"drawCircle","x":400,"y":260,"radius":55,"color":"white"},
    {"action":"drawCircle","x":355,"y":235,"radius":22,"color":"black"},
    {"action":"drawCircle","x":445,"y":235,"radius":22,"color":"black"},
    {"action":"drawCircle","x":365,"y":245,"radius":22,"color":"black"},
    {"action":"drawCircle","x":435,"y":245,"radius":22,"color":"black"},
    {"action":"drawCircle","x":370,"y":255,"radius":8,"color":"white"},
    {"action":"drawCircle","x":430,"y":255,"radius":8,"color":"white"},
    {"action":"drawCircle","x":372,"y":253,"radius":4,"color":"black"},
    {"action":"drawCircle","x":428,"y":253,"radius":4,"color":"black"},
    {"action":"drawCircle","x":400,"y":272,"radius":8,"color":"black"},
    {"action":"drawArc","x":400,"y":290,"radius":12,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawEllipse","x":400,"y":360,"radiusX":55,"radiusY":45,"color":"white"},
    {"action":"drawEllipse","x":370,"y":340,"radiusX":18,"radiusY":22,"color":"black"},
    {"action":"drawEllipse","x":430,"y":340,"radiusX":18,"radiusY":22,"color":"black"},
    {"action":"drawEllipse","x":380,"y":400,"radiusX":12,"radiusY":8,"color":"black"},
    {"action":"drawEllipse","x":420,"y":400,"radiusX":12,"radiusY":8,"color":"black"},
  ]
},

"青蛙": {
  "aliases": ["青蛙","蛙蛙","小青蛙","青娃","wa wa"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":340,"radiusX":60,"radiusY":40,"color":"#4caf50"},
    {"action":"drawEllipse","x":400,"y":280,"radiusX":55,"radiusY":38,"color":"#66bb6a"},
    {"action":"drawCircle","x":370,"y":265,"radius":16,"color":"white"},
    {"action":"drawCircle","x":430,"y":265,"radius":16,"color":"white"},
    {"action":"drawCircle","x":372,"y":263,"radius":8,"color":"black"},
    {"action":"drawCircle","x":428,"y":263,"radius":8,"color":"black"},
    {"action":"drawArc","x":400,"y":295,"radius":20,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawEllipse","x":360,"y":380,"radiusX":12,"radiusY":6,"color":"#4caf50"},
    {"action":"drawEllipse","x":440,"y":380,"radiusX":12,"radiusY":6,"color":"#4caf50"},
    {"action":"drawLine","x1":360,"y1":340,"x2":340,"y2":380,"color":"#4caf50"},
    {"action":"drawLine","x1":440,"y1":340,"x2":460,"y2":380,"color":"#4caf50"},
    {"action":"drawLine","x1":400,"y1":380,"x2":400,"y2":400,"color":"#4caf50"},
  ]
},

"蜜蜂": {
  "aliases": ["蜜蜂","蜜蜂蜂","小蜜蜂","mì fēng","嗡嗡"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":300,"radiusX":30,"radiusY":22,"color":"#ffc107"},
    {"action":"drawLine","x1":372,"y1":290,"x2":428,"y2":290,"color":"black"},
    {"action":"drawLine","x1":372,"y1":300,"x2":428,"y2":300,"color":"black"},
    {"action":"drawLine","x1":372,"y1":310,"x2":428,"y2":310,"color":"black"},
    {"action":"drawEllipse","x":365,"y":288,"radiusX":18,"radiusY":12,"color":"#b3e5fc"},
    {"action":"drawEllipse","x":365,"y":312,"radiusX":18,"radiusY":12,"color":"#b3e5fc"},
    {"action":"drawEllipse","x":435,"y":290,"radiusX":18,"radiusY":12,"color":"#b3e5fc"},
    {"action":"drawEllipse","x":435,"y":310,"radiusX":18,"radiusY":12,"color":"#b3e5fc"},
    {"action":"drawCircle","x":425,"y":285,"radius":6,"color":"black"},
    {"action":"drawLine","x1":430,"y1":285,"x2":445,"y2":275,"color":"black"},
  ]
},

"蜗牛": {
  "aliases": ["蜗牛","蜗蜗","牛牛","小蜗牛","wō niú"],
  "actions": [
    {"action":"drawCircle","x":400,"y":310,"radius":40,"color":"#ffb74d"},
    {"action":"drawArc","x":400,"y":310,"radius":30,"startAngle":0,"endAngle":1.5,"color":"#e65100"},
    {"action":"drawArc","x":400,"y":310,"radius":20,"startAngle":0,"endAngle":1.5,"color":"#e65100"},
    {"action":"drawArc","x":400,"y":310,"radius":10,"startAngle":0,"endAngle":1.5,"color":"#e65100"},
    {"action":"drawEllipse","x":340,"y":300,"radiusX":30,"radiusY":18,"color":"#ffcc80"},
    {"action":"drawCircle","x":325,"y":295,"radius":5,"color":"black"},
    {"action":"drawLine","x1":325,"y1":295,"x2":315,"y2":290,"color":"black"},
    {"action":"drawLine","x1":325,"y1":295,"x2":315,"y2":300,"color":"black"},
    {"action":"drawLine","x1":340,"y1":315,"x2":340,"y2":360,"color":"#ffcc80"},
    {"action":"drawLine","x1":360,"y1":315,"x2":360,"y2":360,"color":"#ffcc80"},
    {"action":"drawLine","x1":380,"y1":315,"x2":380,"y2":360,"color":"#ffcc80"},
  ]
},

"鸡": {
  "aliases": ["鸡","小鸡","母鸡","大公鸡","ji ji","咕咕"],
  "actions": [
    {"action":"drawCircle","x":400,"y":330,"radius":40,"color":"#ffb74d"},
    {"action":"drawCircle","x":350,"y":290,"radius":28,"color":"#ffcc80"},
    {"action":"drawCircle","x":340,"y":278,"radius":5,"color":"black"},
    {"action":"drawPolygon","points":[{"x":323,"y":290},{"x":300,"y":300},{"x":323,"y":295}],"color":"orange"},
    {"action":"drawEllipse","x":345,"y":265,"radiusX":16,"radiusY":10,"color":"red"},
    {"action":"drawArc","x":340,"y":310,"radius":6,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawEllipse","x":420,"y":370,"radiusX":35,"radiusY":28,"color":"#ffb74d"},
    {"action":"drawLine","x1":380,"y1":370,"x2":375,"y2":420,"color":"orange"},
    {"action":"drawLine","x1":420,"y1":370,"x2":420,"y2":420,"color":"orange"},
    {"action":"drawPolygon","points":[{"x":435,"y":370},{"x":460,"y":365},{"x":440,"y":380}],"color":"orange"},
  ]
},

"鸭": {
  "aliases": ["鸭","鸭子","鸭鸭","小鸭","小鸭子","ga ga"],
  "actions": [
    {"action":"drawEllipse","x":380,"y":340,"radiusX":45,"radiusY":35,"color":"#fff176"},
    {"action":"drawCircle","x":350,"y":290,"radius":30,"color":"#fff176"},
    {"action":"drawCircle","x":338,"y":280,"radius":4,"color":"black"},
    {"action":"drawEllipse","x":318,"y":295,"radiusX":12,"radiusY":6,"color":"orange"},
    {"action":"drawEllipse","x":430,"y":370,"radiusX":35,"radiusY":25,"color":"#fff176"},
    {"action":"drawLine","x1":360,"y1":370,"x2":355,"y2":420,"color":"orange"},
    {"action":"drawLine","x1":400,"y1":370,"x2":400,"y2":420,"color":"orange"},
    {"action":"drawCircle","x":365,"y":360,"radius":8,"color":"#64b5f6"},
    {"action":"drawCircle","x":395,"y":360,"radius":8,"color":"#64b5f6"},
  ]
},

"牛": {
  "aliases": ["牛","牛牛","小牛","奶牛","niu niu"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":340,"radiusX":70,"radiusY":50,"color":"#f5f5f5"},
    {"action":"drawCircle","x":360,"y":260,"radius":40,"color":"#f5f5f5"},
    {"action":"drawCircle","x":330,"y":225,"radius":16,"color":"#f5f5f5"},
    {"action":"drawCircle","x":390,"y":225,"radius":16,"color":"#f5f5f5"},
    {"action":"drawCircle","x":345,"y":250,"radius":5,"color":"black"},
    {"action":"drawCircle","x":375,"y":250,"radius":5,"color":"black"},
    {"action":"drawEllipse","x":360,"y":268,"radiusX":12,"radiusY":8,"color":"pink"},
    {"action":"drawArc","x":400,"y":405,"radiusX":50,"radiusY":20,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawLine","x1":340,"y1":380,"x2":335,"y2":440,"color":"#f5f5f5"},
    {"action":"drawLine","x1":380,"y1":380,"x2":375,"y2":440,"color":"#f5f5f5"},
    {"action":"drawLine","x1":420,"y1":380,"x2":425,"y2":440,"color":"#f5f5f5"},
    {"action":"drawLine","x1":460,"y1":380,"x2":465,"y2":440,"color":"#f5f5f5"},
  ]
},

"猪": {
  "aliases": ["猪","小猪","猪猪","佩奇","zhū zhū"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":340,"radiusX":65,"radiusY":50,"color":"pink"},
    {"action":"drawCircle","x":400,"y":260,"radius":45,"color":"pink"},
    {"action":"drawEllipse","x":370,"y":240,"radiusX":12,"radiusY":10,"color":"pink"},
    {"action":"drawEllipse","x":430,"y":240,"radiusX":12,"radiusY":10,"color":"pink"},
    {"action":"drawCircle","x":380,"y":255,"radius":5,"color":"black"},
    {"action":"drawCircle","x":420,"y":255,"radius":5,"color":"black"},
    {"action":"drawEllipse","x":400,"y":278,"radiusX":16,"radiusY":10,"color":"#e57373"},
    {"action":"drawCircle","x":400,"y":275,"radius":5,"color":"#c62828"},
    {"action":"drawArc","x":400,"y":295,"radius":12,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawLine","x1":345,"y1":370,"x2":340,"y2":420,"color":"pink"},
    {"action":"drawLine","x1":385,"y1":370,"x2":380,"y2":420,"color":"pink"},
    {"action":"drawLine","x1":415,"y1":370,"x2":420,"y2":420,"color":"pink"},
    {"action":"drawLine","x1":455,"y1":370,"x2":460,"y2":420,"color":"pink"},
  ]
},

"马": {
  "aliases": ["马","小马","马马","mǎ ma","pony"],
  "actions": [
    {"action":"drawEllipse","x":420,"y":330,"radiusX":90,"radiusY":50,"color":"#a1887f"},
    {"action":"drawEllipse","x":320,"y":260,"radiusX":55,"radiusY":42,"color":"#a1887f"},
    {"action":"drawPolygon","points":[{"x":270,"y":260},{"x":250,"y":270},{"x":270,"y":280}],"color":"#a1887f"},
    {"action":"drawCircle","x":295,"y":245,"radius":6,"color":"black"},
    {"action":"drawEllipse","x":285,"y":240,"radiusX":12,"radiusY":10,"color":"#a1887f"},
    {"action":"drawLine","x1":340,"y1":370,"x2":340,"y2":450,"color":"#a1887f"},
    {"action":"drawLine","x1":390,"y1":370,"x2":390,"y2":450,"color":"#a1887f"},
    {"action":"drawLine","x1":470,"y1":370,"x2":470,"y2":450,"color":"#a1887f"},
    {"action":"drawLine","x1":510,"y1":370,"x2":510,"y2":450,"color":"#a1887f"},
    {"action":"drawLine","x1":315,"y1":240,"x2":290,"y2":220,"color":"#a1887f"},
    {"action":"drawLine","x1":325,"y1":240,"x2":300,"y2":220,"color":"#a1887f"},
    {"action":"drawLine","x1":490,"y1":300,"x2":530,"y2":290,"color":"#a1887f"},
  ]
},

"羊": {
  "aliases": ["羊","羊羊","小羊","绵羊","咩咩","yáng yang"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":350,"radiusX":55,"radiusY":40,"color":"white"},
    {"action":"drawCircle","x":400,"y":270,"radius":35,"color":"white"},
    {"action":"drawCircle","x":365,"y":248,"radius":16,"color":"white"},
    {"action":"drawCircle","x":435,"y":248,"radius":16,"color":"white"},
    {"action":"drawCircle","x":365,"y":275,"radius":18,"color":"white"},
    {"action":"drawCircle","x":435,"y":275,"radius":18,"color":"white"},
    {"action":"drawCircle","x":390,"y":260,"radius":4,"color":"black"},
    {"action":"drawCircle","x":410,"y":260,"radius":4,"color":"black"},
    {"action":"drawEllipse","x":400,"y":275,"radiusX":8,"radiusY":6,"color":"pink"},
    {"action":"drawLine","x1":355,"y1":370,"x2":350,"y2":430,"color":"white"},
    {"action":"drawLine","x1":370,"y1":370,"x2":368,"y2":430,"color":"white"},
    {"action":"drawLine","x1":430,"y1":370,"x2":432,"y2":430,"color":"white"},
    {"action":"drawLine","x1":445,"y1":370,"x2":450,"y2":430,"color":"white"},
  ]
},

"老虎": {
  "aliases": ["老虎","虎虎","大老虎","lǎo hǔ","hǔ zi"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":340,"radiusX":75,"radiusY":55,"color":"orange"},
    {"action":"drawCircle","x":400,"y":250,"radius":50,"color":"orange"},
    {"action":"drawPolygon","points":[{"x":355,"y":220},{"x":370,"y":180},{"x":385,"y":215}],"color":"orange"},
    {"action":"drawPolygon","points":[{"x":445,"y":220},{"x":430,"y":180},{"x":415,"y":215}],"color":"orange"},
    {"action":"drawCircle","x":380,"y":240,"radius":7,"color":"black"},
    {"action":"drawCircle","x":420,"y":240,"radius":7,"color":"black"},
    {"action":"drawCircle","x":400,"y":258,"radius":12,"color":"pink"},
    {"action":"drawCircle","x":400,"y":255,"radius":6,"color":"#e57373"},
    {"action":"drawEllipse","x":400,"y":250,"radiusX":12,"radiusY":4,"color":"black"},
    {"action":"drawLine","x1":370,"y1":270,"x2":340,"y2":275,"color":"black"},
    {"action":"drawLine","x1":430,"y1":270,"x2":460,"y2":275,"color":"black"},
    {"action":"drawLine","x1":340,"y1":380,"x2":335,"y2":440,"color":"orange"},
    {"action":"drawLine","x1":460,"y1":380,"x2":465,"y2":440,"color":"orange"},
    {"action":"drawLine","x1":370,"y1":385,"x2":365,"y2":440,"color":"orange"},
    {"action":"drawLine","x1":430,"y1":385,"x2":435,"y2":440,"color":"orange"},
    {"action":"drawArc","x":440,"y":320,"radius":30,"startAngle":2,"endAngle":3.5,"color":"orange"},
  ]
},

"狮子": {
  "aliases": ["狮子","狮狮","大狮子","shī zi"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":340,"radiusX":70,"radiusY":55,"color":"#ffcc80"},
    {"action":"drawCircle","x":400,"y":250,"radius":45,"color":"#ffcc80"},
    {"action":"drawCircle","x":400,"y":250,"radius":55,"color":"#d4a574"},
    {"action":"drawPolygon","points":[{"x":350,"y":210},{"x":345,"y":185},{"x":365,"y":205}],"color":"#d4a574"},
    {"action":"drawPolygon","points":[{"x":450,"y":210},{"x":455,"y":185},{"x":435,"y":205}],"color":"#d4a574"},
    {"action":"drawCircle","x":380,"y":240,"radius":6,"color":"black"},
    {"action":"drawCircle","x":420,"y":240,"radius":6,"color":"black"},
    {"action":"drawCircle","x":400,"y":258,"radius":12,"color":"#e57373"},
    {"action":"drawLine","x1":360,"y1":268,"x2":340,"y2":272,"color":"black"},
    {"action":"drawLine","x1":440,"y1":268,"x2":460,"y2":272,"color":"black"},
    {"action":"drawLine","x1":340,"y1":380,"x2":335,"y2":440,"color":"#ffcc80"},
    {"action":"drawLine","x1":460,"y1":380,"x2":465,"y2":440,"color":"#ffcc80"},
    {"action":"drawLine","x1":370,"y1":385,"x2":368,"y2":440,"color":"#ffcc80"},
    {"action":"drawLine","x1":430,"y1":385,"x2":432,"y2":440,"color":"#ffcc80"},
    {"action":"drawCircle","x":455,"y":320,"radius":10,"color":"#d4a574"},
  ]
},

"猴子": {
  "aliases": ["猴子","猴猴","小猴","hóu zi","孙悟空"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":340,"radiusX":55,"radiusY":45,"color":"#a1887f"},
    {"action":"drawCircle","x":400,"y":260,"radius":40,"color":"#a1887f"},
    {"action":"drawEllipse","x":365,"y":235,"radiusX":16,"radiusY":14,"color":"#a1887f"},
    {"action":"drawEllipse","x":435,"y":235,"radiusX":16,"radiusY":14,"color":"#a1887f"},
    {"action":"drawCircle","x":380,"y":252,"radius":4,"color":"black"},
    {"action":"drawCircle","x":420,"y":252,"radius":4,"color":"black"},
    {"action":"drawCircle","x":400,"y":268,"radius":8,"color":"pink"},
    {"action":"drawArc","x":400,"y":280,"radius":10,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawArc","x":400,"y":275,"radius":12,"startAngle":3.14,"endAngle":6.28,"color":"black"},
    {"action":"drawLine","x1":350,"y1":340,"x2":290,"y2":310,"color":"#a1887f"},
    {"action":"drawLine","x1":450,"y1":340,"x2":510,"y2":310,"color":"#a1887f"},
    {"action":"drawLine","x1":290,"y1":310,"x2":280,"y2":360,"color":"#a1887f"},
    {"action":"drawLine","x1":510,"y1":310,"x2":520,"y2":360,"color":"#a1887f"},
    {"action":"drawLine","x1":370,"y1":380,"x2":365,"y2":440,"color":"#a1887f"},
    {"action":"drawLine","x1":430,"y1":380,"x2":435,"y2":440,"color":"#a1887f"},
    {"action":"drawLine","x1":395,"y1":260,"x2":350,"y2":210,"color":"#a1887f"},
    {"action":"drawLine","x1":405,"y1":260,"x2":450,"y2":210,"color":"#a1887f"},
  ]
},

"熊": {
  "aliases": ["熊","熊熊","小熊","大熊","xióng xióng"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":350,"radiusX":70,"radiusY":55,"color":"#a1887f"},
    {"action":"drawCircle","x":400,"y":250,"radius":50,"color":"#a1887f"},
    {"action":"drawCircle","x":360,"y":215,"radius":18,"color":"#a1887f"},
    {"action":"drawCircle","x":440,"y":215,"radius":18,"color":"#a1887f"},
    {"action":"drawCircle","x":360,"y":210,"radius":10,"color":"#8d6e63"},
    {"action":"drawCircle","x":440,"y":210,"radius":10,"color":"#8d6e63"},
    {"action":"drawCircle","x":380,"y":240,"radius":6,"color":"black"},
    {"action":"drawCircle","x":420,"y":240,"radius":6,"color":"black"},
    {"action":"drawCircle","x":400,"y":260,"radius":10,"color":"#8d6e63"},
    {"action":"drawArc","x":400,"y":278,"radius":12,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawLine","x1":340,"y1":380,"x2":335,"y2":440,"color":"#a1887f"},
    {"action":"drawLine","x1":370,"y1":380,"x2":365,"y2":440,"color":"#a1887f"},
    {"action":"drawLine","x1":430,"y1":380,"x2":435,"y2":440,"color":"#a1887f"},
    {"action":"drawLine","x1":460,"y1":380,"x2":465,"y2":440,"color":"#a1887f"},
  ]
},

"长颈鹿": {
  "aliases": ["长颈鹿","长颈鹿鹿","cháng jǐng lù","高高鹿"],
  "actions": [
    {"action":"drawEllipse","x":430,"y":420,"radiusX":50,"radiusY":35,"color":"#ffcc80"},
    {"action":"drawLine","x1":400,"y1":388,"x2":390,"y2":220,"color":"#ffcc80"},
    {"action":"drawLine","x1":410,"y1":388,"x2":420,"y2":220,"color":"#ffcc80"},
    {"action":"drawCircle","x":390,"y":190,"radius":28,"color":"#ffcc80"},
    {"action":"drawCircle","x":380,"y":182,"radius":5,"color":"black"},
    {"action":"drawCircle","x":400,"y":182,"radius":5,"color":"black"},
    {"action":"drawCircle","x":385,"y":195,"radius":4,"color":"brown"},
    {"action":"drawArc","x":390,"y":205,"radius":5,"startAngle":0,"endAngle":3.14,"color":"black"},
    {"action":"drawLine","x1":365,"y1":170,"x2":355,"y2":160,"color":"#ffcc80"},
    {"action":"drawLine","x1":415,"y1":170,"x2":425,"y2":160,"color":"#ffcc80"},
    {"action":"drawCircle","x":385,"y":275,"radius":6,"color":"#8d6e63"},
    {"action":"drawCircle","x":415,"y":275,"radius":6,"color":"#8d6e63"},
    {"action":"drawCircle","x":385,"y":325,"radius":6,"color":"#8d6e63"},
    {"action":"drawCircle","x":415,"y":325,"radius":6,"color":"#8d6e63"},
    {"action":"drawLine","x1":390,"y1":440,"x2":385,"y2":480,"color":"#ffcc80"},
    {"action":"drawLine","x1":410,"y1":440,"x2":415,"y2":480,"color":"#ffcc80"},
    {"action":"drawLine","x1":455,"y1":440,"x2":460,"y2":480,"color":"#ffcc80"},
    {"action":"drawLine","x1":475,"y1":440,"x2":480,"y2":480,"color":"#ffcc80"},
  ]
},

"企鹅": {
  "aliases": ["企鹅","企鹅鹅","小企鹅","qǐ é","南南"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":320,"radiusX":50,"radiusY":70,"color":"black"},
    {"action":"drawEllipse","x":400,"y":350,"radiusX":32,"radiusY":55,"color":"white"},
    {"action":"drawCircle","x":400,"y":240,"radius":35,"color":"black"},
    {"action":"drawCircle","x":400,"y":245,"radius":25,"color":"white"},
    {"action":"drawCircle","x":388,"y":238,"radius":5,"color":"black"},
    {"action":"drawCircle","x":412,"y":238,"radius":5,"color":"black"},
    {"action":"drawPolygon","points":[{"x":397,"y":248},{"x":400,"y":260},{"x":403,"y":248}],"color":"orange"},
    {"action":"drawLine","x1":355,"y1":380,"x2":350,"y2":410,"color":"orange"},
    {"action":"drawLine","x1":445,"y1":380,"x2":450,"y2":410,"color":"orange"},
    {"action":"drawLine","x1":370,"y1":270,"x2":350,"y2":290,"color":"black"},
    {"action":"drawLine","x1":430,"y1":270,"x2":450,"y2":290,"color":"black"},
  ]
},

"老鼠": {
  "aliases": ["老鼠","鼠鼠","小老鼠","lǎo shǔ","米奇"],
  "actions": [
    {"action":"drawEllipse","x":400,"y":330,"radiusX":50,"radiusY":38,"color":"#9e9e9e"},
    {"action":"drawCircle","x":400,"y":270,"radius":35,"color":"#9e9e9e"},
    {"action":"drawCircle","x":365,"y":245,"radius":18,"color":"#9e9e9e"},
    {"action":"drawCircle","x":435,"y":245,"radius":18,"color":"#9e9e9e"},
    {"action":"drawCircle","x":365,"y":240,"radius":12,"color":"pink"},
    {"action":"drawCircle","x":435,"y":240,"radius":12,"color":"pink"},
    {"action":"drawCircle","x":383,"y":262,"radius":4,"color":"black"},
    {"action":"drawCircle","x":417,"y":262,"radius":4,"color":"black"},
    {"action":"drawPolygon","points":[{"x":398,"y":280},{"x":400,"y":286},{"x":402,"y":280}],"color":"pink"},
    {"action":"drawLine","x1":390,"y1":285,"x2":380,"y2":292,"color":"black"},
    {"action":"drawLine","x1":410,"y1":285,"x2":420,"y2":292,"color":"black"},
    {"action":"drawArc","x":435,"y":320,"radius":30,"startAngle":5.5,"endAngle":6.28,"color":"#9e9e9e"},
    {"action":"drawLine","x1":358,"y1":360,"x2":352,"y2":410,"color":"#9e9e9e"},
    {"action":"drawLine","x1":442,"y1":360,"x2":448,"y2":410,"color":"#9e9e9e"},
  ]
},

"恐龙": {
  "aliases": ["恐龙","恐龙龙","小恐龙","kǒng lóng","dinosaur"],
  "actions": [
    {"action":"drawEllipse","x":380,"y":350,"radiusX":70,"radiusY":45,"color":"#66bb6a"},
    {"action":"drawCircle","x":300,"y":280,"radius":30,"color":"#66bb6a"},
    {"action":"drawPolygon","points":[{"x":440,"y":370},{"x":520,"y":340},{"x":500,"y":390}],"color":"#66bb6a"},
    {"action":"drawCircle","x":290,"y":272,"radius":5,"color":"black"},
    {"action":"drawPolygon","points":[{"x":295,"y":260},{"x":280,"y":250},{"x":305,"y":255}],"color":"#66bb6a"},
    {"action":"drawLine","x1":340,"y1":390,"x2":338,"y2":450,"color":"#66bb6a"},
    {"action":"drawLine","x1":370,"y1":390,"x2":368,"y2":450,"color":"#66bb6a"},
    {"action":"drawLine","x1":410,"y1":390,"x2":412,"y2":450,"color":"#66bb6a"},
    {"action":"drawLine","x1":440,"y1":390,"x2":445,"y2":450,"color":"#66bb6a"},
    {"action":"drawPolygon","points":[{"x":320,"y":310},{"x":305,"y":315},{"x":315,"y":320}],"color":"#388e3c"},
    {"action":"drawPolygon","points":[{"x":340,"y":315},{"x":325,"y":320},{"x":335,"y":325}],"color":"#388e3c"},
    {"action":"drawPolygon","points":[{"x":360,"y":318},{"x":345,"y":323},{"x":355,"y":328}],"color":"#388e3c"},
  ]
},

# ═══ 自然 ═══

"云": {
  "aliases": ["云","云朵","白云","云云","yún yun"],
  "actions": [
    {"action":"drawCircle","x":350,"y":280,"radius":40,"color":"white"},
    {"action":"drawCircle","x":410,"y":260,"radius":50,"color":"white"},
    {"action":"drawCircle","x":470,"y":290,"radius":40,"color":"white"},
    {"action":"drawCircle","x":310,"y":305,"radius":30,"color":"white"},
    {"action":"drawCircle","x":490,"y":310,"radius":30,"color":"white"},
    {"action":"drawCircle","x":380,"y":300,"radius":45,"color":"white"},
    {"action":"drawCircle","x":440,"y":310,"radius":38,"color":"white"},
  ]
},

"彩虹": {
  "aliases": ["彩虹","彩虹虹","cǎi hóng","虹","七彩虹"],
  "actions": [
    {"action":"drawArc","x":400,"y":350,"radius":180,"startAngle":3.14,"endAngle":6.28,"color":"red"},
    {"action":"drawArc","x":400,"y":350,"radius":168,"startAngle":3.14,"endAngle":6.28,"color":"orange"},
    {"action":"drawArc","x":400,"y":350,"radius":156,"startAngle":3.14,"endAngle":6.28,"color":"yellow"},
    {"action":"drawArc","x":400,"y":350,"radius":144,"startAngle":3.14,"endAngle":6.28,"color":"green"},
    {"action":"drawArc","x":400,"y":350,"radius":132,"startAngle":3.14,"endAngle":6.28,"color":"blue"},
    {"action":"drawArc","x":400,"y":350,"radius":120,"startAngle":3.14,"endAngle":6.28,"color":"purple"},
    {"action":"drawArc","x":400,"y":350,"radius":108,"startAngle":3.14,"endAngle":6.28,"color":"pink"},
  ]
},

"花（重写）": {
  "aliases": ["花","花朵","花花","小花","鲜花","huā hua"],
  "actions": [
    {"action":"drawCircle","x":400,"y":320,"radius":12,"color":"#ffeb3b"},
    {"action":"drawCircle","x":400,"y":272,"radius":22,"color":"#e91e63"},
    {"action":"drawCircle","x":432,"y":300,"radius":22,"color":"#e91e63"},
    {"action":"drawCircle","x":420,"y":338,"radius":22,"color":"#e91e63"},
    {"action":"drawCircle","x":380,"y":338,"radius":22,"color":"#e91e63"},
    {"action":"drawCircle","x":368,"y":300,"radius":22,"color":"#e91e63"},
    {"action":"drawLine","x1":400,"y1":340,"x2":400,"y2":420,"color":"#4caf50"},
    {"action":"drawEllipse","x":380,"y":410,"radiusX":20,"radiusY":10,"color":"#4caf50"},
    {"action":"drawEllipse","x":420,"y":415,"radiusX":18,"radiusY":8,"color":"#4caf50"},
  ]
},

"西瓜": {
  "aliases": ["西瓜","西呱","瓜瓜","西瓜瓜","xī guā"],
  "actions": [
    {"action":"drawArc","x":400,"y":350,"radius":100,"startAngle":0,"endAngle":3.14,"color":"#4caf50"},
    {"action":"drawArc","x":400,"y":350,"radius":95,"startAngle":0,"endAngle":3.14,"color":"red"},
    {"action":"drawArc","x":400,"y":350,"radius":90,"startAngle":0,"endAngle":3.14,"color":"#e57373"},
    {"action":"drawArc","x":400,"y":350,"radius":85,"startAngle":0,"endAngle":3.14,"color":"#ef5350"},
    {"action":"drawCircle","x":350,"y":310,"radius":6,"color":"black"},
    {"action":"drawCircle","x":380,"y":295,"radius":5,"color":"black"},
    {"action":"drawCircle","x":420,"y":290,"radius":7,"color":"black"},
    {"action":"drawCircle","x":450,"y":310,"radius":5,"color":"black"},
    {"action":"drawCircle","x":400,"y":275,"radius":6,"color":"black"},
    {"action":"drawCircle","x":365,"y":330,"radius":4,"color":"black"},
    {"action":"drawCircle","x":435,"y": 335,"radius":5,"color":"black"},
  ]
},

"草莓": {
  "aliases": ["草莓","莓莓","cǎo méi","草莓莓","红莓"],
  "actions": [
    {"action":"drawPolygon","points":[{"x":400,"y":270},{"x":360,"y":310},{"x":365,"y":350},{"x":435,"y":350},{"x":440,"y":310}],"color":"#e53935"},
    {"action":"drawCircle","x":380,"y":310,"radius":4,"color":"#ffcdd2"},
    {"action":"drawCircle","x": 416,"y":305,"radius":3,"color":"#ffcdd2"},
    {"action":"drawCircle","x":395,"y":330,"radius":4,"color":"#ffcdd2"},
    {"action":"drawCircle","x":418,"y":335,"radius":3,"color":"#ffcdd2"},
    {"action":"drawCircle","x":408,"y":318,"radius":4,"color":"#ffcdd2"},
    {"action":"drawEllipse","x":400,"y":268,"radiusX":12,"radiusY":6,"color":"#4caf50"},
    {"action":"drawLine","x1":400,"y1": 268,"x2": 390,"y2": 258,"color":"#4caf50"},
    {"action":"drawLine","x1":400,"y1": 268,"x2": 410,"y2": 258,"color":"#4caf50"},
  ]
},

"蘑菇": {
  "aliases": ["蘑菇","菇菇","mó gū","小蘑菇","伞伞"],
  "actions": [
    {"action":"drawArc","x":400,"y":320,"radius":55,"startAngle":0,"endAngle":3.14,"color":"#e57373"},
    {"action":"drawArc","x":400,"y":320,"radius":50,"startAngle":0,"endAngle":3.14,"color":"#ef5350"},
    {"action":"drawLine","x1":385,"y1":320,"x2":380,"y2":420,"color":"#f5f5f5"},
    {"action":"drawLine","x1":415,"y1":320,"x2":420,"y2":420,"color":"#f5f5f5"},
    {"action":"drawRect","x":380,"y":405,"width":40,"height":15,"color":"#f5f5f5"},
    {"action":"drawCircle","x":370,"y":285,"radius":8,"color":"white"},
    {"action":"drawCircle","x":410,"y":270,"radius":10,"color":"white"},
    {"action":"drawCircle","x":435,"y":292,"radius":7,"color":"white"},
    {"action":"drawCircle","x":390,"y":300,"radius":5,"color":"white"},
  ]
},

"葡萄": {
  "aliases": ["葡萄","葡葡","萄萄","pú tao","紫葡萄"],
  "actions": [
    {"action":"drawCircle","x":390,"y":300,"radius":18,"color":"#7b1fa2"},
    {"action":"drawCircle","x":420,"y":298,"radius":18,"color":"#7b1fa2"},
    {"action":"drawCircle","x":375,"y":332,"radius":18,"color":"#7b1fa2"},
    {"action":"drawCircle","x":405,"y":330,"radius":18,"color":"#7b1fa2"},
    {"action":"drawCircle","x":435,"y":328,"radius":18,"color":"#7b1fa2"},
    {"action":"drawCircle","x":390,"y":358,"radius":18,"color":"#7b1fa2"},
    {"action":"drawCircle","x":420,"y":356,"radius":18,"color":"#7b1fa2"},
    {"action":"drawLine","x1":405,"y1":282,"x2":405,"y2":255,"color":"#4caf50"},
    {"action":"drawEllipse","x":413,"y":252,"radiusX":12,"radiusY":6,"color":"#4caf50"},
    {"action":"drawLine","x1":418,"y1":252,"x2":430,"y2":245,"color":"#4caf50"},
  ]
},

"雪花": {
  "aliases": ["雪花","雪雪","xuě huā","六角花"],
  "actions": [
    {"action":"drawLine","x1":400,"y1":200,"x2":400,"y2":400,"color":"#90caf9"},
    {"action":"drawLine","x1":260,"y1":300,"x2":540,"y2":300,"color":"#90caf9"},
    {"action":"drawLine","x1":300,"y1": 235,"x2":500,"y2":365,"color":"#90caf9"},
    {"action":"drawLine","x1":500,"y1": 235,"x2":300,"y2":365,"color":"#90caf9"},
    {"action":"drawLine","x1":400,"y1":200,"x2":380,"y2":240,"color":"#90caf9"},
    {"action":"drawLine","x1":400,"y1":200,"x2":420,"y2":240,"color":"#90caf9"},
    {"action":"drawLine","x1":260,"y1":300,"x2":300,"y2":290,"color":"#90caf9"},
    {"action":"drawLine","x1":260,"y1":300,"x2":300,"y2":310,"color":"#90caf9"},
    {"action":"drawLine","x1":540,"y1":300,"x2":500,"y2":290,"color":"#90caf9"},
    {"action":"drawLine","x1":540,"y1":300,"x2":500,"y2":310,"color":"#90caf9"},
    {"action":"drawLine","x1":300,"y1": 235,"x2":320,"y2":265,"color":"#90caf9"},
    {"action":"drawLine","x1":300,"y1": 235,"x2":280,"y2":255,"color":"#90caf9"},
    {"action":"drawLine","x1":500,"y1": 235,"x2":480,"y2":265,"color":"#90caf9"},
    {"action":"drawLine","x1":500,"y1": 235,"x2":520,"y2":255,"color":"#90caf9"},
    {"action":"drawLine","x1":300,"y1":365,"x2":320,"y2":340,"color":"#90caf9"},
    {"action":"drawLine","x1":300,"y1":365,"x2":280,"y2":350,"color":"#90caf9"},
    {"action":"drawLine","x1":500,"y1":365,"x2":480,"y2":340,"color":"#90caf9"},
    {"action":"drawLine","x1":500,"y1":365,"x2":520,"y2":350,"color":"#90caf9"},
  ]
},

}

# ═══ 应用 ═══

for name, tpl in HANDMADE.items():
    key = name.replace("（重写）", "")
    shapes[key] = tpl
    print(f"  + {key} ({len(tpl['actions'])} actions)")

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n完成！共写入 {len(HANDMADE)} 个手写模板")
