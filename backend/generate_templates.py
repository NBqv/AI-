"""
一键生成儿童简笔画模板库 -> aliases.json

使用方法：
  1. set DASHSCOPE_API_KEY=sk-xxx            (Windows)
  2. python backend/generate_templates.py

输出会合并到 backend/aliases.json 的 complex_shapes 字段中。
"""

import json, os, sys, time, re
from pathlib import Path

# -- 配置 --
API_KEY = os.environ.get("DASHSCOPE_API_KEY", "")
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
MODEL = "qwen-plus"
ALIASES_PATH = Path(__file__).parent / "aliases.json"

# -- 分类模板列表（按优先级分批生成） --

BATCHES = [
    {
        "name": "动物_上",
        "items": [
            ("猫", "猫的简笔画：圆脸+尖耳朵+眼睛胡须+身体+尾巴"),
            ("狗", "狗的简笔画：圆头+垂耳或立耳+眼睛鼻子+身体+短尾巴"),
            ("兔子", "兔子的简笔画：圆头+长耳朵+圆眼睛+小身体+短尾巴"),
            ("鸡", "鸡的简笔画：圆身体+尖嘴+鸡冠+眼睛+翅膀+脚"),
            ("鸭", "鸭的简笔画：椭圆身体+扁嘴+圆眼睛+翅膀+脚"),
            ("鱼", "鱼的简笔画：椭圆身体+三角尾巴+圆眼睛+鱼鳍"),
            ("鸟", "鸟的简笔画：椭圆身体+小圆头+尖嘴+翅膀+尾巴+脚"),
            ("老鼠", "老鼠的简笔画：圆头+大圆耳朵+小眼睛+胡须+长尾巴"),
            ("牛", "牛的简笔画：大椭圆身体+圆头+角+眼睛+鼻子+四条腿+尾巴"),
            ("猪", "猪的简笔画：圆身体+圆头+大鼻子+小眼睛+短腿+卷尾巴"),
            ("马", "马的简笔画：长椭圆身体+长头+鬃毛+眼睛+四条长腿+尾巴"),
            ("羊", "羊的简笔画：椭圆身体+圆头+卷毛+角+眼睛+四条腿"),
        ]
    },
    {
        "name": "动物_下",
        "items": [
            ("大象", "大象的简笔画：大椭圆身体+大头+长鼻子+大耳朵+眼睛+四条粗腿+小尾巴"),
            ("老虎", "老虎的简笔画：椭圆身体+圆头+额头王字+耳朵+眼睛+胡须+四条腿+长尾巴"),
            ("狮子", "狮子的简笔画：椭圆身体+大圆头+鬃毛+眼睛+鼻子+四条腿+尾巴"),
            ("熊猫", "熊猫的简笔画：圆身体+圆头+黑眼圈+圆耳朵+黑色四肢+白色肚子"),
            ("猴子", "猴子的简笔画：椭圆身体+圆头+圆耳朵+眼睛+长手臂+长尾巴"),
            ("熊", "熊的简笔画：大圆身体+圆头+小圆耳朵+眼睛+圆鼻子+四条短腿"),
            ("长颈鹿", "长颈鹿的简笔画：椭圆身体+长脖子+小头+角+眼睛+四条长腿+尾巴"),
            ("企鹅", "企鹅的简笔画：椭圆身体+黑色背部+白色肚子+小圆头+尖嘴+翅膀+脚"),
            ("蜗牛", "蜗牛的简笔画：螺旋壳+软身体+触角+小眼睛"),
            ("蝴蝶", "蝴蝶的简笔画：细身体+两对大翅膀（多边形）+触角"),
            ("青蛙", "青蛙的简笔画：椭圆身体+大圆眼睛+宽嘴巴+四条腿"),
            ("乌龟", "乌龟的简笔画：半圆壳+小头+眼睛+四条短腿+小尾巴"),
            ("蜜蜂", "蜜蜂的简笔画：椭圆身体+黄色黑色条纹+小翅膀+触角"),
            ("蛇", "蛇的简笔画：波浪曲线+头+眼睛+分叉舌头"),
        ]
    },
    {
        "name": "食物",
        "items": [
            ("苹果", "苹果的简笔画：圆形+顶部小茎+叶子"),
            ("香蕉", "香蕉的简笔画：弯曲长椭圆+两端棕色"),
            ("西瓜", "西瓜的简笔画：半圆形+绿色外皮+红色果肉+黑色种子"),
            ("草莓", "草莓的简笔画：倒三角形+红色+绿色叶子+小点"),
            ("橙子", "橙子的简笔画：圆形+橙色+小点表面+顶部小茎"),
            ("冰淇淋", "冰淇淋的简笔画：圆形雪球+三角形蛋筒+奶油装饰"),
            ("棒棒糖", "棒棒糖的简笔画：大圆形+螺旋纹+细棍"),
            ("蛋糕", "蛋糕的简笔画：梯形+多层+奶油+顶部樱桃"),
            ("饼干", "饼干的简笔画：圆形+小圆点（巧克力豆）"),
            ("鸡蛋", "鸡蛋的简笔画：椭圆形"),
            ("面包", "面包的简笔画：半圆形（吐司形状）+弧线"),
            ("糖葫芦", "糖葫芦的简笔画：竖线+多个红色小圆串在上面"),
            ("玉米", "玉米的简笔画：长椭圆+格子纹+顶部叶子+底部棒"),
            ("葡萄", "葡萄的简笔画：一串小圆+顶部叶子+茎"),
        ]
    },
    {
        "name": "交通工具",
        "items": [
            ("小汽车", "小汽车的简笔画：矩形车身+梯形车窗+两个圆形车轮"),
            ("火车", "火车的简笔画：多个矩形车厢相连+圆形车轮+烟囱+冒烟"),
            ("飞机", "飞机的简笔画：长椭圆机身+三角形机翼+尾翼+小圆窗"),
            ("轮船", "轮船的简笔画：梯形船身+矩形上层+圆形舷窗+旗帜"),
            ("自行车", "自行车的简笔画：两个圆形车轮+三角形车架+车把+座椅"),
            ("公交车", "公交车的简笔画：大矩形车身+方形车窗+两个圆形车轮+车门"),
            ("消防车", "消防车的简笔画：红色矩形车身+梯形车窗+车轮+云梯"),
            ("挖掘机", "挖掘机的简笔画：矩形车身+圆形履带+驾驶室+长臂+挖斗"),
            ("火箭", "火箭的简笔画：长三角形机身+圆形舷窗+尾翼+火焰"),
            ("直升机", "直升机的简笔画：椭圆机身+顶部旋转翼+尾部小旋翼+窗户"),
            ("救护车", "救护车的简笔画：白色矩形车身+红十字+车窗+车轮"),
            ("卡车", "卡车的简笔画：车头+大矩形货箱+圆形车轮"),
        ]
    },
    {
        "name": "自然",
        "items": [
            ("太阳", "太阳的简笔画：大圆形+周围射线"),
            ("月亮", "月亮（弯月）的简笔画：弯月形状"),
            ("星星", "星星（五角星）的简笔画：五角星"),
            ("云", "云的简笔画：多个相连的圆弧组成云朵形状"),
            ("彩虹", "彩虹的简笔画：七条彩色弧线+两端有云"),
            ("山", "山的简笔画：三角形/锯齿形山峰"),
            ("花", "花的简笔画：圆形花心+多个花瓣+茎+叶子"),
            ("树", "树的简笔画：棕色树干+绿色树冠圆形"),
            ("雪花", "雪花的简笔画：六角形星形+分支"),
            ("雨", "雨的简笔画：多条斜线+云"),
            ("雪人", "雪人的简笔画：三个大小圆堆叠+帽子+眼睛+鼻子+围巾"),
            ("火山", "火山的简笔画：三角形山体+顶部红色岩浆+烟"),
            ("草地", "草的简笔画：多条从底部向上的曲线+绿色"),
            ("蘑菇", "蘑菇的简笔画：半圆伞盖+矩形柄+斑点"),
        ]
    },
    {
        "name": "日常物品",
        "items": [
            ("房子", "房子的简笔画：矩形墙壁+三角形屋顶+矩形门+圆形把手+方形窗户"),
            ("气球", "气球的简笔画：椭圆球+细线+打结"),
            ("旗子", "旗子的简笔画：竖线旗杆+矩形或三角形旗帜"),
            ("雨伞", "雨伞的简笔画：半圆伞面+弯手柄"),
            ("钟表", "钟表的简笔画：圆形表盘+数字或刻度+时针分针"),
            ("椅子", "椅子的简笔画：矩形坐垫+四条腿+靠背"),
            ("桌子", "桌子的简笔画：矩形桌面+四条腿"),
            ("床", "床的简笔画：矩形床体+枕头+被子"),
            ("门", "门的简笔画：竖矩形+圆形把手"),
            ("窗户", "窗户的简笔画：方形+十字窗框"),
            ("书", "书的简笔画：矩形+书脊+页面"),
            ("铅笔", "铅笔的简笔画：长六边形笔身+圆锥笔尖+橡皮"),
            ("碗", "碗的简笔画：半圆形+底部"),
            ("杯子", "杯子的简笔画：矩形杯身+半圆把手"),
            ("勺子", "勺子的简笔画：椭圆勺头+长柄"),
            ("电话", "电话的简笔画：矩形机身+圆形听筒+按钮"),
            ("灯", "灯的简笔画：三角形灯罩+细灯柱+矩形底座"),
            ("钥匙", "钥匙的简笔画：圆形头+细长杆+齿"),
            ("剪刀", "剪刀的简笔画：两个椭圆手柄+交叉刀片"),
            ("书包", "书包的简笔画：矩形包体+翻盖+背带"),
        ]
    },
    {
        "name": "人物_表情",
        "items": [
            ("笑脸", "笑脸的简笔画：黄色圆形+两个黑眼睛+弯弯的嘴巴弧线"),
            ("哭脸", "哭脸的简笔画：黄色圆形+两个黑眼睛+下弯嘴巴+眼泪"),
            ("生气脸", "生气脸的简笔画：红色圆形+倒八字眉毛+小眼睛+下弯嘴巴"),
            ("惊讶脸", "惊讶脸的简笔画：黄色圆形+大圆眼睛+O形嘴巴"),
            ("爸爸", "爸爸的简笔画：圆头+头发+眼镜+笑脸+身体+手臂+腿"),
            ("妈妈", "妈妈的简笔画：圆头+长发+笑脸+裙子+手臂+腿"),
            ("宝宝", "宝宝的简笔画：大圆头+小身体+眼睛+小嘴巴+手臂+腿"),
            ("男孩", "男孩的简笔画：圆头+短头发+眼睛+笑脸+身体+手臂+腿+衣服"),
            ("女孩", "女孩的简笔画：圆头+辫子或长发+眼睛+笑脸+裙子+手臂+腿"),
            ("爷爷", "爷爷的简笔画：圆头+白头发+胡子+眼镜+笑脸+拐杖"),
            ("奶奶", "奶奶的简笔画：圆头+白发+眼镜+笑脸+围裙"),
        ]
    },
    {
        "name": "其他",
        "items": [
            ("恐龙", "恐龙的简笔画：椭圆身体+长尾巴+小头+牙齿+四条腿+背上三角板"),
            ("圣诞树", "圣诞树的简笔画：三角形树+树干+星星+装饰球"),
            ("礼物", "礼物的简笔画：矩形盒子+十字丝带+蝴蝶结"),
            ("城堡", "城堡的简笔画：矩形主体+顶部城垛+塔楼+门+窗户"),
            ("机器人", "机器人的简笔画：方形头+天线+矩形身体+方形手臂+腿"),
            ("爱心", "爱心的简笔画：两个半圆+倒三角形组合成心形"),
            ("球", "球的简笔画：圆形+弧线装饰"),
            ("帐篷", "帐篷的简笔画：三角形+矩形底+顶部小旗"),
            ("风筝", "风筝的简笔画：菱形+尾巴+线"),
            ("糖果", "糖果的简笔画：小椭圆+两端三角形包装纸"),
            ("王冠", "王冠的简笔画：弧形底+三个尖顶+宝石"),
            ("望远镜", "望远镜的简笔画：两个相连的圆筒+矩形机身"),
            ("相机", "相机的简笔画：矩形机身+圆形镜头+闪光灯"),
            ("吉他", "吉他的简笔画：8字形琴身+长琴颈+弦"),
            ("鱼缸", "鱼缸的简笔画：梯形或矩形+水线+鱼+水草"),
        ]
    },
    {
        "name": "玩具游乐",
        "items": [
            ("滑梯", "滑梯的简笔画：梯子+斜坡滑道+支柱"),
            ("秋千", "秋千的简笔画：三角形支架+两条绳子+矩形坐板"),
            ("木马", "木马的简笔画：马头+弧形底座+把手+尾巴"),
            ("积木", "积木的简笔画：几个大小不同的矩形方块堆叠"),
            ("皮球", "皮球的简笔画：圆形+弧线装饰条纹"),
            ("泡泡机", "泡泡机的简笔画：矩形机身+圆形出泡口+几个飘着的泡泡"),
        ]
    },
    {
        "name": "乐器",
        "items": [
            ("鼓", "鼓的简笔画：圆柱形鼓身+两个鼓面+鼓棒"),
            ("喇叭", "喇叭的简笔画：梯形喇叭口+细管+吹口"),
            ("钢琴", "钢琴的简笔画：矩形琴身+黑白琴键+琴腿"),
        ]
    },
    {
        "name": "蔬菜",
        "items": [
            ("胡萝卜", "胡萝卜的简笔画：长锥形橙色+顶部绿色叶子"),
            ("西兰花", "西兰花的简笔画：绿色圆形花簇+浅绿色茎"),
            ("番茄", "番茄的简笔画：圆形红色+顶部绿色小蒂"),
            ("黄瓜", "黄瓜的简笔画：长椭圆形绿色+表面小点"),
            ("豌豆", "豌豆的简笔画：绿色豆荚+里面的圆形豆子"),
        ]
    },
    {
        "name": "服饰",
        "items": [
            ("连衣裙", "连衣裙的简笔画：上衣+裙摆+袖子+领口"),
            ("围巾", "围巾的简笔画：长条矩形+流苏"),
            ("手套", "手套的简笔画：手掌形状+五个手指+袖口"),
        ]
    },
    {
        "name": "身体部位",
        "items": [
            ("眼睛", "眼睛的简笔画：眼白+黑色瞳孔+上睫毛+眉毛"),
            ("鼻子", "鼻子的简笔画：小三角形或弧形+两个鼻孔"),
            ("嘴巴", "嘴巴的简笔画：微笑弧形+嘴唇"),
            ("耳朵", "耳朵的简笔画：半圆形耳廓+内部线条"),
            ("手", "手的简笔画：手掌+五个手指"),
            ("脚", "脚的简笔画：脚掌+五个脚趾"),
        ]
    },
    {
        "name": "节日季节",
        "items": [
            ("鞭炮", "鞭炮的简笔画：圆柱形红色炮身+引线+爆炸效果"),
            ("灯笼", "灯笼的简笔画：椭圆形红色+上下金色装饰+流苏"),
            ("南瓜灯", "南瓜灯的简笔画：圆形南瓜+眼睛嘴巴镂空+茎"),
            ("幽灵", "幽灵的简笔画：白色波浪形身体+两个黑眼睛"),
        ]
    },
    {
        "name": "昆虫",
        "items": [
            ("蚂蚁", "蚂蚁的简笔画：三个相连椭圆（头胸腹）+六条腿+触角"),
            ("蜻蜓", "蜻蜓的简笔画：细长身体+两对透明翅膀+大眼睛"),
            ("瓢虫", "瓢虫的简笔画：半圆红色身体+黑色斑点+小头+腿"),
            ("萤火虫", "萤火虫的简笔画：椭圆身体+翅膀+尾部发光+触角"),
        ]
    },
    {
        "name": "建筑场所",
        "items": [
            ("学校", "学校的简笔画：矩形主体建筑+窗户+门+屋顶+旗帜"),
            ("医院", "医院的简笔画：矩形建筑+窗户+红十字+门"),
            ("超市", "超市的简笔画：矩形大建筑+门+窗户+招牌"),
        ]
    },
    {
        "name": "职业",
        "items": [
            ("医生", "医生的简笔画：人物+白大褂+听诊器+帽子"),
            ("警察", "警察的简笔画：人物+制服+帽子+徽章+敬礼"),
            ("厨师", "厨师的简笔画：人物+厨师帽+围裙+锅铲"),
        ]
    },
    {
        "name": "数字字母",
        "items": [
            ("数字123", "数字123的简笔画：三个数字1、2、3连在一起"),
            ("字母ABC", "字母ABC的简笔画：三个字母A、B、C连在一起"),
        ]
    },
    {
        "name": "自然现象",
        "items": [
            ("闪电", "闪电的简笔画：锯齿形闪电从云中劈下"),
            ("风", "风的简笔画：几条弧形螺旋线表示风吹"),
        ]
    },
    {
        "name": "家庭扩展",
        "items": [
            ("哥哥", "哥哥的简笔画：男孩形象+短发+衣服+笑脸"),
            ("姐姐", "姐姐的简笔画：女孩形象+长发+裙子+笑脸"),
        ]
    },
    {
        "name": "其他补充",
        "items": [
            ("树叶", "树叶的简笔画：椭圆形叶片+叶脉+叶柄"),
            ("石头", "石头的简笔画：不规则圆形+灰色+阴影线条"),
        ]
    },
]

# -- 系统提示词 --

def build_system_prompt():
    return """你是儿童简笔画设计师。为每个主题生成画布坐标精确的简笔画。

画布: 800x600. 坐标参考: 左上(50,50) 右下(750,550) 中心(400,300)

输出格式必须是严格的JSON数组（纯JSON, 不要markdown, 不要额外文字）:
[
  {
    "name": "主题名",
    "aliases": ["名称","常见儿童叫法","发音变体","叠词"],
    "actions": [
      {"action":"drawCircle","x":400,"y":300,"radius":N,"color":"red"},
      {"action":"drawRect","x":N,"y":N,"width":N,"height":N,"color":"blue"},
      {"action":"drawEllipse","x":N,"y":N,"radiusX":N,"radiusY":N,"color":"green"},
      {"action":"drawLine","x1":N,"y1":N,"x2":N,"y2":N,"color":"black"},
      {"action":"drawPolygon","points":[{"x":N,"y":N},...],"color":"orange"},
      {"action":"drawArc","x":N,"y":N,"radius":N,"startAngle":N,"endAngle":N,"color":"black"}
    ]
  },
  ...
]

注意事项：
1. aliases 要包含：中文名称、儿童常说的叠词（猫猫、狗狗、兔兔、车车）、常见发音变体、可能的错误发音
2. 所有坐标必须在画布 800x600 范围内，图形居中放置
3. 图形要简洁可爱，适合2-4岁儿童认知水平
4. 颜色用: red红 blue蓝 green绿 yellow黄 black黑 white白 orange橙 purple紫 pink粉 brown棕 gold金
5. 每个图形的actions通常5-15个，不要过于复杂
6. 相互参照：如果画面上有多个元素（如人脸+五官），注意它们之间的相对位置

只输出JSON数组，不要有任何其他文字。"""


# -- API 调用 --

def call_qwen(items, batch_name):
    """调用千问API生成一批模板"""
    import urllib.request
    import ssl

    if not API_KEY:
        print("[ERROR] 未设置 DASHSCOPE_API_KEY 环境变量")
        sys.exit(1)

    # 构建用户消息
    lines = []
    for name, desc in items:
        lines.append(f"- {name}：{desc}")
    user_prompt = "请为以下主题生成儿童简笔画模板（每个包含aliases和actions）：\n\n" + "\n".join(lines)
    user_prompt += "\n\n注意：每个主题的aliases要包含儿童常用叫法和叠词（猫猫、狗狗、兔兔、车车等）。"

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 4096,
    }

    body = json.dumps(payload).encode("utf-8")
    url = f"{BASE_URL}/chat/completions"

    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    # 禁用SSL验证（Windows常见问题）
    ctx = ssl._create_unverified_context()

    print(f"  [WAIT] 请求中...", end="", flush=True)
    try:
        resp = urllib.request.urlopen(req, timeout=120, context=ctx)
        result = json.loads(resp.read().decode("utf-8"))
        content = result["choices"][0]["message"]["content"]
        print(" [OK]")
        return content
    except Exception as e:
        print(f" [FAIL] {e}")
        return None


def try_repair_json(text):
    """尝试修复常见JSON问题"""
    import re, math
    # 把 Math.PI 表达式替换为具体数值
    def replace_math_pi(m):
        expr = m.group(0)
        simplified = expr.replace("Math.PI", "3.14159")
        try:
            result = eval(simplified, {"__builtins__": {}}, {})
            return str(result)
        except:
            return simplified
    text = re.sub(r'[\d.]*(?:\s*\*\s*)?Math\.PI(?:\s*[*/]\s*[\d.]+)?', replace_math_pi, text)
    # 去掉尾随逗号（在 } 或 ] 前的逗号）
    text = re.sub(r",\s*([}\]])", r"\1", text)
    # 把单引号键名换成双引号
    text = re.sub(r"\{\s*'([^']+?)'\s*:", r'{"\1":', text)
    text = re.sub(r",\s*'([^']+?)'\s*:", r',"\1":', text)
    # 把单引号字符串值换成双引号
    text = re.sub(r":\s*'([^']*?)'\s*([,\]})])", r': "\1"\2', text)
    # 去掉注释
    text = re.sub(r"//[^\n]*", "", text)
    return text


def parse_result(content):
    """从API响应中提取JSON"""
    if not content:
        return []
    # 去掉 markdown 代码块
    text = content.strip()
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    # 找第一个 [ 和最后一个 ]
    start = text.find("[")
    end = text.rfind("]")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    # 尝试解析
    for attempt in range(2):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            if attempt == 0:
                text = try_repair_json(text)
            else:
                # 尝试逐对象解析：如果外层是数组但某个元素有问题，逐个提取
                try:
                    # 尝试用更宽松的方式：每个对象单独解析
                    objects = re.findall(r'\{[^{}]*\}', text)
                    result = []
                    for obj_str in objects:
                        try:
                            obj = json.loads(obj_str)
                            result.append(obj)
                        except json.JSONDecodeError:
                            try:
                                obj = json.loads(try_repair_json(obj_str))
                                result.append(obj)
                            except json.JSONDecodeError:
                                pass
                    if result:
                        return result
                except Exception:
                    pass
                print(f"    [WARN] JSON解析失败")
                debug_path = Path(__file__).parent / f"_debug_{int(time.time())}.txt"
                debug_path.write_text(content, encoding="utf-8")
                print(f"    [SAVED] 原始内容已保存到 {debug_path.name}")
                return []
    return []


def merge_into_aliases(new_templates):
    """将生成的模板合并到 aliases.json 的 complex_shapes 中"""
    if not ALIASES_PATH.exists():
        print(f"[ERROR] 未找到 {ALIASES_PATH}")
        return

    with open(ALIASES_PATH, "r", encoding="utf-8") as f:
        aliases = json.load(f)

    if "complex_shapes" not in aliases:
        aliases["complex_shapes"] = {}

    existing = set(aliases["complex_shapes"].keys())
    added = 0
    skipped = 0

    for tpl in new_templates:
        name = tpl.get("name", "")
        if not name:
            continue
        if name in existing:
            print(f"  [SKIP] [{name}] 已存在，跳过")
            skipped += 1
            continue

        alias_list = tpl.get("aliases", [])
        actions = tpl.get("actions", [])

        # 验证坐标合法性
        valid_actions = []
        for a in actions:
            action = a.get("action", "")
            if action in ("drawCircle", "drawEllipse", "drawArc", "drawRect", "drawLine", "drawPolygon", "drawTriangle", "drawStar", "drawOval"):
                # Normalize: map triangle/star/oval to polygon/ellipse by renaming action
                if action == "drawTriangle" or action == "drawStar":
                    pass  # frontend handles these directly
                if action == "drawOval":
                    a["action"] = "drawEllipse"
                valid_actions.append(a)
            else:
                print(f"    [WARN] [{name}] 忽略未知action: {action}")

        if not valid_actions:
            print(f"  [WARN] [{name}] 没有有效action，跳过")
            skipped += 1
            continue

        aliases["complex_shapes"][name] = {
            "aliases": alias_list,
            "actions": valid_actions,
        }
        print(f"  [ADD] [{name}] {len(valid_actions)}个动作")
        added += 1

    # 写回文件
    with open(ALIASES_PATH, "w", encoding="utf-8") as f:
        json.dump(aliases, f, ensure_ascii=False, indent=2)

    print(f"\n[STATS] 新增 {added} 个, 跳过 {skipped} 个, 现有共 {len(aliases['complex_shapes'])} 个模板")
    return added


# -- 主流程 --

def main():
    if not API_KEY:
        print("=" * 50)
        print("  儿童简笔画模板生成器")
        print("=" * 50)
        print()
        print("请先设置环境变量：")
        print("  set DASHSCOPE_API_KEY=sk-xxx    (Windows)")
        print("  或")
        print("  export DASHSCOPE_API_KEY=sk-xxx (Mac/Linux)")
        print()
        sys.exit(1)

    # 屏蔽 API key 显示
    key_preview = API_KEY[:8] + "..." + API_KEY[-4:] if len(API_KEY) > 12 else "***"
    print(f"[Key] {key_preview}")
    print(f"[Endpoint] {BASE_URL}")
    print(f"[Model] {MODEL}")
    print(f"[Target] {ALIASES_PATH}")
    print(f"[Total] {len(BATCHES)} batches, {sum(len(b['items']) for b in BATCHES)} templates")
    print()

    total_added = 0

    for i, batch in enumerate(BATCHES, 1):
        name = batch["name"]
        items = batch["items"]
        print(f"\n{'='*50}")
        print(f"  [Batch {i}/{len(BATCHES)}] {name} ({len(items)}个)")
        print(f"{'='*50}")

        for j in range(0, len(items), 5):
            chunk = items[j:j+5]
            print(f"\n  -> 生成中 ({j+1}-{min(j+5, len(items))}/{len(items)})...")
            content = call_qwen(chunk, name)
            templates = parse_result(content)

            if templates:
                added = merge_into_aliases(templates)
                if added:
                    total_added += added

            # 请求间隔，避免限流
            if j + 5 < len(items):
                print("  [SLEEP] 等待2秒...")
                time.sleep(2)

    print(f"\n{'='*50}")
    print(f"  全部完成！共新增 {total_added} 个模板")
    print(f"{'='*50}")
    print(f"\n查看结果: {ALIASES_PATH}")


if __name__ == "__main__":
    main()
