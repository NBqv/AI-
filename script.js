/**

 * Voice Draw — Main Entry

 */



// ── DOM Ready ──────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {

  // ── Canvas Setup ────────────────────────────────────────

  const canvas = document.getElementById("canvas");

  const ctx = canvas.getContext("2d");



  canvas.width = 800;

  canvas.height = 600;



  // Fill background white

  ctx.fillStyle = "#fff";

  ctx.fillRect(0, 0, canvas.width, canvas.height);



  // ── Global References ──────────────────────────────────

  window.ctx = ctx;

  window.canvas = canvas;



  // ── Drawing State ──────────────────────────────────────

  window.currentColor = "black";

  window.currentRadius = 40;

  window.currentX = 400;

  window.currentY = 300;



  // ── History Stack (Undo) ───────────────────────────────

  const history = [];

  const MAX_HISTORY = 50;



  function saveSnapshot() {

    const data = ctx.getImageData(0, 0, canvas.width, canvas.height);

    history.push(data);

    if (history.length > MAX_HISTORY) history.shift();

    console.log(`[History] snapshot #${history.length}`);

  }



  window.undo = () => {

    if (history.length === 0) {

      speak("没有可以撤销的操作");

      return;

    }

    const data = history.pop();

    ctx.putImageData(data, 0, 0);

    console.log(`[History] undo → #${history.length} remaining`);

    speak("撤销成功");

  };



  window.saveDrawing = () => {

    const link = document.createElement("a");

    link.download = "drawing.png";

    link.href = canvas.toDataURL("image/png");

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);

    speak("图片已保存");

  };



  // ── Chinese Number Parser ──────────────────────────────

  const chineseDigit = {

    "零": 0, "一": 1, "二": 2, "三": 3, "四": 4,

    "五": 5, "六": 6, "七": 7, "八": 8, "九": 9,

  };



  function parseChineseNumber(str) {

    let result = 0;

    let temp = 0;



    for (const ch of str) {

      if (ch === "十") { result += (temp || 1) * 10; temp = 0; }

      else if (ch === "百") { result += (temp || 1) * 100; temp = 0; }

      else if (ch === "千") { result += (temp || 1) * 1000; temp = 0; }

      else if (chineseDigit[ch] !== undefined) { temp = chineseDigit[ch]; }

    }

    result += temp;

    return result || NaN;

  }



  // ── Position Name Map ──────────────────────────────────

  let positionMap = [

    { names: ["左上角", "左上"], x: 50, y: 50 },

    { names: ["右上角", "右上"], x: 750, y: 50 },

    { names: ["左下角", "左下"], x: 50, y: 550 },

    { names: ["右下角", "右下"], x: 750, y: 550 },

    { names: ["中心", "正中央", "中央", "中间"], x: 400, y: 300 },

    { names: ["左边中间", "左中"], x: 50, y: 300 },

    { names: ["右边中间", "右中"], x: 750, y: 300 },

    { names: ["上边中间", "上中"], x: 400, y: 50 },

    { names: ["下边中间", "下中"], x: 400, y: 550 },

  ];



  // ── Direction Helpers ──────────────────────────────────

  const directionMap = {

    "左": { dx: -1, dy: 0 }, "右": { dx: 1, dy: 0 },

    "上": { dx: 0, dy: -1 }, "下": { dx: 0, dy: 1 },

  };



  const defaultStep = 20;



  function getDirection(text) {

    for (const [key, vec] of Object.entries(directionMap))

      if (text.includes(key)) return vec;

    return null;

  }



  function getStep(text) {

    if (text.includes("一点点") || text.includes("一点")) return 10;

    if (text.includes("一大步") || text.includes("很多")) return 50;

    return defaultStep;

  }



  // ── Line Expression Parser ─────────────────────────────

  const lineActionPrefixes = ["画一条", "画条", "画一根", "绘制", "拉一条", "拉"];

  const lineActionSuffixes = ["线条"];



  function detectLineCommand(text) {

    const hasPrefix = lineActionPrefixes.some((p) => text.includes(p));

    const hasSuffix = lineActionSuffixes.some((s) => text.includes(s));

    const hasSimple = text.includes("画线") || text.includes("连线");

    if (!hasPrefix && !hasSuffix && !hasSimple) return null;



    let clean = text;

    for (const p of [...lineActionPrefixes].sort((a, b) => b.length - a.length)) clean = clean.replace(p, "");

    for (const s of [...lineActionSuffixes].sort((a, b) => b.length - a.length)) clean = clean.replace(s, "");

    clean = clean.replace("画线", "").replace("连线", "");

    clean = clean.replace(/的?线$/, "");

    return clean.trim() || "";

  }



  function resolvePosition(desc) {

    if (!desc) return null;

    const d = desc.trim();

    const sorted = [...positionMap].sort((a, b) => b.names[0].length - a.names[0].length);

    for (const entry of sorted)

      if (entry.names.some((n) => d.includes(n))) return { x: entry.x, y: entry.y };

    const numMatch = d.match(/(\d+)\s*[,，和\s]+\s*(\d+)/);

    if (numMatch) return { x: parseInt(numMatch[1], 10), y: parseInt(numMatch[2], 10) };

    const seqMatch = d.match(/^(\d{2,3})\s*(\d{2,3})$/);

    if (seqMatch) return { x: parseInt(seqMatch[1], 10), y: parseInt(seqMatch[2], 10) };

    return null;

  }



  function parseLineCommand(text) {

    const clean = detectLineCommand(text);

    if (clean === null) return null;

    let fromDesc = null, toDesc = null;

    const p1 = clean.match(/从\s*(.+?)\s*(?:到|至|往)\s*(.+)/);

    const p2 = !p1 && clean.match(/(.+?)\s*(?:到|至|往)\s*(.+)/);

    if (p1) { fromDesc = p1[1].trim(); toDesc = p1[2].trim(); }

    else if (p2) { fromDesc = p2[1].trim(); toDesc = p2[2].trim(); }

    if (!fromDesc || !toDesc) {

      if (!clean) return { x1: 200, y1: 300, x2: 600, y2: 300 };

      return null;

    }

    const from = resolvePosition(fromDesc);

    const to = resolvePosition(toDesc);

    if (from && to) return { x1: from.x, y1: from.y, x2: to.x, y2: to.y };

    if (to) return { x1: currentX, y1: currentY, x2: to.x, y2: to.y };

    return null;

  }



  // ── Color Map ─────────────────────────────────────────

  let colorMap = {

    "红色": "red", "红": "red",

    "蓝色": "blue", "蓝": "blue",

    "绿色": "green", "绿": "green",

    "黄色": "yellow", "黄": "yellow",

    "黑色": "black", "黑": "black",

    "白色": "white", "白": "white",

    "橙色": "orange", "橙": "orange",

    "紫色": "purple", "紫": "purple",

    "粉色": "pink", "粉": "pink",

  };



    const corr = {
      "一员": "医院",
      "丝子": "狮子",
      "丫丫": "鸭",
      "中表": "钟表",
      "举行": "矩形",
      "也也": "爷爷",
      "书": "书",
      "于于": "鱼",
      "云云": "云",
      "云彩": "云",
      "些": "雪",
      "人": "人",
      "保存": "保存",
      "倒霉": "草莓",
      "兔兔": "兔子",
      "兔几": "兔子",
      "兔子": "兔子",
      "兔纸": "兔子",
      "六色": "绿色",
      "冯": "风",
      "冰饥淋": "冰淇淋",
      "冰麒麟": "冰淇淋",
      "凸子": "兔子",
      "出来": "擦掉",
      "划陷": "画线",
      "包": "包",
      "包包": "包",
      "化缘": "画圆",
      "医生": "医生",
      "医院": "医院",
      "南瓜": "南瓜灯",
      "卡卡": "卡车",
      "卡卡车": "卡车",
      "厨师": "厨师",
      "叔叔": "鼠",
      "变形金刚": "机器人",
      "叽叽": "鸡",
      "吉他": "吉他",
      "哥哥": "哥哥",
      "喵喵": "猫",
      "嘟嘟车": "火车",
      "围巾": "围巾",
      "圣蛋树": "圣诞树",
      "圣诞树": "圣诞树",
      "圣诞老人": "圣诞树",
      "地地": "弟弟",
      "城堡": "城堡",
      "城宝": "城堡",
      "大几": "大鸡",
      "大大": "大象",
      "大计": "大鸡",
      "太太": "太阳",
      "太样": "太阳",
      "太远": "太阳",
      "奶奶": "奶奶",
      "妈妈": "妈妈",
      "妹美": "妹妹",
      "姐姐": "姐姐",
      "娃娃": "娃娃",
      "媒媒": "妹妹",
      "嫖虫": "瓢虫",
      "学校": "学校",
      "宝宝": "宝宝",
      "密蜂": "蜜蜂",
      "小气车": "小汽车",
      "小盆友": "小朋友",
      "小计": "小鸡",
      "工作": "橙子",
      "巨星": "矩形",
      "帐篷": "帐篷",
      "帮帮糖": "棒棒糖",
      "平平": "苹果",
      "幼上": "右上",
      "幼下": "右下",
      "幼侧": "右侧",
      "幼方": "右方",
      "幼边": "右边",
      "庆功": "清空",
      "弟弟": "弟弟",
      "彩虹": "彩虹",
      "心心": "星星",
      "恐恐": "恐龙",
      "房几": "房子",
      "手套": "手套",
      "才虹": "彩虹",
      "抱抱": "宝宝",
      "挖土机": "挖掘机",
      "插掉": "擦掉",
      "撤下": "撤销",
      "撤销": "撤销",
      "擦掉": "擦掉",
      "救护车": "救护车",
      "救火车": "消防车",
      "数数": "树",
      "新新": "星星",
      "旗子": "旗子",
      "时子": "狮子",
      "时整": "时钟",
      "星星": "星星",
      "星空": "清空",
      "昨上": "左上",
      "昨下": "左下",
      "昨侧": "左侧",
      "昨方": "左方",
      "昨边": "左边",
      "月月": "月亮",
      "本都车": "公交车",
      "机机": "机器人",
      "来": "来",
      "来来": "奶奶",
      "树树": "树",
      "桌几": "桌子",
      "椅几": "椅子",
      "毛毛": "猫",
      "气球": "气球",
      "沟沟": "狗",
      "泡泡": "泡泡",
      "泵泡": "泡泡",
      "清廷": "蜻蜓",
      "滑体": "滑梯",
      "滑县": "画线",
      "滑梯": "滑梯",
      "火山": "火山",
      "火箭": "火箭",
      "火贱": "火箭",
      "灯": "灯",
      "灰机": "飞机",
      "熊熊": "熊",
      "爱心": "爱心",
      "爱新": "爱心",
      "爷爷": "爷爷",
      "爸爸": "爸爸",
      "牛牛": "牛",
      "特特": "兔兔",
      "狗狗": "狗",
      "猪猪": "猪",
      "猫猫": "猫",
      "猴猴": "猴",
      "王冠": "王冠",
      "瓢虫": "瓢虫",
      "电化": "电话",
      "电四": "电视",
      "电视": "电视",
      "电话": "电话",
      "男色": "蓝色",
      "画丝": "画狮",
      "画个懒": "画个蓝",
      "画个男": "画个蓝",
      "画个老": "画个鸟",
      "画了": "画鸟",
      "画住": "画猪",
      "画六": "画牛",
      "画刘": "画牛",
      "画只": "画纸",
      "画撕": "画狮",
      "画珠": "画猪",
      "画组": "画鼠",
      "画那": "画马",
      "疮": "窗",
      "白色": "白色",
      "百色": "白色",
      "直升机": "直升机",
      "相机": "相机",
      "碳高": "蛋糕",
      "礼物": "礼物",
      "福蝶": "蝴蝶",
      "秋千": "秋千",
      "秋迁": "秋千",
      "移走": "移动",
      "突子": "兔子",
      "窗": "窗",
      "等": "灯",
      "糖糖": "糖",
      "累色": "黑色",
      "红色": "红色",
      "约亮": "月亮",
      "约约": "月亮",
      "约量": "月亮",
      "纸升机": "直升机",
      "纽纽": "牛",
      "绿色": "绿色",
      "羊羊": "羊",
      "翔翔": "象",
      "老户": "老虎",
      "老斧": "老虎",
      "老腐": "老虎",
      "老许": "老鼠",
      "脑斧": "老虎",
      "花园": "画圆",
      "花圆": "画圆",
      "花线": "画线",
      "花花": "花",
      "苍蝇": "苍蝇",
      "苹苹": "苹果",
      "草": "草",
      "草妹": "草莓",
      "草子": "草纸",
      "草草": "草",
      "菊菊": "橘子",
      "萤火虫": "萤火虫",
      "蓝色": "蓝色",
      "薄存": "保存",
      "蚂蚁": "蚂蚁",
      "蚊子": "蚊子",
      "蛇蛇": "蛇",
      "蛋糕": "蛋糕",
      "蛛蛛": "猪",
      "蜘蛛": "蜘蛛",
      "蜜蜂": "蜜蜂",
      "蜻蜓": "蜻蜓",
      "蝴蝶": "蝴蝶",
      "西呱": "西瓜",
      "西挂": "西瓜",
      "西西": "星星",
      "解解": "姐姐",
      "警察": "警察",
      "计计": "鸡",
      "请空": "清空",
      "象象": "象",
      "购购": "狗",
      "超市": "超市",
      "距形": "矩形",
      "蹦蹦糖": "棒棒糖",
      "车车": "车",
      "连衣裙": "连衣裙",
      "迪迪": "弟弟",
      "钢琴": "钢琴",
      "铅比": "铅笔",
      "铅笔": "铅笔",
      "长子": "长颈鹿",
      "门": "门",
      "闪电": "闪电",
      "阳阳": "羊",
      "除掉": "擦掉",
      "雨": "雨",
      "雨伞": "雨伞",
      "雪": "雪",
      "雪人": "雪人",
      "风": "风",
      "风筝": "风筝",
      "飞几": "飞机",
      "飞艇": "飞机",
      "香椒": "香蕉",
      "马蚁": "蚂蚁",
      "马马": "马",
      "鱼": "鱼",
      "鱼鱼": "鱼",
      "鸟鸟": "鸟",
      "鸡鸡": "鸡",
      "鸭鸭": "鸭",
      "鸽鸽": "哥哥",
      "麻麻": "马",
      "黄四": "黄色",
      "黄色": "黄色",
      "鼠鼠": "鼠",
      "龙龙": "龙",
    };

    



  // ── Shape Keywords ────────────────────────────────────

  let shapeMap = {

    circle: ["圆", "圆形", "圆圈"],

    rect: ["矩形", "长方形", "正方形", "方块"],

    line: ["线", "线条", "直线"],

  };



  // ── Compound Command Parser ────────────────────────────

  function parseCompoundCommand(text) {

    let shape = null;

    for (const [type, keywords] of Object.entries(shapeMap))

      if (keywords.some((kw) => text.includes(kw))) { shape = type; break; }

    if (!shape) return null;

    if (shape === "line") {

      if (text.includes("从") && (text.includes("到") || text.includes("至"))) return null;

      if (text.includes("向") && (text.includes("画") || text.includes("移"))) return null;

    }



    let pos = null;

    const sortedPos = [...positionMap].sort((a, b) => b.names[0].length - a.names[0].length);

    for (const entry of sortedPos)

      if (entry.names.some((n) => text.includes(n))) { pos = { x: entry.x, y: entry.y }; break; }

    if (!pos) {

      const np = text.match(/在\s*(\d+)\s*[,，和\s]+\s*(\d+)/);

      if (np) pos = { x: parseInt(np[1], 10), y: parseInt(np[2], 10) };

    }



    let color = null, colorName = null;

    for (const [kw, val] of Object.entries(colorMap))

      if (text.includes(kw)) { color = val; colorName = kw; break; }



    if (color) currentColor = color;

    const dx = pos ? pos.x : 400;

    const dy = pos ? pos.y : 300;



    if (shape === "circle") { drawCircle(dx, dy); speak(`画${colorName || "当前颜色"}圆成功`); return true; }

    if (shape === "rect") { drawRect(dx - 50, dy - 40, 100, 80); speak(`画${colorName || "当前颜色"}矩形成功`); return true; }

    if (shape === "line") { drawLine(200, 300, 600, 300); speak("画线成功"); return true; }

    return false;

  }



  // ── Drawing Functions ──────────────────────────────────

  window.drawCircle = (x, y, radius = currentRadius, color = currentColor) => {

    saveSnapshot();
    if (!_rebuilding)
    actionHistory.push({fn: "drawCircle", args: [x, y, radius, color], desc: "圆形("+x+","+y+") r="+radius});

    console.log(`[Draw] circle at (${x},${y}) radius=${radius} color=${color}`);

    ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2);

    ctx.fillStyle = color; ctx.fill(); ctx.closePath();

  };



  window.clearCanvas = () => { saveSnapshot(); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, canvas.width, canvas.height); if (!_rebuilding) actionHistory = []; };



  window.drawRect = (x = 300, y = 200, width = 100, height = 80, color = currentColor) => {

    saveSnapshot(); if (!_rebuilding) actionHistory.push({fn: "drawRect", args: [x, y, width, height, color], desc: "rect"}); console.log(`[Draw] rect at (${x},${y}) ${width}x${height} color=${color}`);

    ctx.fillStyle = color; ctx.fillRect(x, y, width, height);

  };



  window.drawLine = (x1 = 200, y1 = 300, x2 = 600, y2 = 300, color = currentColor) => {

    saveSnapshot(); if (!_rebuilding) actionHistory.push({fn: "drawLine", args: [x1, y1, x2, y2, color], desc: "line"}); console.log(`[Draw] line from (${x1},${y1}) to (${x2},${y2}) color=${color}`);

    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);

    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.stroke(); ctx.closePath();

  };



  window.drawPolygon = (points, color = currentColor) => {

    if (!points || points.length < 3) return;

    saveSnapshot(); if (!_rebuilding) actionHistory.push({fn: "drawPolygon", args: [points, color], desc: "poly"}); console.log(`[Draw] polygon ${points.length} pts color=${color}`);

    ctx.beginPath(); ctx.moveTo(points[0].x, points[0].y);

    for (let i = 1; i < points.length; i++) ctx.lineTo(points[i].x, points[i].y);

    ctx.closePath(); ctx.fillStyle = color; ctx.fill(); ctx.stroke();

  };



  window.drawArc = (x, y, radius, startAngle = 0, endAngle = Math.PI, color = currentColor) => {

    saveSnapshot(); if (!_rebuilding) actionHistory.push({fn: "drawArc", args: [x, y, radius, startAngle, endAngle, color], desc: "arc"}); console.log(`[Draw] arc at (${x},${y}) r=${radius} a=${startAngle}-${endAngle}`);

    ctx.beginPath(); ctx.arc(x, y, radius, startAngle, endAngle);

    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.stroke(); ctx.closePath();

  };



  window.drawEllipse = (x, y, radiusX, radiusY, color = currentColor) => {

    saveSnapshot(); if (!_rebuilding) actionHistory.push({fn: "drawEllipse", args: [x, y, radiusX, radiusY, color], desc: "ellipse"}); console.log(`[Draw] ellipse at (${x},${y}) rx=${radiusX} ry=${radiusY} color=${color}`);

    ctx.beginPath(); ctx.ellipse(x, y, radiusX, radiusY, 0, 0, Math.PI * 2);

    ctx.fillStyle = color; ctx.fill(); ctx.closePath();

  };



  window.moveTo = (x, y) => {

    currentX = x; currentY = y;

    console.log(`[Move] cursor to (${currentX},${currentY})`);

    ctx.fillStyle = "#999"; ctx.beginPath(); ctx.arc(currentX, currentY, 3, 0, Math.PI * 2); ctx.fill(); ctx.closePath();

    speak(`已移动到X${Math.round(currentX)}，Y${Math.round(currentY)}`);

  };



  window.lineTo = (x, y) => {

    saveSnapshot(); console.log(`[Line] from (${currentX},${currentY}) to (${x},${y})`);

    ctx.beginPath(); ctx.moveTo(currentX, currentY); ctx.lineTo(x, y);

    ctx.strokeStyle = currentColor; ctx.lineWidth = 2; ctx.stroke(); ctx.closePath();

    currentX = x; currentY = y;

    speak(`已连线到X${Math.round(currentX)}，Y${Math.round(currentY)}`);

  };



  // ── Speech Synthesis ──────────────────────────────────

  window.speak = (text) => {

    if (!window.speechSynthesis) return;

    const utterance = new SpeechSynthesisUtterance(text);

    utterance.lang = "zh-CN";

    speechSynthesis.speak(utterance);

  };



  // ── Graph Context (for AI editing/redrawing) ──────────

  const graphList = [];
  var actionHistory = [];
  var _rebuilding = false;  // true during rebuildCanvas, suppresses actionHistory push
  var lastTemplateName = "";

  const MAX_GRAPH_HISTORY = 10;

  // Store loaded complex_shapes templates for local template operations
  let templateDB = {};

  // Store drawn shape name keyword -> canvas entry mapping
  let shapeNameIndex = {};

  function recordShape(shape, desc, cx, cy) {
    const entry = { shape, desc, cx, cy };
    graphList.push(entry);
    if (graphList.length > MAX_GRAPH_HISTORY) graphList.shift();
  }

  /** Find the most recent shape matching a name keyword in graphList */
  function findShapeInCanvas(keyword) {
    for (let i = graphList.length - 1; i >= 0; i--) {
      const g = graphList[i];
      if (g.desc && g.desc.includes(keyword)) return g;
      if (g.cx != null) return g;
    }
    return null;
  }



  function getGraphContext() {

    if (graphList.length === 0) return "";

    const lines = graphList.map((g, i) => `  ${i + 1}. ${g.desc}`);

    return "【画布当前状态】以下图形已绘制在画布上（不需要重复绘制），你可以参考它们的坐标来修改或补充：\n" + lines.join("\n");

  }



  // Wrap draw functions to auto-record shapes for context

  const _origDrawCircle = window.drawCircle;

  window.drawCircle = (...args) => {

    _origDrawCircle(...args);

    recordShape("circle", `圆形(${args[0]},${args[1]}) r=${args[2]} 颜色${args[3]||currentColor}`, args[0], args[1]);

  };

  const _origDrawEllipse = window.drawEllipse;

  window.drawEllipse = (...args) => {

    _origDrawEllipse(...args);

    recordShape("ellipse", `椭圆(${args[0]},${args[1]}) rx=${args[2]} ry=${args[3]} 颜色${args[4]||currentColor}`, args[0], args[1]);

  };

  const _origDrawRect = window.drawRect;

  window.drawRect = (...args) => {

    _origDrawRect(...args);

    recordShape("rect", `矩形(${args[0]},${args[1]}) ${args[2]}x${args[3]} 颜色${args[4]||currentColor}`, args[0] + args[2]/2, args[1] + args[3]/2);

  };

  const _origDrawLine = window.drawLine;

  window.drawLine = (...args) => {

    _origDrawLine(...args);

    recordShape("line", `线段从(${args[0]},${args[1]})到(${args[2]},${args[3]}) 颜色${args[4]||currentColor}`, (args[0]+args[2])/2, (args[1]+args[3])/2);

  };

  const _origDrawArc = window.drawArc;

  window.drawArc = (...args) => {

    _origDrawArc(...args);

    recordShape("arc", `弧线(${args[0]},${args[1]}) r=${args[2]} 颜色${args[4]||currentColor}`, args[0], args[1]);

  };

  const _origDrawPolygon = window.drawPolygon;

  window.drawPolygon = (points, color) => {

    _origDrawPolygon(points, color);

    if (points && points.length >= 3) {

      const avgX = Math.round(points.reduce((s, p) => s + p.x, 0) / points.length);

      const avgY = Math.round(points.reduce((s, p) => s + p.y, 0) / points.length);

      recordShape("polygon", `多边形中心(${avgX},${avgY}) ${points.length}顶点 颜色${color||currentColor}`, avgX, avgY);

    }

  };

  const _origClearCanvas = window.clearCanvas;

  window.clearCanvas = () => { _origClearCanvas(); graphList.length = 0; shapeNameIndex = {}; };



  // ── Erase & Move: "擦掉兔子" / "把兔子移到右边" ──────────

    function rebuildCanvas() {
    _rebuilding = true;
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    graphList.length = 0;
    var histCopy = actionHistory.slice();
    for (var hi = 0; hi < histCopy.length; hi++) {
      var entry = histCopy[hi];
      var fn = window[entry.fn];
      if (fn) fn.apply(null, entry.args);
      if (entry.fn === "_batch_composite") {
        var cname = (entry.desc || "").replace("tpl_composite:", "");
        var cx = entry.args[0] || 400;
        var cy = entry.args[1] || 300;
        recordShape(cname, "tpl_composite:" + cname, cx, cy);
      }
    }
    _rebuilding = false;
  }

  function getShapeActionIndices(keyword) {
    // Find all actionHistory indices belonging to a shape matching keyword
    // Match by checking graphList entries that contain the keyword
    var indices = [];
    for (var gi = 0; gi < graphList.length; gi++) {
      var g = graphList[gi];
      if (g.desc && g.desc.indexOf(keyword) >= 0) {
        // Find matching actionHistory entries by checking if graphList entry
        // was recorded during the same rendering batch
        indices.push(gi);
        continue;
      }
      if (g.shape && g.shape.indexOf(keyword) >= 0) {
        indices.push(gi);
        continue;
      }
    }
    return indices;
  }

  function eraseShapeByKeyword(keyword) {
    // Find shape batch marker in actionHistory
    var markerIdx = -1;
    var markerName = "";
    for (var hi = 0; hi < actionHistory.length; hi++) {
      var entry = actionHistory[hi];
      if (entry.fn === "_batch_start") {
        var desc = entry.desc || "";
        if (desc.indexOf(keyword) >= 0 || desc.indexOf("tpl_start:") >= 0) {
          markerIdx = hi;
          markerName = desc.replace("tpl_start:", "");
          break;
        }
      }
    }

    if (markerIdx < 0) {
      // Fallback: try finding by graphList keyword match
      var foundInGraph = false;
      for (var gi = graphList.length - 1; gi >= 0; gi--) {
        if (graphList[gi].desc && graphList[gi].desc.indexOf(keyword) >= 0) {
          foundInGraph = true;
          break;
        }
      }
      if (!foundInGraph) {
        speak("没找到" + keyword);
        return false;
      }
      // If found in graph but no batch marker, it was drawn individually
      // Remove from actionHistory by matching single entries
      var removed = 0;
      var newHist = [];
      for (var hi = 0; hi < actionHistory.length; hi++) {
        var entry = actionHistory[hi];
        var desc = entry.desc || "";
        if (desc.indexOf(keyword) >= 0) {
          removed++;
        } else {
          newHist.push(entry);
        }
      }
      if (removed === 0) {
        speak("无法擦除" + keyword);
        return false;
      }
      actionHistory = newHist;
      saveSnapshot();
      rebuildCanvas();
      speak("已擦掉" + keyword);
      return true;
    }

    // Remove all entries from markerIdx to the next marker or end
    var nextMarker = -1;
    for (var hi = markerIdx + 1; hi < actionHistory.length; hi++) {
      if (actionHistory[hi].fn === "_batch_start") {
        nextMarker = hi;
        break;
      }
    }
    var endIdx = nextMarker > 0 ? nextMarker : actionHistory.length;

    // Also remove the composite graphList entry for this template
    var newHistory = actionHistory.slice(0, markerIdx).concat(actionHistory.slice(endIdx));

    var removedCount = endIdx - markerIdx;
    if (removedCount <= 0) {
      speak("无法擦除" + keyword);
      return false;
    }

    actionHistory = newHistory;
    saveSnapshot();
    rebuildCanvas();
    speak("已擦掉" + keyword);
    return true;
  }

  function parseEraseMoveCommand(text) {
    // Pattern 1: "擦掉兔子" / "删除乌龟" / "清除花"
    var eraseMatch = text.match(/(?:擦掉|擦除|删除|删掉|移除|去掉)(.+)/);
    if (eraseMatch) {
      var target = eraseMatch[1].trim();
      if (target) {
        var ok = eraseShapeByKeyword(target);
        return ok;
      }
    }

    // Pattern 2: "把兔子移到右边" / "把乌龟移到左边" / "移动兔子到上面"
    var moveMatch = text.match(/把(.+?)(?:移到|移动到|挪到|移至|移向|向|往)(?:左边|右边|上边|下边|上面|下面|左侧|右侧|左|右|上|下)/);
    if (moveMatch) {
      // Ensure the matched verb is followed by direction, not just end of word
      // For "向" and "往", they may need "移动" suffix
      var fullMatch = moveMatch[0];
      if (fullMatch.indexOf("向") >= 0 && text.indexOf("移动", moveMatch.index + fullMatch.length - 2) < 0) {
        // "向" without "移动" after it - skip this match
        moveMatch = null;
      }
    }
    if (!moveMatch) {
      moveMatch = text.match(/把(.+?)(?:向|往)(.+?)(?:边|面|侧|方)?(?:移|移动|挪)/);
    }
    if (!moveMatch) {
      moveMatch = text.match(/(?:移到|移动到|挪动)(.+?)到(?:左边|右边|上边|下边|上面|下面|左侧|右侧|左|右|上|下)/);
    }
    if (!moveMatch) {
      moveMatch = text.match(/(?:把|将)(.+?)(?:移到|移动到|挪到|移至)(.+?)(?:边|面|侧|方)/);
    }
    if (!moveMatch) {
      // Simpler: "移动兔子到右边"
      moveMatch = text.match(/移动(.+?)(?:到|至)(.+?)(?:边|面|侧|方)/);
    }
    if (!moveMatch) {
      // "兔子右移" / "猫左移"
      moveMatch = text.match(/(.+?)(?:左移|右移|上移|下移)/);
    }
    if (moveMatch) {
      var target = moveMatch[1].trim();
      var dirText = text.match(/(?:左边|右边|上边|下边|上面|下面|左侧|右侧|左|右|上|下)/);
      if (dirText) {
        console.log("[Move] 目标=" + target + " 方向=" + dirText[0]);
        return moveShapeByKeyword(target, dirText[0]);
      }
    }

    return false;
  }

    function moveShapeByKeyword(keyword, direction) {
    var dirMap = {
      "左": {dx: -1, dy: 0}, "左边": {dx: -1, dy: 0}, "左侧": {dx: -1, dy: 0},
      "右": {dx: 1, dy: 0}, "右边": {dx: 1, dy: 0}, "右侧": {dx: 1, dy: 0},
      "上": {dx: 0, dy: -1}, "上边": {dx: 0, dy: -1}, "上面": {dx: 0, dy: -1}, "上方": {dx: 0, dy: -1},
      "下": {dx: 0, dy: 1}, "下边": {dx: 0, dy: 1}, "下面": {dx: 0, dy: 1}, "下方": {dx: 0, dy: 1},
    };
    var dir = dirMap[direction];
    if (!dir) return false;

    // Find shape via _batch_start marker
    var markerIdx = -1;
    for (var hi = 0; hi < actionHistory.length; hi++) {
      if (actionHistory[hi].fn === "_batch_start") {
        var desc = actionHistory[hi].desc || "";
        if (desc.indexOf(keyword) >= 0) {
          markerIdx = hi;
          break;
        }
      }
    }

    if (markerIdx < 0) {
      // Fallback: find in graphList by keyword
      var found = false;
      for (var gi = graphList.length - 1; gi >= 0; gi--) {
        if (graphList[gi].desc && graphList[gi].desc.indexOf(keyword) >= 0) {
          found = true; break;
        }
      }
      if (!found) { speak("没找到" + keyword); return false; }
      // Try offsetting single actions by desc match
      var step = 80;
      var dx = Math.round(dir.dx * step);
      var dy = Math.round(dir.dy * step);
      var hit = false;
      for (var hi = 0; hi < actionHistory.length; hi++) {
        var entry = actionHistory[hi];
        if ((entry.desc || "").indexOf(keyword) >= 0) {
          var args = entry.args;
          if (entry.fn === "drawCircle" || entry.fn === "drawArc") { if (args.length >= 2) { args[0] += dx; args[1] += dy; hit = true; } }
          else if (entry.fn === "drawRect") { if (args.length >= 2) { args[0] += dx; args[1] += dy; hit = true; } }
          else if (entry.fn === "drawEllipse") { if (args.length >= 2) { args[0] += dx; args[1] += dy; hit = true; } }
          else if (entry.fn === "drawLine") { if (args.length >= 4) { args[0] += dx; args[1] += dy; args[2] += dx; args[3] += dy; hit = true; } }
          else if (entry.fn === "drawPolygon") { if (args[0] && Array.isArray(args[0])) { args[0] = args[0].map(function(p) { return {x:p.x+dx, y:p.y+dy}; }); hit = true; } }
        }
      }
      if (!hit) { speak("无法移动" + keyword); return false; }
      saveSnapshot(); rebuildCanvas(); speak("已移动" + keyword); return true;
    }

    // Find next marker
    var nextMarker = -1;
    for (var hi = markerIdx + 1; hi < actionHistory.length; hi++) {
      if (actionHistory[hi].fn === "_batch_start") { nextMarker = hi; break; }
    }
    var endIdx = nextMarker > 0 ? nextMarker : actionHistory.length;

    // Calculate offset
    var step = 80;
    var dx = Math.round(dir.dx * step);
    var dy = Math.round(dir.dy * step);

    // Bounds check on the batch actions
    var minX = 9999, maxX = 0, minY = 9999, maxY = 0;
    for (var hi = markerIdx + 1; hi < endIdx; hi++) {
      var entry = actionHistory[hi];
      var args = entry.args;
      if (entry.fn === "drawCircle") {
        minX = Math.min(minX, args[0]-args[2]); maxX = Math.max(maxX, args[0]+args[2]);
        minY = Math.min(minY, args[1]-args[2]); maxY = Math.max(maxY, args[1]+args[2]);
      } else if (entry.fn === "drawRect") {
        minX = Math.min(minX, args[0]); maxX = Math.max(maxX, args[0]+args[2]);
        minY = Math.min(minY, args[1]); maxY = Math.max(maxY, args[1]+args[3]);
      } else if (entry.fn === "drawLine") {
        minX = Math.min(minX, args[0], args[2]); maxX = Math.max(maxX, args[0], args[2]);
        minY = Math.min(minY, args[1], args[3]); maxY = Math.max(maxY, args[1], args[3]);
      } else if (entry.fn === "drawPolygon" && args[0]) {
        for (var pi = 0; pi < args[0].length; pi++) {
          minX = Math.min(minX, args[0][pi].x); maxX = Math.max(maxX, args[0][pi].x);
          minY = Math.min(minY, args[0][pi].y); maxY = Math.max(maxY, args[0][pi].y);
        }
      }
    }
    var margin = 20;
    if (minX + dx < margin) dx = margin - minX;
    if (maxX + dx > 800 - margin) dx = (800 - margin) - maxX;
    if (minY + dy < margin) dy = margin - minY;
    if (maxY + dy > 600 - margin) dy = (600 - margin) - maxY;
    dx = Math.round(dx); dy = Math.round(dy);

    // Offset all actions in the batch
    for (var hi = markerIdx + 1; hi < endIdx; hi++) {
      var entry = actionHistory[hi];
      var args = entry.args;
      if (entry.fn === "drawCircle" || entry.fn === "drawArc") { if (args.length >= 2) { args[0] += dx; args[1] += dy; } }
      else if (entry.fn === "drawRect") { if (args.length >= 2) { args[0] += dx; args[1] += dy; } }
      else if (entry.fn === "drawEllipse") { if (args.length >= 2) { args[0] += dx; args[1] += dy; } }
      else if (entry.fn === "drawLine") { if (args.length >= 4) { args[0] += dx; args[1] += dy; args[2] += dx; args[3] += dy; } }
      else if (entry.fn === "drawPolygon") { if (args[0] && Array.isArray(args[0])) { args[0] = args[0].map(function(p) { return {x:p.x+dx, y:p.y+dy}; }); } }
    }

    // Also update the composite graphList entry
    for (var gi = 0; gi < graphList.length; gi++) {
      if (graphList[gi].cx != null) { graphList[gi].cx += dx; graphList[gi].cy += dy; }
    }

    saveSnapshot();
    rebuildCanvas();
    speak("已将" + keyword + "移到" + direction);
    return true;
  }

  function offsetTemplateActions(actions, dx, dy) {
    return actions.map(function(a) {
      var na = JSON.parse(JSON.stringify(a));
      if (na.x != null) na.x += dx;
      if (na.y != null) na.y += dy;
      if (na.x1 != null) na.x1 += dx;
      if (na.y1 != null) na.y1 += dy;
      if (na.x2 != null) na.x2 += dx;
      if (na.y2 != null) na.y2 += dy;
      if (na.points) {
        na.points = na.points.map(function(p) { return { x: p.x + dx, y: p.y + dy }; });
      }
      return na;
    });
  }

  function tryRelativePosition(text) {
    var REL_DIR_MAP = {
      "左边": { dx: -1, dy: 0 }, "左侧": { dx: -1, dy: 0 }, "左": { dx: -1, dy: 0 },
      "右边": { dx: 1, dy: 0 }, "右侧": { dx: 1, dy: 0 }, "右": { dx: 1, dy: 0 },
      "上边": { dx: 0, dy: -1 }, "上面": { dx: 0, dy: -1 }, "上方": { dx: 0, dy: -1 }, "上": { dx: 0, dy: -1 },
      "下边": { dx: 0, dy: 1 }, "下面": { dx: 0, dy: 1 }, "下方": { dx: 0, dy: 1 }, "下": { dx: 0, dy: 1 },
      "旁边": { dx: -1.5, dy: 0 }, "附近": { dx: -1.5, dy: -0.5 },
    };
    var patterns = [
      /在(.+?)(左边|右边|上边|下边|上面|下面|上方|下方|左侧|右侧|旁边|附近|左|右|上|下)画(?:个|一个|只|条|棵|朵|座|的)?(.+)/,
      /在(.+?)的(左边|右边|上边|下边|上面|下面|左侧|右侧|旁边|附近|左|右|上|下)画(?:个|一个|只|条|棵|朵|座|的)?(.+)/,
    ];
    var match = null;
    for (var pi = 0; pi < patterns.length; pi++) {
      match = text.match(patterns[pi]);
      if (match) break;
    }
    if (!match) return null;

    var refName = match[1].trim();
    var dirKey = match[2].trim();
    var targetName = match[3].trim();

    console.log("[Relative] 参照=" + refName + " 方向=" + dirKey + " 目标=" + targetName);

    var refShape = findShapeInCanvas(refName);
    if (!refShape || refShape.cx == null) {
      console.log("[Relative] 找不到参考物 " + refName + " 在画布上");
      return null;
    }

    var dir = REL_DIR_MAP[dirKey];
    if (!dir) return null;

    var tplName = null;
    var tplActions = null;
    var keys = Object.keys(templateDB);
    for (var ki = 0; ki < keys.length; ki++) {
      var name = keys[ki];
      var tpl = templateDB[name];
      if (name === targetName || name.indexOf(targetName) >= 0 || targetName.indexOf(name) >= 0) {
        tplName = name;
        tplActions = tpl.actions;
        break;
      }
      for (var ai = 0; ai < (tpl.aliases || []).length; ai++) {
        var alias = tpl.aliases[ai];
        if (alias === targetName || targetName.indexOf(alias) >= 0 || alias.indexOf(targetName) >= 0) {
          tplName = name;
          tplActions = tpl.actions;
          break;
        }
      }
      if (tplName) break;
    }

    if (!tplActions) {
      console.log("[Relative] no template for " + targetName);
      return null;
    }

    var gap = 140;
    var offsetX = Math.round(refShape.cx + dir.dx * gap - 400);
    var offsetY = Math.round(refShape.cy + dir.dy * gap - 300);

    var shifted = offsetTemplateActions(tplActions, offsetX, offsetY);
    console.log("[Relative] 偏移: dx=" + offsetX + " dy=" + offsetY + " -> " + tplName);
    return { actions: shifted, name: tplName };
  }

  // ── AI Backend Service ─────────────────────────────────

  const AI_API = "http://localhost:8080";

  let aiMode = false;
  window.aiMode = aiMode;



  async function checkAI() {

    try { const r = await fetch(`${AI_API}/`); if (r.ok) return true; } catch (_) {}

  }



  // ── Load aliases from backend (extends local maps) ────

  async function loadAliases() {

    try {

      const r = await fetch(`${AI_API}/aliases`);

      if (!r.ok) return;

      const data = await r.json();

      console.log(`[Aliases] Loaded from backend`);



      // Extend color map

      if (data.color) {

        for (const [eng, names] of Object.entries(data.color)) {

          for (const name of names) {

            if (!colorMap[name]) colorMap[name] = eng;

          }

        }

      }



      // Extend shape map

      if (data.shape) {

        shapeMap = { ...shapeMap };

        for (const [eng, names] of Object.entries(data.shape)) {

          for (const name of names) {

            const key = eng === "rect" ? "rect" : eng;

            if (!shapeMap[key]) shapeMap[key] = [];

            if (!shapeMap[key].includes(name)) shapeMap[key].push(name);

          }

        }

      }



      // Extend position map

      if (data.position_absolute) {

        for (const entry of data.position_absolute) {

          const exists = positionMap.some(p => p.names[0] === entry.names[0]);

          if (!exists) positionMap.push({ names: entry.names, x: entry.x, y: entry.y });

        }

      }



      console.log(`[Aliases] colorMap:${Object.keys(data.color).length} shapeMap:${Object.keys(data.shape).length} position_absolute:${data.position_absolute.length}`);

      // Load complex_shapes templates for local relative positioning
      if (data.complex_shapes) {
        templateDB = data.complex_shapes;
        console.log(`[Aliases] Loaded ${Object.keys(templateDB).length} templates`);
      }

    } catch (_) {

      // Backend offline — use local maps only

    }

  }



  // Fetch aliases on startup (non-blocking)

  loadAliases();



  async function parseWithAI(text) {

    try {

      // Send graph context so AI knows what's on the canvas

      const ctx = getGraphContext();

      const body = ctx ? { text, context: ctx } : { text };

      console.log(`[Network] POST ${AI_API}/parse text="${text}"`);

      const r = await fetch(`${AI_API}/parse`, {

        method: "POST", headers: { "Content-Type": "application/json" },

        body: JSON.stringify(body),

      });

      if (!r.ok) {

        console.log(`[Network] 请求失败: ${r.status}`);

        return null;

      }

      const result = await r.json();

      console.log(`[Network] 响应:`, result);

      return result;

    } catch (e) {

      console.log(`[Network] 异常:`, e.message);

      return null;

    }

  }



  function executeAIResponse(data) {

    if (!data) return false;

    console.log(`[AI] AI响应数据:`, data);



    // ── 支持 actions 数组格式 ──

    const actions = data.actions || data.commands;

    const isBatch = Array.isArray(actions) && actions.length > 0;



    if (isBatch) {

      saveSnapshot();

      if (lastTemplateName) { actionHistory.push({fn: "_batch_start", args: [], desc: "tpl_start:" + lastTemplateName}); }
      for (const cmd of actions) {

        const c = cmd.color !== undefined ? cmd.color : currentColor;
        var _ox = window._globalOffsetX || 0;
        var _oy = window._globalOffsetY || 0;

        console.log(`[AI] 执行动作: ${cmd.action}`, cmd);



        // Normalize polygon points: support [[x,y],[x,y]] or [{"x":N,"y":N},...]

        let pts = cmd.points;

        if (pts && pts.length > 0 && Array.isArray(pts[0])) {

          pts = pts.map(p => ({ x: p[0], y: p[1] }));

        }



        switch (cmd.action) {

          case "drawCircle":

            if (cmd.radiusX !== undefined || cmd.radiusY !== undefined) {

              drawEllipse((cmd.x ?? 400) + _ox, (cmd.y ?? 300) + _oy, cmd.radiusX ?? cmd.radius ?? 40, cmd.radiusY ?? cmd.radius ?? 40, c);

            } else {

              drawCircle((cmd.x ?? 400) + _ox, (cmd.y ?? 300) + _oy, cmd.radius ?? currentRadius, c);

            }

            break;

          case "drawEllipse": case "drawOval":

            drawEllipse(cmd.x ?? 400, cmd.y ?? 300, cmd.radiusX ?? cmd.rx ?? 50, cmd.radiusY ?? cmd.ry ?? 30, c);

            break;

          case "drawRect": drawRect((cmd.x ?? 300) + _ox, (cmd.y ?? 200) + _oy, cmd.width ?? 80, cmd.height ?? 60, c); break;

          case "drawLine": drawLine((cmd.x1 ?? 200) + _ox, (cmd.y1 ?? 300) + _oy, (cmd.x2 ?? 600) + _ox, (cmd.y2 ?? 300) + _oy, c); break;

          case "drawPolygon": case "drawTriangle": case "drawStar":
            if (pts) { drawPolygon(pts, c); break; }
            {
              const cx = cmd.x ?? 400, cy = cmd.y ?? 300, r = cmd.radius ?? 40;
              const starPts = [];
              for (let i = 0; i < 10; i++) {
                const angle = (i * Math.PI * 2) / 10 - Math.PI / 2;
                const rad = i % 2 === 0 ? r : r * 0.4;
                starPts.push({ x: cx + rad * Math.cos(angle), y: cy + rad * Math.sin(angle) });
              }
              drawPolygon(starPts, c);
              break;
            }
          case "drawArc": drawArc((cmd.x ?? 400) + _ox, (cmd.y ?? 300) + _oy, cmd.radius ?? 40, cmd.startAngle ?? 0, cmd.endAngle ?? Math.PI, c); break;

          case "setColor": if (cmd.color) currentColor = cmd.color; break;

          case "setSize": if (cmd.size !== undefined && cmd.size !== null) currentRadius = cmd.size; break;

          case "clear": clearCanvas(); break;

        }

      }

      speak(actions.length > 1 ? "绘制完成" : "完成");
      if (lastTemplateName) {
        actionHistory.push({fn: "_batch_start", args: [], desc: "tpl_start:" + lastTemplateName});
        var _sx = 0, _sy = 0, _sc = 0;
        for (var _ri = 0; _ri < graphList.length; _ri++) {
          var _g = graphList[_ri];
          if (_g.cx != null) { _sx += _g.cx; _sy += _g.cy; _sc++; }
        }
        if (_sc > 0) {
          var _bcx = Math.round(_sx/_sc), _bcy = Math.round(_sy/_sc);
          actionHistory.push({fn: "_batch_composite", args: [_bcx, _bcy], desc: "tpl_composite:" + lastTemplateName});
          recordShape(lastTemplateName, "tpl_composite:" + lastTemplateName, _bcx, _bcy);
        }
        lastTemplateName = "";
      }

      return true;

    }



    // ── 单意图格式（旧格式兼容） ──

    if (!data.intent) {

      console.log(`[AI] 无intent，无法处理`);

      return false;

    }

    console.log(`[AI] intent=${data.intent}`, data);

    if (data.intent === "DRAW_SHAPE") {

      const x = data.position?.x ?? currentX; const y = data.position?.y ?? currentY;

      if (data.color) currentColor = data.color;

      if (data.size) currentRadius = data.size;

      if (data.shape === "circle") drawCircle(x, y);

      else if (data.shape === "rect") drawRect(x - 50, y - 40, 100, 80);

      else return false;

      speak(`画${data.color || ""}${data.shape === "circle" ? "圆" : "矩形"}成功`);

      return true;

    }

    if (data.intent === "LINE") {

      if (data.from_pos && data.to_pos) drawLine(data.from_pos.x, data.from_pos.y, data.to_pos.x, data.to_pos.y);

      else if (data.to_pos) drawLine(currentX, currentY, data.to_pos.x, data.to_pos.y);

      else if (data.direction) {

        const dm = { "左":{dx:-1,dy:0},"右":{dx:1,dy:0},"上":{dx:0,dy:-1},"下":{dx:0,dy:1} };

        const dir = dm[data.direction]; if (dir) lineTo(currentX + dir.dx * 100, currentY + dir.dy * 100);

      } else drawLine();

      speak("画线成功"); return true;

    }

    if (data.intent === "MOVE") {

      if (data.position) { moveTo(data.position.x, data.position.y); return true; }

      if (data.direction) {

        const dm = { "左":{dx:-1,dy:0},"右":{dx:1,dy:0},"上":{dx:0,dy:-1},"下":{dx:0,dy:1} };

        const dir = dm[data.direction];

        if (dir) { moveTo(currentX + dir.dx * 20, currentY + dir.dy * 20); return true; }

      }

      return false;

    }

    if (data.intent === "SET_COLOR" && data.color) { currentColor = data.color; speak(`颜色已设为${data.color}`); return true; }

    if (data.intent === "SET_SIZE" && data.size) { currentRadius = data.size; speak(`半径已设为${data.size}`); return true; }

    if (data.intent === "CLEAR") { clearCanvas(); speak("清空成功"); return true; }

    if (data.intent === "UNDO") { undo(); return true; }

    if (data.intent === "SAVE") { saveDrawing(); return true; }

    return false;

  }



  // ── Local Parser ──────────────────────────────────────

  function parseLocal(text) {

    // Step 1: clean text

    const filler = ["嗯", "啊", "哦", "吧", "的", "了", "嘛", "呀", "啦",

      "一个", "给我", "帮我", "这个", "那个", "一下", "一下下"];

    for (const w of filler) text = text.replaceAll(w, "");

    text = text.trim();



    // Step 2: misrecognition correctionfor (const [w, c] of Object.entries(corr)) text = text.replaceAll(w, c);



    let matched = false;



    // Compound command

    if (!matched) matched = parseCompoundCommand(text);



    // Color

    if (!matched) {

      for (const [kw, val] of Object.entries(colorMap)) {

        if (text.includes(kw)) { currentColor = val; speak(`当前颜色${kw}`); setStatus(STATUS.SUCCESS, `🎨 颜色：${kw}`); matched = true; break; }

      }

    }



    // Radius

    if (!matched) {

      const rm = text.match(/半径\s*(\d+)/) || text.match(/半径为\s*(\d+)/);

      const cn = !rm && text.match(/半径\s*([零一二三四五六七八九十百千]+)/);

      if (rm) { currentRadius = parseInt(rm[1], 10); speak(`当前半径${currentRadius}`); setStatus(STATUS.SUCCESS, `📏 半径：${currentRadius}`); matched = true; }

      else if (cn) { const p = parseChineseNumber(cn[1]); if (!isNaN(p)) { currentRadius = p; speak(`当前半径${currentRadius}`); setStatus(STATUS.SUCCESS, `📏 半径：${currentRadius}`); matched = true; } }

    }



    // Move to numeric

    if (!matched) {

      const mm = text.match(/移动到\s*(\d+)\s*[,，和\s]+\s*(\d+)/);

      if (mm) { moveTo(+mm[1], +mm[2]); setStatus(STATUS.SUCCESS, `📍 移动到 (${mm[1]}, ${mm[2]})`); matched = true; }

    }



    // LineTo numeric

    if (!matched) {

      const lm = text.match(/连线到\s*(\d+)\s*[,，和\s]+\s*(\d+)/);

      if (lm) { lineTo(+lm[1], +lm[2]); setStatus(STATUS.SUCCESS, `📏 连线到 (${lm[1]}, ${lm[2]})`); matched = true; }

    }



    // Line expression parser (from→to)

    if (!matched) {

      const lr = parseLineCommand(text);

      if (lr) { drawLine(lr.x1, lr.y1, lr.x2, lr.y2); setStatus(STATUS.SUCCESS, `📏 ${text.slice(0, 24)}`); matched = true; }

    }



    // Position name → moveTo

    if (!matched) {

      const sorted = [...positionMap].sort((a, b) => b.names[0].length - a.names[0].length);

      for (const e of sorted) {

        if (e.names.some(n => text.includes(n))) { moveTo(e.x, e.y); setStatus(STATUS.SUCCESS, `📍 ${e.names[0]}`); matched = true; break; }

      }

    }



    // Directional line

    if (!matched) {

      const combined = { "左上":{dx:-1,dy:-1},"左下":{dx:-1,dy:1},"右上":{dx:1,dy:-1},"右下":{dx:1,dy:1} };

      let dir = null;

      for (const [k, v] of Object.entries(combined)) { if (text.includes(k)) { dir = v; break; } }

      if (!dir) dir = getDirection(text);

      if (dir && (text.includes("画线") || text.includes("画条") || text.includes("画一根"))) {

        const len = text.includes("一点") ? 50 : text.includes("很多") ? 150 : 100;

        lineTo(currentX + dir.dx * len, currentY + dir.dy * len);

        const dn = Object.keys(directionMap).find(d => text.includes(d)) || "斜";

        setStatus(STATUS.SUCCESS, `📏 向${dn}画线`); matched = true;

      }

    }



    // Relative direction move

    if (!matched) {

      const combined = { "左上":{dx:-1,dy:-1},"左下":{dx:-1,dy:1},"右上":{dx:1,dy:-1},"右下":{dx:1,dy:1} };

      let dir = null, dn = null;

      for (const [k, v] of Object.entries(combined)) { if (text.includes(k)) { dir = v; dn = k; break; } }

      if (!dir) { for (const [k, v] of Object.entries(directionMap)) { if (text.includes(k)) { dir = v; dn = k; break; } } }

      if (dir && (text.includes("往") || text.includes("向") || text.includes("移") || text.includes("走"))) {

        const step = getStep(text);

        moveTo(currentX + dir.dx * step, currentY + dir.dy * step);

        setStatus(STATUS.SUCCESS, `📍 往${dn}`); matched = true;

      }

    }



    // Circle fallback

    if (!matched && ["圆", "圆圈", "圆形"].some(k => text.includes(k))) { drawCircle(400, 300); speak("画圆成功"); setStatus(STATUS.SUCCESS, "✅ 画圆"); matched = true; }

    // Rectangle fallback

    if (!matched && ["矩形", "长方形", "正方形", "方块"].some(k => text.includes(k))) { drawRect(); speak("画矩形成功"); setStatus(STATUS.SUCCESS, "✅ 画矩形"); matched = true; }

    // Clear

    if (!matched && ["清空", "清除", "擦掉"].some(k => text.includes(k))) { clearCanvas(); speak("清空成功"); setStatus(STATUS.SUCCESS, "✅ 已清空"); matched = true; }

    // Undo

    if (!matched && ["撤销", "撤回", "回退", "上一步"].some(k => text.includes(k))) { undo(); setStatus(STATUS.SUCCESS, "↩️ 已撤销"); matched = true; }

    // Save

    if (!matched && ["保存", "导出", "下载图片"].some(k => text.includes(k))) { saveDrawing(); setStatus(STATUS.SUCCESS, "💾 已保存"); matched = true; }

    // Redraw / retry

    if (!matched && (text.includes("重新画") || text.includes("重画") || text.includes("重来") || text.includes("重新画一个"))) {

      clearCanvas();

      speak("已清空，重新来");

      setStatus(STATUS.SUCCESS, "🗑️ 已清空，请重新说"); matched = true;

    }

    // Retry AI (for AI mode: resend same request)

    if (!matched && text.includes("换一个") && aiMode) {

      matched = true; // Don't fall through to "没听清"

    }

    // Fallback

    if (!matched && text) speak("没听清，请再说一遍");

  }



  // ── Elements & Status System ──────────────────────────

  const statusDot = document.getElementById("status-dot");

  const statusLabel = document.getElementById("status-label");

  const recognizedTextEl = document.getElementById("recognizedText");

  const recordBtn = document.getElementById("recordBtn");

  const aiToggle = document.getElementById("aiToggle");



  const STATUS = {

    IDLE:      { cls: "dot-idle",      msg: "等待语音" },

    LISTENING: { cls: "dot-listening", msg: "聆听中..." },

    THINKING:  { cls: "dot-thinking",  msg: "AI 思考中" },

    DRAWING:   { cls: "dot-drawing",   msg: "绘图执行中" },

    SUCCESS:   { cls: "dot-success",   msg: "完成 ✓" },

    ERROR:     { cls: "dot-error",     msg: "出错" },

  };



  function setStatus(state, msg) {

    statusDot.className = state.cls;

    statusLabel.textContent = msg || state.msg;

  }



  // ── Utility buttons ────────────────────────────────────
  if (undoBtn) {
    undoBtn.addEventListener("click", () => { if (typeof window.undo === "function") window.undo(); });
  }
  if (clearBtn) {
    clearBtn.addEventListener("click", () => { if (typeof window.clearCanvas === "function") window.clearCanvas(); speak("已清空"); });
  }
  if (saveBtn) {
    saveBtn.addEventListener("click", () => { if (typeof window.saveDrawing === "function") window.saveDrawing(); });
  }

  // ── Quick tips ──────────────────────────────────────────
  document.querySelectorAll(".tip").forEach(function(tip) {
    tip.addEventListener("click", function() {
      var text = this.getAttribute("data-text") || "";
      if (!text) return;
      document.getElementById("recognizedText").textContent = text;
      if (aiMode) {
        setStatus(STATUS.THINKING, "AI 思考中...");
        parseWithAI(text).then(function(data) {
          var a = data && (data.actions || data.commands);
          if (a && a.length > 0) {
            if (data.backend && data.backend.indexOf("template:") === 0) {
              lastTemplateName = data.backend.replace("template:", "");
            }
            executeAIResponse(data);
            setStatus(STATUS.SUCCESS, "完成 ✓");
          } else {
            parseLocal(text);
          }
        });
      } else {
        parseLocal(text);
      }
    });
  });

  // ── AI Toggle ──────────────────────────────────────────

  if (aiToggle) {

    aiToggle.addEventListener("click", async () => {

      if (!aiMode) {

        aiToggle.textContent = "🧠 连接中...";

        aiToggle.classList.add("ai-active");

        const ok = await checkAI();

        if (ok) {

          aiMode = true;

          aiToggle.textContent = "🧠 AI模式";

          aiToggle.classList.add("ai-active");

          setStatus(STATUS.IDLE, "AI 模式已启用");

        } else {

          aiMode = false;

          aiToggle.textContent = "🧠 AI离线";

          aiToggle.classList.add("ai-error");

          setTimeout(() => {

            aiToggle.textContent = "🧠 本地模式";

            aiToggle.classList.remove("ai-error", "ai-active");

          }, 3000);

          setStatus(STATUS.ERROR, "AI 后端未启动，使用本地模式");

        }

      } else {

        aiMode = false;

        aiToggle.textContent = "🧠 本地模式";

        aiToggle.classList.remove("ai-active");

        setStatus(STATUS.IDLE, "本地模式");

      }

    });

  }



  // ── Split continuous commands ─────────────────────────
    function splitContinuousCommands(text) {
    // Strategy: split on connector words that appear between drawing commands
    // First try: split on 再/然后/还/又/接着 before drawing verbs
    // Use a non-capturing group to avoid extra segments
    var parts = text.split(/(?:再|然后|接着|接下来)(?=\s*(?:画|绘|来|给我|整|搞))/);
    var result = [];
    for (var pi = 0; pi < parts.length; pi++) {
      var s = parts[pi].trim();
      if (s) result.push(s);
    }
    // If still single segment, try 还/又 (which are single chars)
    if (result.length <= 1) {
      var t = text;
      // Replace 还画/又画 with a unique split marker
      t = t.replace(/还(?=画|绘)/g, "\nSPLIT\n");
      t = t.replace(/又(?=画|绘)/g, "\nSPLIT\n");
      var parts2 = t.split("\nSPLIT\n");
      result = [];
      for (var pi = 0; pi < parts2.length; pi++) {
        var s = parts2[pi].trim();
        if (s) result.push(s);
      }
    }
    // If still single segment, try 和/跟 between commands
    if (result.length <= 1) {
      var parts3 = text.split(/(?:和|跟)(?=\s*(?:画|绘|来|给我|整|搞))/);
      result = [];
      for (var pi = 0; pi < parts3.length; pi++) {
        var s = parts3[pi].trim();
        if (s) result.push(s);
      }
    }
    return result;
  }function executeActions(actions) {
    for (var _i = 0; _i < actions.length; _i++) {
      var cmd = actions[_i];
      var _ox = window._globalOffsetX || 0;
    var _oy = window._globalOffsetY || 0;
    var _c = cmd.color !== undefined ? cmd.color : currentColor;
    var _ox = window._globalOffsetX || 0;
    var _oy = window._globalOffsetY || 0;
      var pts = cmd.points;
      if (pts && pts.length > 0 && Array.isArray(pts[0])) {
        pts = pts.map(function(p) { return Array.isArray(p) ? {x: p[0], y: p[1]} : p; });
      }
      switch (cmd.action) {
        case "drawCircle":
          if (cmd.radiusX !== undefined || cmd.radiusY !== undefined) {
            drawEllipse(cmd.x || 400, cmd.y || 300, cmd.radiusX || cmd.radius || 40, cmd.radiusY || cmd.radius || 40, _c);
          } else {
            drawCircle((cmd.x || 400) + _ox, (cmd.y || 300) + _oy, cmd.radius || currentRadius, _c);
          }
          break;
        case "drawEllipse": drawEllipse((cmd.x || 400) + _ox, (cmd.y || 300) + _oy, cmd.radiusX || 50, cmd.radiusY || 30, _c); break;
        case "drawRect": drawRect((cmd.x || 300) + _ox, (cmd.y || 200) + _oy, cmd.width || 80, cmd.height || 60, _c); break;
        case "drawLine": drawLine((cmd.x1 || 200) + _ox, (cmd.y1 || 300) + _oy, (cmd.x2 || 600) + _ox, (cmd.y2 || 300) + _oy, _c); break;
        case "drawPolygon": case "drawTriangle": if (pts) drawPolygon(pts, _c); break;
        case "drawArc": drawArc(cmd.x || 400, cmd.y || 300, cmd.radius || 40, cmd.startAngle || 0, cmd.endAngle || 3.14159, _c); break;
        case "drawStar":
          if (pts) { drawPolygon(pts, _c); break; }
          var cx = cmd.x || 400, cy = cmd.y || 300, r = cmd.radius || 40;
          var starPts = [];
          for (var si = 0; si < 10; si++) {
            var angle = (si * Math.PI * 2) / 10 - Math.PI / 2;
            var rad = si % 2 === 0 ? r : r * 0.4;
            starPts.push({ x: cx + rad * Math.cos(angle), y: cy + rad * Math.sin(angle) });
          }
          drawPolygon(starPts, _c);
          break;
      }
    }
  }

  // ── Speech Recognition ──────────────────────────────────

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;



  if (!SpeechRecognition) {

    setStatus(STATUS.ERROR, "浏览器不支持语音识别，请使用 Chrome");

    recordBtn.disabled = true;

  } else {

    const recognition = new SpeechRecognition();

    recognition.continuous = true;

    recognition.interimResults = true;

    recognition.lang = "zh-CN";



    recognition.onresult = (event) => {

      let interim = "", final = "", lastFinal = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {

        const t = event.results[i][0].transcript;

        if (event.results[i].isFinal) { final += t; lastFinal = t; }

        else { interim += t; }

      }

      const display = final || interim;

      if (display.trim()) recognizedTextEl.textContent = display;

      if (!lastFinal) return;



      // ── Debug ──

      console.log(`[Step 1] 语音识别: "${lastFinal}"`);



      // AI or local mode

      // Apply pronunciation correction
      for (const [wrong, correct] of Object.entries(corr)) { lastFinal = lastFinal.replaceAll(wrong, correct); }

      // ── Split continuous commands: "画个猫再画个花再画个房子" ──
      var segments = splitContinuousCommands(lastFinal);
      if (segments.length > 1) {
        console.log("[Continuous] 分割为 " + segments.length + " 段: ", segments);
        var segIdx = 0;
        function processNextSegment() {
          if (segIdx >= segments.length) {
            setStatus(STATUS.SUCCESS, "全部完成 ✓");
            return;
          }
          var cmd = segments[segIdx];
          // Shift each subsequent drawing to avoid overlap
          if (segIdx > 0) {
            // Apply a global position offset so templates don't overlap
            var _segN = segIdx;
            var _offsetCol = (_segN * 180) % 600;
            var _offsetRow = Math.floor((_segN * 180) / 600) * 180 + 30;
            window._globalOffsetX = _offsetCol;
            window._globalOffsetY = _offsetRow;
          } else {
            window._globalOffsetX = 0;
            window._globalOffsetY = 0;
          }
          segIdx++;
          console.log("[Continuous] 执行第 " + segIdx + "/" + segments.length + " 段: " + cmd);
          // Apply same pipeline for each segment
          // Try erase/move then relative positioning then AI/local
          if (parseEraseMoveCommand(cmd)) {
            setStatus(STATUS.DRAWING, "正在处理...");
            processNextSegment();
            return;
          }
          var rel = tryRelativePosition(cmd);
          if (rel) {
            setStatus(STATUS.DRAWING, "相对位置绘图...");
            saveSnapshot();
            executeActions(rel.actions);
            speak("在" + rel.name + "旁边画好了");
            processNextSegment();
            return;
          }
          if (aiMode) {
            setStatus(STATUS.THINKING, "AI 思考中...");
            parseWithAI(cmd).then(function(data) {
              var a = data && (data.actions || data.commands);
              if (a && a.length > 0) {
                executeAIResponse(data);
              } else {
                currentX = (window._globalOffsetX || 0) + 400; currentY = (window._globalOffsetY || 0) + 200;
                parseLocal(cmd);
              }
              processNextSegment();
            });
          } else {
            currentX = (window._globalOffsetX || 0) + 400; currentY = (window._globalOffsetY || 0) + 200;
            parseLocal(cmd);
            processNextSegment();
          }
        }
        processNextSegment();
        // Clear global offset after all segments
        window._globalOffsetX = 0;
        window._globalOffsetY = 0;
        return;  // skip the single-command path below
      }

      // Try erase/move first
      var eraseMoveResult = parseEraseMoveCommand(lastFinal);
      if (eraseMoveResult) {
        setStatus(STATUS.SUCCESS, "完成 \u2713");
        return;
      }

      // Try relative positioning first
      var relResult = tryRelativePosition(lastFinal);
      if (relResult) {
        console.log("[Relative] 命中: " + relResult.name);
        setStatus(STATUS.DRAWING, "相对位置绘图...");
        saveSnapshot();
        var _actions = relResult.actions;
        for (var _i = 0; _i < _actions.length; _i++) {
          var cmd = _actions[_i];
          var _c = cmd.color !== undefined ? cmd.color : currentColor;
          var pts = cmd.points;
          if (pts && pts.length > 0 && Array.isArray(pts[0])) {
            pts = pts.map(function(p) { return Array.isArray(p) ? {x: p[0], y: p[1]} : p; });
          }
          (function(cmd, _c, pts) {
            switch (cmd.action) {
              case "drawCircle":
                if (cmd.radiusX !== undefined || cmd.radiusY !== undefined) {
                  drawEllipse(cmd.x || 400, cmd.y || 300, cmd.radiusX || cmd.radius || 40, cmd.radiusY || cmd.radius || 40, _c);
                } else {
                  drawCircle((cmd.x || 400) + _ox, (cmd.y || 300) + _oy, cmd.radius || currentRadius, _c);
                }
                break;
              case "drawEllipse": drawEllipse((cmd.x || 400) + _ox, (cmd.y || 300) + _oy, cmd.radiusX || 50, cmd.radiusY || 30, _c); break;
              case "drawRect": drawRect((cmd.x || 300) + _ox, (cmd.y || 200) + _oy, cmd.width || 80, cmd.height || 60, _c); break;
              case "drawLine": drawLine((cmd.x1 || 200) + _ox, (cmd.y1 || 300) + _oy, (cmd.x2 || 600) + _ox, (cmd.y2 || 300) + _oy, _c); break;
              case "drawPolygon": case "drawTriangle": if (pts) drawPolygon(pts, _c); break;
              case "drawArc": drawArc(cmd.x || 400, cmd.y || 300, cmd.radius || 40, cmd.startAngle || 0, cmd.endAngle || 3.14159, _c); break;
              case "drawStar":
                if (pts) { drawPolygon(pts, _c); break; }
                var cx = cmd.x || 400, cy = cmd.y || 300, r = cmd.radius || 40;
                var starPts = [];
                for (var si = 0; si < 10; si++) {
                  var angle = (si * Math.PI * 2) / 10 - Math.PI / 2;
                  var rad = si % 2 === 0 ? r : r * 0.4;
                  starPts.push({ x: cx + rad * Math.cos(angle), y: cy + rad * Math.sin(angle) });
                }
                drawPolygon(starPts, _c);
                break;
            }
          })(cmd, _c, pts);
        }
        speak("在" + relResult.name + "旁边画好了");
        setStatus(STATUS.SUCCESS, "完成 ✓");
        return;
      }

      if (aiMode) {

        // Apply pronunciation correction before sending to AI
      for (const [wrong, correct] of Object.entries(corr)) { lastFinal = lastFinal.replaceAll(wrong, correct); }
      console.log(`[Step 2] 发送AI: "${lastFinal}"`);

        setStatus(STATUS.THINKING, "AI 思考中...");

        parseWithAI(lastFinal).then((data) => {

          console.log(`[Step 3] AI返回:`, data);

          // 同时检查 intent 和 actions 数组

          const hasActions = data && ((data.actions && data.actions.length > 0) || (data.commands && data.commands.length > 0));

          const hasIntent = data && data.intent && data.intent !== "UNKNOWN";

          if (hasActions || hasIntent) {

            if (data.backend && data.backend.indexOf("template:") === 0) {
              lastTemplateName = data.backend.replace("tpl_composite:", "");
            }

            const ok = executeAIResponse(data);

            if (ok) setStatus(STATUS.SUCCESS, "完成 ✓");

            else parseLocal(lastFinal);

          } else {

            setStatus(STATUS.IDLE, "AI未识别，使用本地模式");

            parseLocal(lastFinal);

          }

        });

      } else {

        parseLocal(lastFinal);

      }

    };



    recognition.onerror = (event) => {

      console.error("Speech recognition error:", event.error);

      setStatus(STATUS.ERROR, `错误：${event.error}`);

      if (event.error === "no-speech" || event.error === "aborted") {

        recordBtn.disabled = false;

        recordBtn.textContent = "🎤 开始说话"; recordBtn.classList.remove("recording");

      }

    };



    recognition.onend = () => {

      if (recordBtn.textContent === "⏹ 停止") recognition.start();

      else { recordBtn.disabled = false; recordBtn.textContent = "🎤 开始说话"; recordBtn.classList.remove("recording"); }

    };



    recordBtn.addEventListener("click", () => {

      if (recordBtn.textContent === "🎤 开始说话") {

        recognition.start();

        recordBtn.textContent = "⏹ 停止"; recordBtn.classList.add("recording");

        setStatus(STATUS.LISTENING, "正在聆听...");

      } else {

        recognition.stop();

        recordBtn.textContent = "🎤 开始说话"; recordBtn.classList.remove("recording");

        setStatus(STATUS.IDLE, "已停止");

      }

    });



    window.recognition = recognition;

  }



  console.log("Voice Draw ready");

});