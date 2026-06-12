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

  // ── Drawing Functions ──────────────────────────────────
  window.drawCircle = (x, y, radius = currentRadius, color = currentColor) => {
    console.log(`[Draw] circle at (${x},${y}) radius=${radius} color=${color}`);
    ctx.beginPath();
    ctx.arc(x, y, radius, 0, Math.PI * 2);
    ctx.fillStyle = color;
    ctx.fill();
    ctx.closePath();
  };

  window.clearCanvas = () => {
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  };

  window.drawRect = (x = 300, y = 200, width = 100, height = 80, color = currentColor) => {
    console.log(`[Draw] rect at (${x},${y}) ${width}x${height} color=${color}`);
    ctx.fillStyle = color;
    ctx.fillRect(x, y, width, height);
  };

  window.drawLine = (x1 = 200, y1 = 300, x2 = 600, y2 = 300, color = currentColor) => {
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
  };

  window.lineTo = (x, y) => {
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
        "请空": "清空",
        "庆功": "清空",
      };
      for (const [wrong, correct] of Object.entries(correctionMap)) {
        text = text.replaceAll(wrong, correct);
      }

      let matched = false;

      // Color keywords
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

      // Move: "移动到 100,200" / "移动到 100，200"
      const moveMatch = text.match(/移动到\s*(\d+)\s*[,，]\s*(\d+)/);
      if (moveMatch) {
        const x = parseInt(moveMatch[1], 10);
        const y = parseInt(moveMatch[2], 10);
        moveTo(x, y);
        statusEl.textContent = `📍 移动到 (${x}, ${y})`;
        speak(`移动到 ${x}, ${y}`);
        matched = true;
      }

      // LineTo: "连线到 100,200" / "连线到 100，200"
      const lineMatch = text.match(/连线到\s*(\d+)\s*[,，]\s*(\d+)/);
      if (lineMatch) {
        const x = parseInt(lineMatch[1], 10);
        const y = parseInt(lineMatch[2], 10);
        lineTo(x, y);
        statusEl.textContent = `📏 连线到 (${x}, ${y})`;
        speak(`连线到 ${x}, ${y}`);
        matched = true;
      }

      // Circle: match 圆 / 圆圈 / 圆形
      if (["圆", "圆圈", "圆形"].some((kw) => text.includes(kw))) {
        drawCircle(400, 300);
        statusEl.textContent = "✅ 画圆";
        speak("画圆成功");
        matched = true;
      }

      // Rectangle: match 矩形 / 长方形 / 正方形 / 方块
      if (["矩形", "长方形", "正方形", "方块"].some((kw) => text.includes(kw))) {
        drawRect();
        statusEl.textContent = "✅ 画矩形";
        speak("画矩形成功");
        matched = true;
      }

      // Line: match 画线 / 线条 / 直线 / 线段
      if (["画线", "线条", "直线", "线段"].some((kw) => text.includes(kw))) {
        drawLine();
        statusEl.textContent = "✅ 画线";
        speak("画线成功");
        matched = true;
      }

      // Clear: match 清空 / 清除 / 擦掉
      if (["清空", "清除", "擦掉"].some((kw) => text.includes(kw))) {
        clearCanvas();
        statusEl.textContent = "✅ 已清空";
        speak("清空成功");
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
