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
      if (ch === "十") {
        result += (temp || 1) * 10;
        temp = 0;
      } else if (ch === "百") {
        result += (temp || 1) * 100;
        temp = 0;
      } else if (ch === "千") {
        result += (temp || 1) * 1000;
        temp = 0;
      } else if (chineseDigit[ch] !== undefined) {
        temp = chineseDigit[ch];
      }
    }

    result += temp;
    return result || NaN;
  }

  // ── Position Name Map ──────────────────────────────────
  const positionMap = [
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
    for (const [key, vec] of Object.entries(directionMap)) {
      if (text.includes(key)) return vec;
    }
    return null;
  }

  function getStep(text) {
    if (text.includes("一点点") || text.includes("一点")) return 10;
    if (text.includes("一大步") || text.includes("很多")) return 50;
    return defaultStep;
  }

  // ── Line Expression Parser ─────────────────────────────
  // Extensible: add patterns here as needed
  const lineActionPrefixes = ["画一条", "画条", "画一根", "绘制", "拉一条", "拉"];
  const lineActionSuffixes = ["线条"];

  // Check if text is a line command; return the "clean" text (from→to part)
  function detectLineCommand(text) {
    // Only trigger on explicit line intent
    const hasPrefix = lineActionPrefixes.some((p) => text.includes(p));
    const hasSuffix = lineActionSuffixes.some((s) => text.includes(s));
    const hasSimple = text.includes("画线") || text.includes("连线");

    if (!hasPrefix && !hasSuffix && !hasSimple) return null;

    // Strip known noise to expose the from→to pattern
    let clean = text;
    for (const p of [...lineActionPrefixes].sort((a, b) => b.length - a.length)) {
      clean = clean.replace(p, "");
    }
    for (const s of [...lineActionSuffixes].sort((a, b) => b.length - a.length)) {
      clean = clean.replace(s, "");
    }
    // Strip "画线" / "连线" (may appear after from→to)
    clean = clean.replace("画线", "").replace("连线", "");
    // Strip trailing "的线" or "线" at end ("从A到B的线" → "从A到B")
    clean = clean.replace(/的?线$/, "");
    clean = clean.trim();
    return clean || "";
  }

  // Resolve a position description like "左上角", "100,200", "100 200" to {x,y}
  function resolvePosition(desc) {
    if (!desc) return null;
    const d = desc.trim();

    // 1. Try position name map (longest match first)
    const sorted = [...positionMap].sort((a, b) => b.names[0].length - a.names[0].length);
    for (const entry of sorted) {
      if (entry.names.some((n) => d.includes(n))) return { x: entry.x, y: entry.y };
    }

    // 2. Try numeric "100,200", "100 200", "100，200", "100和200"
    const numMatch = d.match(/(\d+)\s*[,，和\s]+\s*(\d+)/);
    if (numMatch) return { x: parseInt(numMatch[1], 10), y: parseInt(numMatch[2], 10) };

    // 3. Try single digit "100 200" (no separator)
    const seqMatch = d.match(/^(\d{2,3})\s*(\d{2,3})$/);
    if (seqMatch) return { x: parseInt(seqMatch[1], 10), y: parseInt(seqMatch[2], 10) };

    return null;
  }

  // Main line parser
  function parseLineCommand(text) {
    const clean = detectLineCommand(text);
    if (clean === null) return null;

    console.log(`[LineParser] text="${text}" clean="${clean}"`);

    let fromDesc = null;
    let toDesc = null;

    // Try "从X到Y" first, then "X到Y" (no 从)
    const pattern1 = clean.match(/从\s*(.+?)\s*(?:到|至|往)\s*(.+)/);
    const pattern2 = !pattern1 && clean.match(/(.+?)\s*(?:到|至|往)\s*(.+)/);

    if (pattern1) {
      fromDesc = pattern1[1].trim();
      toDesc = pattern1[2].trim();
    } else if (pattern2) {
      fromDesc = pattern2[1].trim();
      toDesc = pattern2[2].trim();
    }

    if (!fromDesc || !toDesc) {
      // Bare "画线" / "连线" with no from→to → use defaults
      if (!clean) return { x1: 200, y1: 300, x2: 600, y2: 300 };
      // Has content but no from→to pattern (e.g., "向左画线") → defer
      return null;
    }

    // Resolve positions
    const from = resolvePosition(fromDesc);
    const to = resolvePosition(toDesc);

    if (from && to) {
      console.log(`[LineParser] (${from.x},${from.y}) → (${to.x},${to.y})`);
      return { x1: from.x, y1: from.y, x2: to.x, y2: to.y };
    }

    if (to) {
      console.log(`[LineParser] partial: current → (${to.x},${to.y})`);
      return { x1: currentX, y1: currentY, x2: to.x, y2: to.y };
    }

    return null;
  }

  // ── Color Map (global for compound parser) ───────────────
  const colorMap = {
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

  // ── Shape Keywords ──────────────────────────────────────
  const shapeMap = {
    circle: ["圆", "圆形", "圆圈"],
    rect: ["矩形", "长方形", "正方形", "方块"],
    line: ["线", "线条", "直线"],
  };

  // ── Compound Command Parser ──────────────────────────────
  // Handles: "在左上角画一个红色的圆", "画一个蓝色矩形在中心", etc.
  function parseCompoundCommand(text) {
    // ── Step 1: Detect shape ──────────────────────────────
    let shape = null;
    for (const [type, keywords] of Object.entries(shapeMap)) {
      if (keywords.some((kw) => text.includes(kw))) {
        shape = type;
        break;
      }
    }
    if (!shape) return null;
    // Exclude "线条"/"直线" if they're part of a line command
    if (shape === "line") {
      // Check if this looks like a line with from→to
      if (text.includes("从") && (text.includes("到") || text.includes("至"))) return null;
      // If it contains directional drawing keywords, defer
      if (text.includes("向") && (text.includes("画") || text.includes("移"))) return null;
    }

    console.log(`[CompoundParser] shape=${shape} text="${text}"`);

    // ── Step 2: Extract position ──────────────────────────
    let pos = null;
    const sortedPos = [...positionMap].sort((a, b) => b.names[0].length - a.names[0].length);
    for (const entry of sortedPos) {
      if (entry.names.some((n) => text.includes(n))) {
        pos = { x: entry.x, y: entry.y };
        break;
      }
    }
    // Also try numeric position: "在 100,200 画一个圆"
    if (!pos) {
      const numPos = text.match(/在\s*(\d+)\s*[,，和\s]+\s*(\d+)/);
      if (numPos) pos = { x: parseInt(numPos[1], 10), y: parseInt(numPos[2], 10) };
    }

    // ── Step 3: Extract color ─────────────────────────────
    let color = null;
    let colorName = null;
    for (const [kw, val] of Object.entries(colorMap)) {
      if (text.includes(kw)) {
        color = val;
        colorName = kw;
        break;
      }
    }

    // ── Step 4: Save state & execute ─────────────────────
    const savedColor = currentColor;
    const savedX = currentX;
    const savedY = currentY;

    // Set color if provided
    if (color) currentColor = color;

    // Default position to center if not specified
    const drawX = pos ? pos.x : 400;
    const drawY = pos ? pos.y : 300;

    // Draw based on shape
    if (shape === "circle") {
      drawCircle(drawX, drawY);
      const col = colorName || "当前颜色";
      const loc = pos ? `在${sortedPos.find((e) => e.names.some((n) => text.includes(n)))?.names[0] || "当前位置"}` : "";
      statusEl.textContent = `✅ ${loc}画${col}圆`;
      speak(`画${col}圆成功`);
      return true;
    }

    if (shape === "rect") {
      drawRect(drawX - 50, drawY - 40, 100, 80);
      const col = colorName || "当前颜色";
      statusEl.textContent = `✅ 画${col}矩形`;
      speak(`画${col}矩形成功`);
      return true;
    }

    if (shape === "line") {
      // For compound "line", draw from current to position or a fixed horizontal
      const lineX1 = pos ? drawX : 200;
      const lineY1 = pos ? drawY : 300;
      const lineX2 = pos ? drawX + 200 : 600;
      const lineY2 = pos ? drawY : 300;
      drawLine(lineX1, lineY1, lineX2, lineY2);
      statusEl.textContent = `✅ 画线`;
      speak("画线成功");
      return true;
    }

    return false;
  }

  // ── Drawing Functions ──────────────────────────────────
  window.drawCircle = (x, y, radius = currentRadius, color = currentColor) => {
    saveSnapshot();
    console.log(`[Draw] circle at (${x},${y}) radius=${radius} color=${color}`);
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.closePath();
  };

  window.clearCanvas = () => {
    saveSnapshot();
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  };

  window.drawRect = (x = 300, y = 200, width = 100, height = 80, color = currentColor) => {
    saveSnapshot();
    console.log(`[Draw] rect at (${x},${y}) ${width}x${height} color=${color}`);
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
  };

  window.drawLine = (x1 = 200, y1 = 300, x2 = 600, y2 = 300, color = currentColor) => {
    saveSnapshot();
    console.log(`[Draw] line from (${x1},${y1}) to (${x2},${y2}) color=${color}`);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.closePath();
  };

  window.moveTo = (x, y) => {
    currentX = x;
    currentY = y;
    console.log(`[Move] cursor to (${currentX},${currentY})`);
    // Draw a small dot as visual cursor
    ctx.fillStyle = "#999";
    ctx.beginPath();
    ctx.arc(currentX, currentY, 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.closePath();
    speak(`已移动到X${Math.round(currentX)}，Y${Math.round(currentY)}`);
  };

  window.lineTo = (x, y) => {
    saveSnapshot();
    console.log(`[Line] from (${currentX},${currentY}) to (${x},${y})`);
    ctx.beginPath();
    ctx.moveTo(currentX, currentY);
    ctx.lineTo(x, y);
    ctx.strokeStyle = currentColor;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.closePath();
    currentX = x;
    currentY = y;
    speak(`已连线到X${Math.round(currentX)}，Y${Math.round(currentY)}`);
  };

  // ── Speech Synthesis Helper ────────────────────────────
  window.speak = (text) => {
    if (!window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "zh-CN";
    speechSynthesis.speak(utterance);
  };

  // ── Elements ────────────────────────────────────────────
  const statusEl = document.getElementById("status");
  const recognizedTextEl = document.getElementById("recognizedText");
  const recordBtn = document.getElementById("recordBtn");

  // ── Speech Recognition ──────────────────────────────────
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    statusEl.textContent = "❌ 您的浏览器不支持语音识别，请使用 Chrome";
    recordBtn.disabled = true;
  } else {
    const recognition = new SpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.lang = "zh-CN";

    // ── Recognition Events ──────────────────────────────
    recognition.onresult = (event) => {
      let interim = "";
      let final = "";
      let lastFinal = "";

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
          lastFinal = transcript;
        } else {
          interim += transcript;
        }
      }

      // Show recognized text in dedicated display area
      const display = final || interim;
      if (display.trim()) {
        recognizedTextEl.textContent = display;
      }

      // Only process final results for commands
      if (!lastFinal) return;

      // ── Voice Command Parsing ─────────────────────────
      let text = lastFinal.toLowerCase().trim();

      // Remove filler words before matching
      const fillerWords = ["嗯", "啊", "哦", "吧", "的", "了", "嘛", "呀", "啦",
        "一个", "给我", "帮我", "这个", "那个", "一下", "一下下"];
      for (const word of fillerWords) {
        text = text.replaceAll(word, "");
      }
      text = text.trim();

      // Misrecognition correction map
      const correctionMap = {
        "化缘": "画圆",
        "花园": "画圆",
        "花圆": "画圆",
        "画完": "画圆",
        "举行": "矩形",
        "巨星": "矩形",
        "画距型": "画矩形",
        "滑县": "画线",
        "花线": "画线",
        "划陷": "画线",
        "昨上": "左上",
        "幼上": "右上",
        "昨下": "左下",
        "幼下": "右下",
        "请空": "清空",
        "庆功": "清空",
      };
      for (const [wrong, correct] of Object.entries(correctionMap)) {
        text = text.replaceAll(wrong, correct);
      }

      let matched = false;

      // ── Compound Command Parser ─────────────────────────
      // Handles: "在左上角画一个红色的圆", "画一个蓝色矩形在中心"
      // Runs before individual color/shape/position parsers
      if (!matched) {
        matched = parseCompoundCommand(text);
      }

      // Color keywords
      for (const [kw, val] of Object.entries(colorMap)) {
        if (text.includes(kw)) {
          currentColor = val;
          statusEl.textContent = `🎨 颜色：${kw}`;
          speak(`当前颜色${kw}`);
          matched = true;
          break;
        }
      }

      // Radius: "半径 50", "半径50", "半径为50", "半径八十", "半径为八十"
      const radiusMatch = text.match(/半径\s*(\d+)/) || text.match(/半径为\s*(\d+)/);
      const cnRadiusMatch = !radiusMatch && (
        text.match(/半径\s*([零一二三四五六七八九十百千]+)/) ||
        text.match(/半径为\s*([零一二三四五六七八九十百千]+)/)
      );
      if (radiusMatch) {
        currentRadius = parseInt(radiusMatch[1], 10);
        console.log(`[Voice] radius set to ${currentRadius}`);
        statusEl.textContent = `📏 半径：${currentRadius}`;
        speak(`当前半径${currentRadius}`);
        matched = true;
      } else if (cnRadiusMatch) {
        const parsed = parseChineseNumber(cnRadiusMatch[1]);
        if (!isNaN(parsed)) {
          currentRadius = parsed;
          console.log(`[Voice] radius set to ${currentRadius} (from Chinese number)`);
          statusEl.textContent = `📏 半径：${currentRadius}`;
          speak(`当前半径${currentRadius}`);
          matched = true;
        }
      }

      // Move: "移动到 100,200" / "移动到 100 200" / "移动到 100和200"
      const moveMatch = text.match(/移动到\s*(\d+)\s*[,，和\s]+\s*(\d+)/);
      if (moveMatch) {
        const x = parseInt(moveMatch[1], 10);
        const y = parseInt(moveMatch[2], 10);
        moveTo(x, y);
        statusEl.textContent = `📍 移动到 (${x}, ${y})`;
        matched = true;
      }

      // LineTo: "连线到 500,400" / "连线到 500 400" / "连线到 500和400"
      const lineMatch = text.match(/连线到\s*(\d+)\s*[,，和\s]+\s*(\d+)/);
      if (lineMatch) {
        const x = parseInt(lineMatch[1], 10);
        const y = parseInt(lineMatch[2], 10);
        lineTo(x, y);
        statusEl.textContent = `📏 连线到 (${x}, ${y})`;
        matched = true;
      }

      // ── Line Expression Parser ──────────────────────────
      // Must fire BEFORE Step 1: "从左上角到右下角画线" contains "左上角"
      // but should be handled as a line, not a moveTo.
      if (!matched) {
        const lineResult = parseLineCommand(text);
        if (lineResult) {
          drawLine(lineResult.x1, lineResult.y1, lineResult.x2, lineResult.y2);
          const shown = text.replace(/[的啊吧哦啦嗯呀]/g, "").trim().slice(0, 24);
          statusEl.textContent = `📏 ${shown}`;
          matched = true;
        }
      }

      // ── Step 1: Position Name → moveTo ──────────────────
      if (!matched) {
        for (const entry of positionMap) {
          if (entry.names.some((n) => text.includes(n))) {
            moveTo(entry.x, entry.y);
            statusEl.textContent = `📍 ${entry.names[0]}`;
            matched = true;
            break;
          }
        }
      }

      // ── Step 3: Directional line (e.g., "向左画线", "往右上画") ──
      if (!matched) {
        const combinedDirs = {
          "左上": { dx: -1, dy: -1 }, "左下": { dx: -1, dy: 1 },
          "右上": { dx: 1, dy: -1 }, "右下": { dx: 1, dy: 1 },
        };
        let dir = null;
        // Check combined first
        for (const [key, vec] of Object.entries(combinedDirs)) {
          if (text.includes(key)) { dir = vec; break; }
        }
        if (!dir) dir = getDirection(text);
        const wantsDraw = text.includes("画线") || text.includes("画条") || text.includes("画一根");
        if (dir && wantsDraw) {
          const lineLen = text.includes("一点") ? 50 : text.includes("很多") ? 150 : 100;
          const nx = currentX + dir.dx * lineLen;
          const ny = currentY + dir.dy * lineLen;
          lineTo(nx, ny);
          const dirName = Object.keys(directionMap).find((d) => text.includes(d)) || "斜";
          statusEl.textContent = `📏 向${dirName}画线`;
          matched = true;
        }
      }

      // ── Step 2: Relative direction move ─────────────────
      // Combined direction support (Step 4): 左+上, 右+下 etc.
      if (!matched) {
        const combinedDirs = {
          "左上": { dx: -1, dy: -1 }, "左下": { dx: -1, dy: 1 },
          "右上": { dx: 1, dy: -1 }, "右下": { dx: 1, dy: 1 },
        };
        let dir = null;
        let dirName = null;
        // Check combined first (e.g., "往左上走")
        for (const [key, vec] of Object.entries(combinedDirs)) {
          if (text.includes(key)) { dir = vec; dirName = key; break; }
        }
        // Fallback to single direction
        if (!dir) {
          for (const [key, vec] of Object.entries(directionMap)) {
            if (text.includes(key)) { dir = vec; dirName = key; break; }
          }
        }
        const hasMoveWord = dir && (
          text.includes("往") || text.includes("向") || text.includes("移") || text.includes("走")
        );
        if (hasMoveWord) {
          const step = getStep(text);
          const nx = Math.round(currentX + dir.dx * step);
          const ny = Math.round(currentY + dir.dy * step);
          moveTo(nx, ny);
          statusEl.textContent = `📍 往${dirName} (${nx}, ${ny})`;
          matched = true;
        }
      }

      // Circle: match 圆 / 圆圈 / 圆形 (fallback if compound parser missed)
      if (!matched && ["圆", "圆圈", "圆形"].some((kw) => text.includes(kw))) {
        drawCircle(400, 300);
        statusEl.textContent = "✅ 画圆";
        speak("画圆成功");
        matched = true;
      }

      // Rectangle: match 矩形 / 长方形 / 正方形 / 方块 (fallback)
      if (!matched && ["矩形", "长方形", "正方形", "方块"].some((kw) => text.includes(kw))) {
        drawRect();
        statusEl.textContent = "✅ 画矩形";
        speak("画矩形成功");
        matched = true;
      }

      // Clear: match 清空 / 清除 / 擦掉
      if (["清空", "清除", "擦掉"].some((kw) => text.includes(kw))) {
        clearCanvas();
        statusEl.textContent = "✅ 已清空";
        speak("清空成功");
        matched = true;
      }

      // Undo: match 撤销 / 撤回 / 回退 / 上一步
      if (!matched && ["撤销", "撤回", "回退", "上一步"].some((kw) => text.includes(kw))) {
        undo();
        statusEl.textContent = "↩️ 已撤销";
        matched = true;
      }

      // Save: match 保存 / 导出 / 下载
      if (!matched && ["保存", "导出", "下载图片"].some((kw) => text.includes(kw))) {
        saveDrawing();
        statusEl.textContent = "💾 已保存";
        matched = true;
      }

      // Fallback: no command matched
      if (!matched && text) {
        speak("没听清，请再说一遍");
      }
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      statusEl.textContent = `❌ 错误：${event.error}`;

      // Re-enable button on non-fatal errors
      if (event.error === "no-speech" || event.error === "aborted") {
        recordBtn.disabled = false;
        recordBtn.textContent = "🎤 开始语音";
      }
    };

    recognition.onend = () => {
      // Auto-restart if button still indicates recording
      if (recordBtn.textContent === "⏹ 停止录音") {
        recognition.start();
      } else {
        recordBtn.disabled = false;
        recordBtn.textContent = "🎤 开始语音";
      }
    };

    // ── Recording Toggle ─────────────────────────────────
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

    // ── Global Reference ─────────────────────────────────
    window.recognition = recognition;
  }

  console.log("Voice Draw ready");
});
