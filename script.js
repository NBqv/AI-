/**
 * Voice Draw — Main Entry
 */

// ── DOM Ready ──────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // ── Canvas Setup ────────────────────────────────────────
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");

  // Ensure canvas buffer matches CSS size (avoid blurring)
  canvas.width = 800;
  canvas.height = 600;

  // Fill background white
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // ── Global References ──────────────────────────────────
  window.ctx = ctx;
  window.canvas = canvas;

  console.log("Voice Draw ready");
});
