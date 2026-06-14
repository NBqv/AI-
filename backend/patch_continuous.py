"""Patch script.js to support continuous drawing: \"画个猫再画个花再画个房子\""""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import re

with open('script.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Find the section after pronunciation correction and before erase/move
old = """      // Apply pronunciation correction
      for (const [wrong, correct] of Object.entries(corr)) { lastFinal = lastFinal.replaceAll(wrong, correct); }
      // Try erase/move first"""

new = """      // Apply pronunciation correction
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
                parseLocal(cmd);
              }
              processNextSegment();
            });
          } else {
            parseLocal(cmd);
            processNextSegment();
          }
        }
        processNextSegment();
        return;  // skip the single-command path below
      }

      // Try erase/move first"""

if old in c:
    c = c.replace(old, new, 1)
    print('1. Continuous split + recursive executor inserted')
else:
    print('1. FAIL: pronunciation correction section not found')
    idx = c.find('Apply pronunciation correction')
    if idx >= 0:
        print(repr(c[idx-20:idx+200]))

# Add the splitContinuousCommands function and executeActions helper
# Insert them before the onresult handler
old2 = """  // ── Speech Recognition ──────────────────────────────────"""

new2 = """  // ── Split continuous commands ─────────────────────────
  function splitContinuousCommands(text) {
    // Split on: 再, 然后, 接着, 还, 又 (only between commands, not inside words)
    // Child speech: "画个猫再画个花再画个房子"
    // Also support: "画个猫然后画个花" "画个猫接着画个花"
    var parts = text.split(/[再然后还又](?=画|绘|来|给我|整|搞)/);
    // Filter empty and trim
    var result = [];
    for (var pi = 0; pi < parts.length; pi++) {
      var s = parts[pi].trim();
      if (s) result.push(s);
    }
    // If only one part, also try splitting on 接着/然后/跟/和
    if (result.length <= 1) {
      parts = text.split(/(?:接着|然后|跟|和)(?=画|绘|来|给我|整|搞)/);
      result = [];
      for (var pi = 0; pi < parts.length; pi++) {
        var s = parts[pi].trim();
        if (s) result.push(s);
      }
    }
    // If still only one, try splitting on simple 和 between nouns
    if (result.length <= 1 && text.indexOf("画") >= 0) {
      // "猫和花" -> already handled by individual commands
      // Don't over-split
    }
    return result;
  }

  function executeActions(actions) {
    for (var _i = 0; _i < actions.length; _i++) {
      var cmd = actions[_i];
      var _c = cmd.color !== undefined ? cmd.color : currentColor;
      var pts = cmd.points;
      if (pts && pts.length > 0 && Array.isArray(pts[0])) {
        pts = pts.map(function(p) { return Array.isArray(p) ? {x: p[0], y: p[1]} : p; });
      }
      switch (cmd.action) {
        case "drawCircle":
          if (cmd.radiusX !== undefined || cmd.radiusY !== undefined) {
            drawEllipse(cmd.x || 400, cmd.y || 300, cmd.radiusX || cmd.radius || 40, cmd.radiusY || cmd.radius || 40, _c);
          } else {
            drawCircle(cmd.x || 400, cmd.y || 300, cmd.radius || currentRadius, _c);
          }
          break;
        case "drawEllipse": drawEllipse(cmd.x || 400, cmd.y || 300, cmd.radiusX || 50, cmd.radiusY || 30, _c); break;
        case "drawRect": drawRect(cmd.x || 300, cmd.y || 200, cmd.width || 80, cmd.height || 60, _c); break;
        case "drawLine": drawLine(cmd.x1 || 200, cmd.y1 || 300, cmd.x2 || 600, cmd.y2 || 300, _c); break;
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

  // ── Speech Recognition ──────────────────────────────────"""

if old2 in c:
    c = c.replace(old2, new2, 1)
    print('2. splitContinuousCommands + executeActions inserted')
else:
    print('2. FAIL: Speech Recognition marker not found')
    idx = c.find('Speech Recognition')
    if idx >= 0:
        print(repr(c[idx:idx+80]))

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(c)

opens = c.count('{')
closes = c.count('}')
print(f'Braces: {opens}/{closes}')

# Verify
for kw in ['splitContinuousCommands', 'executeActions', 'processNextSegment']:
    if kw in c:
        print(f'  + {kw}')
    else:
        print(f'  - MISSING: {kw}')
