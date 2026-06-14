"""Replace the small corr dict with comprehensive children's pronunciation error correction"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('script.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Build the comprehensive correction map
# Organized by pattern type

corrections = {
    # ── 动物常见发音错误 ──
    "兔几": "兔子", "兔纸": "兔子", "凸子": "兔子", "突子": "兔子",
    "猫猫": "猫", "毛毛": "猫", "喵喵": "猫",
    "狗狗": "狗", "购购": "狗", "沟沟": "狗",
    "鸡鸡": "鸡", "叽叽": "鸡", "计计": "鸡",
    "鸭鸭": "鸭", "丫丫": "鸭",
    "鱼鱼": "鱼", "于于": "鱼",
    "鸟鸟": "鸟",
    "牛牛": "牛", "纽纽": "牛",
    "猪猪": "猪", "蛛蛛": "猪",
    "马马": "马", "麻麻": "马",
    "羊羊": "羊", "阳阳": "羊",
    "象象": "象", "翔翔": "象",
    "蛇蛇": "蛇",
    "猴猴": "猴",
    "鼠鼠": "鼠", "叔叔": "鼠",
    "熊熊": "熊",
    "龙龙": "龙",
    "兔兔": "兔子",
    "西西": "星星", "心心": "星星", "新新": "星星",
    "月月": "月亮", "约约": "月亮",
    "花花": "花",
    "云云": "云",
    "草草": "草",
    "树树": "树", "数数": "树",
    "鱼": "鱼",  # already correct but helps normalization

    # ── 形状名称发音错误 ──
    "花圆": "画圆", "花园": "画圆", "化缘": "画圆",
    "举行": "矩形", "巨星": "矩形", "距形": "矩形",
    "滑县": "画线", "花线": "画线", "划陷": "画线",

    # ── 平翘舌混淆 (zh/z, ch/c, sh/s) ──
    "画住": "画猪", "画珠": "画猪",
    "画组": "画鼠",
    "画丝": "画狮", "画撕": "画狮",
    "画只": "画纸",
    "草子": "草纸",
    "时子": "狮子", "丝子": "狮子",
    "兔子": "兔子",  # intentional keep
    "长子": "长颈鹿",

    # ── n/l 混淆 ──
    "画刘": "画牛", "画六": "画牛",
    "画了": "画鸟",
    "画那": "画马",
    "老户": "老虎", "老斧": "老虎",
    "脑斧": "老虎", "老腐": "老虎",
    "老许": "老鼠",
    "来": "来",

    # ── 叠词归一 ──
    "猫猫": "猫", "狗狗": "狗", "兔兔": "兔子",
    "鸭鸭": "鸭", "鸡鸡": "鸡", "猪猪": "猪",
    "马马": "马", "牛牛": "牛", "羊羊": "羊",
    "象象": "象", "熊熊": "熊",
    "星星": "星星",
    "花花": "花",
    "车车": "车", "车车": "汽车",
    "糖糖": "糖",

    # ── 常见的儿童口齿不清 ──
    "画个懒": "画个蓝", "画个男": "画个蓝",
    "画个老": "画个鸟",
    "大几": "大鸡", "大计": "大鸡",
    "小计": "小鸡",
    "地地": "弟弟",
    "特特": "兔兔",
    "大大": "大象",
    "妈妈": "马",  # "妈妈" -> if context is drawing, likely "马"
    "爸爸": "八",

    # ── 方位词发音错误 ──
    "昨上": "左上", "幼上": "右上",
    "昨下": "左下", "幼下": "右下",
    "昨边": "左边", "幼边": "右边",
    "昨侧": "左侧", "幼侧": "右侧",
    "昨方": "左方", "幼方": "右方",

    # ── 操作命令发音错误 ──
    "请空": "清空", "庆功": "清空", "星空": "清空",
    "撤销": "撤销", "撤下": "撤销",
    "保存": "保存", "薄存": "保存",
    "擦掉": "擦掉", "插掉": "擦掉",
    "除掉": "擦掉", "出来": "擦掉",
    "移走": "移动",

    # ── 颜色发音错误 ──
    "红色": "红色", "红色": "红色",
    "蓝色": "蓝色", "男色": "蓝色",
    "绿色": "绿色", "六色": "绿色",
    "黄色": "黄色", "黄四": "黄色",
    "累色": "黑色",
    "白色": "白色", "百色": "白色",

    # ── 食物发音错误 ──
    "菊菊": "橘子",
    "苹苹": "苹果", "平平": "苹果",
    "香椒": "香蕉", "香椒": "香蕉",
    "草妹": "草莓", "倒霉": "草莓",
    "西挂": "西瓜", "西呱": "西瓜",
    "工作": "橙子",
    "冰饥淋": "冰淇淋", "冰麒麟": "冰淇淋",
    "蹦蹦糖": "棒棒糖", "帮帮糖": "棒棒糖",
    "蛋糕": "蛋糕", "碳高": "蛋糕",

    # ── 交通工具发音错误 ──
    "车车": "车",
    "飞几": "飞机", "灰机": "飞机",
    "本都车": "公交车",
    "小气车": "小汽车",
    "挖土机": "挖掘机",
    "救火车": "消防车",
    "救护车": "救护车", "救护车": "救护车",
    "火箭": "火箭", "火贱": "火箭",
    "直升机": "直升机", "纸升机": "直升机",
    "飞艇": "飞机",
    "嘟嘟车": "火车",
    "卡卡车": "卡车", "卡卡": "卡车",

    # ── 自然发音错误 ──
    "太远": "太阳", "太样": "太阳", "太太": "太阳",
    "约量": "月亮", "约亮": "月亮",
    "云彩": "云",
    "雨": "雨",
    "雪": "雪", "些": "雪",
    "风": "风", "冯": "风",
    "彩虹": "彩虹", "才虹": "彩虹",
    "闪电": "闪电",
    "火山": "火山", "火山": "火山",

    # ── 日常用品发音错误 ──
    "房几": "房子",
    "桌几": "桌子",
    "椅几": "椅子",
    "门": "门",
    "窗": "窗", "疮": "窗",
    "灯": "灯", "等": "灯",
    "电四": "电视",
    "电视": "电视",
    "电话": "电话", "电化": "电话",
    "相机": "相机", "相机": "相机",
    "时整": "时钟", "中表": "钟表",
    "雨伞": "雨伞",
    "铅笔": "铅笔", "铅比": "铅笔",
    "书": "书",
    "包": "包", "包包": "包",

    # ── 人物发音错误 ──
    "宝宝": "宝宝", "抱抱": "宝宝",
    "妹美": "妹妹", "媒媒": "妹妹",
    "姐姐": "姐姐", "解解": "姐姐",
    "弟弟": "弟弟", "迪迪": "弟弟",
    "哥哥": "哥哥", "鸽鸽": "哥哥",
    "爷爷": "爷爷", "也也": "爷爷",
    "奶奶": "奶奶", "来来": "奶奶",
    "爸爸": "爸爸",
    "妈妈": "妈妈",
    "人": "人",
    "小盆友": "小朋友",
    "娃娃": "娃娃",

    # ── 复杂图形的变体 ──
    "变形金刚": "机器人",
    "机机": "机器人",
    "恐恐": "恐龙",
    "圣诞树": "圣诞树", "圣蛋树": "圣诞树",
    "雪人": "雪人",
    "城堡": "城堡", "城宝": "城堡",
    "旗子": "旗子",
    "帐篷": "帐篷",
    "礼物": "礼物",
    "爱心": "爱心", "爱新": "爱心",
    "王冠": "王冠",
    "风筝": "风筝",
    "气球": "气球",
    "泵泡": "泡泡",
    "泡泡": "泡泡",
    "秋千": "秋千", "秋迁": "秋千",
    "滑梯": "滑梯", "滑体": "滑梯",
    "围巾": "围巾",
    "手套": "手套",
    "连衣裙": "连衣裙",
    "草": "草",
    "圣诞老人": "圣诞树",
    "南瓜": "南瓜灯",
    "苍蝇": "苍蝇",
    "蚊子": "蚊子",
    "蜘蛛": "蜘蛛",
    "蜜蜂": "蜜蜂", "密蜂": "蜜蜂",
    "蜻蜓": "蜻蜓", "清廷": "蜻蜓",
    "蚂蚁": "蚂蚁", "马蚁": "蚂蚁",
    "瓢虫": "瓢虫", "嫖虫": "瓢虫",
    "蝴蝶": "蝴蝶", "福蝶": "蝴蝶",
    "萤火虫": "萤火虫",
    "医院": "医院", "一员": "医院",
    "学校": "学校",
    "超市": "超市",
    "医生": "医生",
    "警察": "警察",
    "厨师": "厨师", "厨师": "厨师",
    "钢琴": "钢琴",
    "吉他": "吉他",
    "兔子": "兔子",  # Keep correct
}

# Build the JS object literal string
pairs = []
for wrong, correct in sorted(corrections.items()):
    pairs.append(f'      "{wrong}": "{correct}"')

corr_js = 'const corr = {\n' + ',\n'.join(pairs) + ',\n    };'

# Find the old corr dict and replace
old_start = c.find('const corr = {')
old_end = c.find('};', old_start) + 2

if old_start >= 0:
    c = c[:old_start] + corr_js + c[old_end:]
    print(f'Replaced corr dict ({len(corrections)} entries)')
else:
    print('FAIL: corr dict not found')

# Also add pronunciation correction in the AI mode flow before sending to backend
# Find where lastFinal is sent to parseWithAI
marker = 'console.log(`[Step 2] 发送AI: "${lastFinal}"`);'
if marker in c:
    old = 'console.log(`[Step 2] 发送AI: "${lastFinal}"`);'
    new = '// Apply pronunciation correction before sending to AI\n      for (const [wrong, correct] of Object.entries(corr)) { lastFinal = lastFinal.replaceAll(wrong, correct); }\n      console.log(`[Step 2] 发送AI: "${lastFinal}"`);'
    c = c.replace(old, new, 1)
    print('AI mode pronunciation correction added')
else:
    print('FAIL: AI mode marker not found')
    idx = c.find('发送AI')
    if idx >= 0: print(repr(c[idx-20:idx+60]))

# Also apply to the erase/move flow before check
marker2 = '// Try erase/move first'
if marker2 in c:
    old2 = '// Try erase/move first'
    new2 = '// Apply pronunciation correction\n      for (const [wrong, correct] of Object.entries(corr)) { lastFinal = lastFinal.replaceAll(wrong, correct); }\n      // Try erase/move first'
    c = c.replace(old2, new2, 1)
    print('Erase/move pronunciation correction added')
else:
    print('FAIL: erase/move marker not found')

# Also apply to relative positioning flow
marker3 = '// Try relative positioning first'
if marker3 in c:
    old3 = '// Try relative positioning first'
    new3 = '// Try relative positioning first'
    # Already covered by the erase/move insertion above since it's after

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
import re
opens = c.count('{')
closes = c.count('}')
print(f'Braces: {opens}/{closes}')

# Check corr size
start = c.find('const corr = {')
end = c.find('};', start)
if start >= 0:
    entries = c[start:end].count('": "')
    print(f'Found {entries} correction entries')

# Verify a few specific entries are present
for test in ['兔几', '花花', '太远', '飞几']:
    if test in c:
        print(f'  + {test}')
    else:
        print(f'  - MISSING {test}')
