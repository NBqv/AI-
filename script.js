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

  // ── Drawing Functions ──────────────────────────────────
  window.drawCircle = (x, y, radius, color) => {
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

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          final += transcript;
        } else {
          interim += transcript;
        }
      }

      // Show recognized text in dedicated display area
      const display = final || interim;
      if (display.trim()) {
        recognizedTextEl.textContent = display;
      }

      // ── Voice Command Parsing ─────────────────────────
      const text = event.results[event.results.length - 1][0].transcript
        .toLowerCase()
        .trim();

      if (text.includes("画圆")) {
        drawCircle(400, 300, 40, "black");
        statusEl.textContent = "✅ 画圆";
        speak("画圆成功");
      }

      if (text.includes("清空")) {
        clearCanvas();
        statusEl.textContent = "✅ 已清空";
        speak("清空成功");
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
