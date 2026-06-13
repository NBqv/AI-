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
    console.log(`[Draw] circle at (${x},${y}) radius=${radius} color=${color}`);
    ctx.beginPath(); ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = color; ctx.fill(); ctx.closePath();
  };

  window.clearCanvas = () => { saveSnapshot(); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, canvas.width, canvas.height); };

  window.drawRect = (x = 300, y = 200, width = 100, height = 80, color = currentColor) => {
    saveSnapshot(); console.log(`[Draw] rect at (${x},${y}) ${width}x${height} color=${color}`);
    ctx.fillStyle = color; ctx.fillRect(x, y, width, height);
  };

  window.drawLine = (x1 = 200, y1 = 300, x2 = 600, y2 = 300, color = currentColor) => {
    saveSnapshot(); console.log(`[Draw] line from (${x1},${y1}) to (${x2},${y2}) color=${color}`);
    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.stroke(); ctx.closePath();
  };

  window.drawPolygon = (points, color = currentColor) => {
    if (!points || points.length < 3) return;
    saveSnapshot(); console.log(`[Draw] polygon ${points.length} pts color=${color}`);
    ctx.beginPath(); ctx.moveTo(points[0].x, points[0].y);
    for (let i = 1; i < points.length; i++) ctx.lineTo(points[i].x, points[i].y);
    ctx.closePath(); ctx.fillStyle = color; ctx.fill(); ctx.stroke();
  };

  window.drawArc = (x, y, radius, startAngle = 0, endAngle = Math.PI, color = currentColor) => {
    saveSnapshot(); console.log(`[Draw] arc at (${x},${y}) r=${radius} a=${startAngle}-${endAngle}`);
    ctx.beginPath(); ctx.arc(x, y, radius, startAngle, endAngle);
    ctx.strokeStyle = color; ctx.lineWidth = 3; ctx.stroke(); ctx.closePath();
  };

  window.drawEllipse = (x, y, radiusX, radiusY, color = currentColor) => {
    saveSnapshot(); console.log(`[Draw] ellipse at (${x},${y}) rx=${radiusX} ry=${radiusY} color=${color}`);
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
  const MAX_GRAPH_HISTORY = 10;

  function recordShape(shape, desc) {
    graphList.push({ shape, desc });
    if (graphList.length > MAX_GRAPH_HISTORY) graphList.shift();
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
    recordShape("circle", `圆形(${args[0]},${args[1]}) r=${args[2]} 颜色${args[3]||currentColor}`);
  };
  const _origDrawEllipse = window.drawEllipse;
  window.drawEllipse = (...args) => {
    _origDrawEllipse(...args);
    recordShape("ellipse", `椭圆(${args[0]},${args[1]}) rx=${args[2]} ry=${args[3]} 颜色${args[4]||currentColor}`);
  };
  const _origDrawRect = window.drawRect;
  window.drawRect = (...args) => {
    _origDrawRect(...args);
    recordShape("rect", `矩形(${args[0]},${args[1]}) ${args[2]}x${args[3]} 颜色${args[4]||currentColor}`);
  };
  const _origDrawLine = window.drawLine;
  window.drawLine = (...args) => {
    _origDrawLine(...args);
    recordShape("line", `线段从(${args[0]},${args[1]})到(${args[2]},${args[3]}) 颜色${args[4]||currentColor}`);
  };
  const _origDrawArc = window.drawArc;
  window.drawArc = (...args) => {
    _origDrawArc(...args);
    recordShape("arc", `弧线(${args[0]},${args[1]}) r=${args[2]} 颜色${args[4]||currentColor}`);
  };
  const _origDrawPolygon = window.drawPolygon;
  window.drawPolygon = (points, color) => {
    _origDrawPolygon(points, color);
    if (points && points.length >= 3) {
      const avgX = Math.round(points.reduce((s, p) => s + p.x, 0) / points.length);
      const avgY = Math.round(points.reduce((s, p) => s + p.y, 0) / points.length);
      recordShape("polygon", `多边形中心(${avgX},${avgY}) ${points.length}顶点 颜色${color||currentColor}`);
    }
  };
  const _origClearCanvas = window.clearCanvas;
  window.clearCanvas = () => { _origClearCanvas(); graphList.length = 0; };

  // ── AI Backend Service ─────────────────────────────────
  const AI_API = "http://localhost:8080";
  let aiMode = false;

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
      for (const cmd of actions) {
        const c = cmd.color !== undefined ? cmd.color : currentColor;
        console.log(`[AI] 执行动作: ${cmd.action}`, cmd);

        // Normalize polygon points: support [[x,y],[x,y]] or [{"x":N,"y":N},...]
        let pts = cmd.points;
        if (pts && pts.length > 0 && Array.isArray(pts[0])) {
          pts = pts.map(p => ({ x: p[0], y: p[1] }));
        }

        switch (cmd.action) {
          case "drawCircle":
            if (cmd.radiusX !== undefined || cmd.radiusY !== undefined) {
              drawEllipse(cmd.x ?? 400, cmd.y ?? 300, cmd.radiusX ?? cmd.radius ?? 40, cmd.radiusY ?? cmd.radius ?? 40, c);
            } else {
              drawCircle(cmd.x ?? 400, cmd.y ?? 300, cmd.radius ?? currentRadius, c);
            }
            break;
          case "drawEllipse": case "drawOval":
            drawEllipse(cmd.x ?? 400, cmd.y ?? 300, cmd.radiusX ?? cmd.rx ?? 50, cmd.radiusY ?? cmd.ry ?? 30, c);
            break;
          case "drawRect": drawRect(cmd.x ?? 300, cmd.y ?? 200, cmd.width ?? 80, cmd.height ?? 60, c); break;
          case "drawLine": drawLine(cmd.x1 ?? 200, cmd.y1 ?? 300, cmd.x2 ?? 600, cmd.y2 ?? 300, c); break;
          case "drawPolygon": case "drawTriangle": if (pts) drawPolygon(pts, c); break;
          case "drawArc": drawArc(cmd.x ?? 400, cmd.y ?? 300, cmd.radius ?? 40, cmd.startAngle ?? 0, cmd.endAngle ?? Math.PI, c); break;
          case "setColor": if (cmd.color) currentColor = cmd.color; break;
          case "setSize": if (cmd.size !== undefined && cmd.size !== null) currentRadius = cmd.size; break;
          case "clear": clearCanvas(); break;
        }
      }
      speak(actions.length > 1 ? "绘制完成" : "完成");
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

    // Step 2: misrecognition correction
    const corr = {
      "化缘": "画圆", "花园": "画圆", "花圆": "画圆", "画完": "画圆",
      "举行": "矩形", "巨星": "矩形", "画距型": "画矩形",
      "滑县": "画线", "花线": "画线", "划陷": "画线",
      "昨上": "左上", "幼上": "右上", "昨下": "左下", "幼下": "右下",
      "请空": "清空", "庆功": "清空",
    };
    for (const [w, c] of Object.entries(corr)) text = text.replaceAll(w, c);

    let matched = false;

    // Compound command
    if (!matched) matched = parseCompoundCommand(text);

    // Color
    if (!matched) {
      for (const [kw, val] of Object.entries(colorMap)) {
        if (text.includes(kw)) { currentColor = val; speak(`当前颜色${kw}`); statusEl.textContent = `🎨 颜色：${kw}`; matched = true; break; }
      }
    }

    // Radius
    if (!matched) {
      const rm = text.match(/半径\s*(\d+)/) || text.match(/半径为\s*(\d+)/);
      const cn = !rm && text.match(/半径\s*([零一二三四五六七八九十百千]+)/);
      if (rm) { currentRadius = parseInt(rm[1], 10); speak(`当前半径${currentRadius}`); statusEl.textContent = `📏 半径：${currentRadius}`; matched = true; }
      else if (cn) { const p = parseChineseNumber(cn[1]); if (!isNaN(p)) { currentRadius = p; speak(`当前半径${currentRadius}`); statusEl.textContent = `📏 半径：${currentRadius}`; matched = true; } }
    }

    // Move to numeric
    if (!matched) {
      const mm = text.match(/移动到\s*(\d+)\s*[,，和\s]+\s*(\d+)/);
      if (mm) { moveTo(+mm[1], +mm[2]); statusEl.textContent = `📍 移动到 (${mm[1]}, ${mm[2]})`; matched = true; }
    }

    // LineTo numeric
    if (!matched) {
      const lm = text.match(/连线到\s*(\d+)\s*[,，和\s]+\s*(\d+)/);
      if (lm) { lineTo(+lm[1], +lm[2]); statusEl.textContent = `📏 连线到 (${lm[1]}, ${lm[2]})`; matched = true; }
    }

    // Line expression parser (from→to)
    if (!matched) {
      const lr = parseLineCommand(text);
      if (lr) { drawLine(lr.x1, lr.y1, lr.x2, lr.y2); statusEl.textContent = `📏 ${text.slice(0, 24)}`; matched = true; }
    }

    // Position name → moveTo
    if (!matched) {
      const sorted = [...positionMap].sort((a, b) => b.names[0].length - a.names[0].length);
      for (const e of sorted) {
        if (e.names.some(n => text.includes(n))) { moveTo(e.x, e.y); statusEl.textContent = `📍 ${e.names[0]}`; matched = true; break; }
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
        statusEl.textContent = `📏 向${dn}画线`; matched = true;
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
        statusEl.textContent = `📍 往${dn}`; matched = true;
      }
    }

    // Circle fallback
    if (!matched && ["圆", "圆圈", "圆形"].some(k => text.includes(k))) { drawCircle(400, 300); speak("画圆成功"); statusEl.textContent = "✅ 画圆"; matched = true; }
    // Rectangle fallback
    if (!matched && ["矩形", "长方形", "正方形", "方块"].some(k => text.includes(k))) { drawRect(); speak("画矩形成功"); statusEl.textContent = "✅ 画矩形"; matched = true; }
    // Clear
    if (!matched && ["清空", "清除", "擦掉"].some(k => text.includes(k))) { clearCanvas(); speak("清空成功"); statusEl.textContent = "✅ 已清空"; matched = true; }
    // Undo
    if (!matched && ["撤销", "撤回", "回退", "上一步"].some(k => text.includes(k))) { undo(); statusEl.textContent = "↩️ 已撤销"; matched = true; }
    // Save
    if (!matched && ["保存", "导出", "下载图片"].some(k => text.includes(k))) { saveDrawing(); statusEl.textContent = "💾 已保存"; matched = true; }
    // Redraw / retry
    if (!matched && (text.includes("重新画") || text.includes("重画") || text.includes("重来") || text.includes("重新画一个"))) {
      clearCanvas();
      speak("已清空，重新来");
      statusEl.textContent = "🗑️ 已清空，请重新说"; matched = true;
    }
    // Retry AI (for AI mode: resend same request)
    if (!matched && text.includes("换一个") && aiMode) {
      matched = true; // Don't fall through to "没听清"
    }
    // Fallback
    if (!matched && text) speak("没听清，请再说一遍");
  }

  // ── Elements ──────────────────────────────────────────
  const statusEl = document.getElementById("status");
  const recognizedTextEl = document.getElementById("recognizedText");
  const recordBtn = document.getElementById("recordBtn");
  const aiToggle = document.getElementById("aiToggle");

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
          statusEl.textContent = "🤖 AI 模式已启用";
        } else {
          aiMode = false;
          aiToggle.textContent = "🧠 AI离线";
          aiToggle.classList.add("ai-error");
          setTimeout(() => {
            aiToggle.textContent = "🧠 本地模式";
            aiToggle.classList.remove("ai-error", "ai-active");
          }, 3000);
          statusEl.textContent = "⚠️ AI 后端未启动，使用本地模式";
        }
      } else {
        aiMode = false;
        aiToggle.textContent = "🧠 本地模式";
        aiToggle.classList.remove("ai-active");
        statusEl.textContent = "📡 本地模式";
      }
    });
  }

  // ── Speech Recognition ──────────────────────────────────
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    statusEl.textContent = "❌ 您的浏览器不支持语音识别，请使用 Chrome";
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
      if (aiMode) {
        console.log(`[Step 2] 发送AI: "${lastFinal}"`);
        statusEl.textContent = "🤖 思考中...";
        parseWithAI(lastFinal).then((data) => {
          console.log(`[Step 3] AI返回:`, data);
          // 同时检查 intent 和 actions 数组
          const hasActions = data && ((data.actions && data.actions.length > 0) || (data.commands && data.commands.length > 0));
          const hasIntent = data && data.intent && data.intent !== "UNKNOWN";
          if (hasActions || hasIntent) {
            const ok = executeAIResponse(data);
            if (ok) statusEl.textContent = "✅ 完成";
            else parseLocal(lastFinal);
          } else {
            statusEl.textContent = "🤖 AI未识别，使用本地模式";
            parseLocal(lastFinal);
          }
        });
      } else {
        parseLocal(lastFinal);
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      statusEl.textContent = `❌ 错误：${event.error}`;
      if (event.error === "no-speech" || event.error === "aborted") {
        recordBtn.disabled = false;
        recordBtn.textContent = "🎤 开始语音";
      }
    };

    recognition.onend = () => {
      if (recordBtn.textContent === "⏹ 停止录音") recognition.start();
      else { recordBtn.disabled = false; recordBtn.textContent = "🎤 开始语音"; }
    };

    recordBtn.addEventListener("click", () => {
      if (recordBtn.textContent === "🎤 开始语音") {
        recognition.start();
        recordBtn.textContent = "⏹ 停止录音";
        statusEl.textContent = "🎤 正在聆听...";
      } else {
        recognition.stop();
        recordBtn.textContent = "🎤 开始语音";
        statusEl.textContent = "⏸ 已停止";
      }
    });

    window.recognition = recognition;
  }

  console.log("Voice Draw ready");
});