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

  // ── Drawing Functions ──────────────────────────────────
  window.drawCircle = (x, y, radius = currentRadius, color = currentColor) => {
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

      // Radius: "半径 50", "半径50"
      const radiusMatch = text.match(/半径\s*(\d+)/);
      if (radiusMatch) {
        currentRadius = parseInt(radiusMatch[1], 10);
        statusEl.textContent = `📏 半径：${currentRadius}`;
        speak(`当前半径${currentRadius}`);
        matched = true;
      }

      // Circle: match 圆 / 圆圈 / 圆形
      if (["圆", "圆圈", "圆形"].some((kw) => text.includes(kw))) {
        drawCircle(400, 300);
        statusEl.textContent = "✅ 画圆";
        speak("画圆成功");
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
