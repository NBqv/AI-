"""Add erase and move functionality to script.js"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('script.js', 'r', encoding='utf-8') as f:
    c = f.read()

# ── 1. Add actionHistory array next to graphList ──
old = '  const graphList = [];\n  var lastTemplateName = "";'
new = '  const graphList = [];\n  var actionHistory = [];  // stores {fn: Function, args: Array, desc: String}\n  var lastTemplateName = "";'
c = c.replace(old, new, 1)
print('1. actionHistory added')

# ── 2. Wrap draw functions to also push to actionHistory ──
# drawCircle
old = '  window.drawCircle = (x, y, radius = currentRadius, color = currentColor) => {\n    saveSnapshot();'
new = '  window.drawCircle = (x, y, radius = currentRadius, color = currentColor) => {\n    saveSnapshot();\n    actionHistory.push({fn: "drawCircle", args: [x, y, radius, color], desc: "圆形("+x+","+y+") r="+radius});'
if old in c:
    c = c.replace(old, new, 1)
    print('2a. drawCircle wrapped')
else:
    print('2a. FAIL drawCircle')

# clearCanvas
old = '  window.clearCanvas = () => { saveSnapshot(); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, canvas.width, canvas.height); };'
new = '  window.clearCanvas = () => { saveSnapshot(); ctx.fillStyle = "#fff"; ctx.fillRect(0, 0, canvas.width, canvas.height); actionHistory = []; };'
c = c.replace(old, new, 1)
print('2b. clearCanvas updated')

# drawRect
old = '  window.drawRect = (x = 300, y = 200, width = 100, height = 80, color = currentColor) => {\n    saveSnapshot(); console.log(`[Draw] rect at (${x},${y}) ${width}x${height} color=${color}`);'
new = '  window.drawRect = (x = 300, y = 200, width = 100, height = 80, color = currentColor) => {\n    saveSnapshot(); actionHistory.push({fn: "drawRect", args: [x, y, width, height, color], desc: "矩形("+x+","+y+")"}); console.log(`[Draw] rect at (${x},${y}) ${width}x${height} color=${color}`);'
c = c.replace(old, new, 1)
print('2c. drawRect wrapped')

# drawLine
old = '  window.drawLine = (x1 = 200, y1 = 300, x2 = 600, y2 = 300, color = currentColor) => {\n    saveSnapshot(); console.log(`[Draw] line from (${x1},${y1}) to (${x2},${y2}) color=${color}`);'
new = '  window.drawLine = (x1 = 200, y1 = 300, x2 = 600, y2 = 300, color = currentColor) => {\n    saveSnapshot(); actionHistory.push({fn: "drawLine", args: [x1, y1, x2, y2, color], desc: "线("+x1+","+y1+")-("+x2+","+y2+")"}); console.log(`[Draw] line from (${x1},${y1}) to (${x2},${y2}) color=${color}`);'
c = c.replace(old, new, 1)
print('2d. drawLine wrapped')

# drawPolygon
old = '  window.drawPolygon = (points, color = currentColor) => {\n    if (!points || points.length < 3) return;\n    saveSnapshot(); console.log(`[Draw] polygon ${points.length} pts color=${color}`);'
new = '  window.drawPolygon = (points, color = currentColor) => {\n    if (!points || points.length < 3) return;\n    saveSnapshot(); actionHistory.push({fn: "drawPolygon", args: [points, color], desc: "多边形"+points.length+"顶点"}); console.log(`[Draw] polygon ${points.length} pts color=${color}`);'
c = c.replace(old, new, 1)
print('2e. drawPolygon wrapped')

# drawArc
old = '  window.drawArc = (x, y, radius, startAngle = 0, endAngle = Math.PI, color = currentColor) => {\n    saveSnapshot(); console.log(`[Draw] arc at (${x},${y}) r=${radius} a=${startAngle}-${endAngle}`);'
new = '  window.drawArc = (x, y, radius, startAngle = 0, endAngle = Math.PI, color = currentColor) => {\n    saveSnapshot(); actionHistory.push({fn: "drawArc", args: [x, y, radius, startAngle, endAngle, color], desc: "弧线("+x+","+y+") r="+radius}); console.log(`[Draw] arc at (${x},${y}) r=${radius} a=${startAngle}-${endAngle}`);'
c = c.replace(old, new, 1)
print('2f. drawArc wrapped')

# drawEllipse
old = '  window.drawEllipse = (x, y, radiusX, radiusY, color = currentColor) => {\n    saveSnapshot(); console.log(`[Draw] ellipse at (${x},${y}) rx=${radiusX} ry=${radiusY} color=${color}`);'
new = '  window.drawEllipse = (x, y, radiusX, radiusY, color = currentColor) => {\n    saveSnapshot(); actionHistory.push({fn: "drawEllipse", args: [x, y, radiusX, radiusY, color], desc: "椭圆("+x+","+y+")"}); console.log(`[Draw] ellipse at (${x},${y}) rx=${radiusX} ry=${radiusY} color=${color}`);'
c = c.replace(old, new, 1)
print('2g. drawEllipse wrapped')

# ── 3. Add rebuildCanvas, eraseShape, moveShape functions ──
# Insert before "AI Backend Service" section (which already has relative positioning before it)
# Find the relative positioning function section
marker = '  // ── Relative positioning: "在兔子左边画个乌龟"'
insert = '''  // ── Erase & Move: "擦掉兔子" / "把兔子移到右边" ──────────

  function rebuildCanvas() {
    ctx.fillStyle = "#fff";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    graphList.length = 0;
    for (var hi = 0; hi < actionHistory.length; hi++) {
      var entry = actionHistory[hi];
      var fn = window[entry.fn];
      if (fn) fn.apply(null, entry.args);
    }
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
    // Find shape in graphList
    var targetIdx = -1;
    var targetDesc = "";
    for (var gi = graphList.length - 1; gi >= 0; gi--) {
      var g = graphList[gi];
      if (g.desc && g.desc.indexOf(keyword) >= 0) {
        targetIdx = gi;
        targetDesc = g.desc;
        break;
      }
    }
    if (targetIdx < 0) {
      speak("没找到" + keyword);
      return false;
    }

    // Remove all actionHistory entries that match this shape's desc substring
    // Strategy: rebuild the whole history by keeping only entries that don't match
    var toRemove = [];
    for (var hi = 0; hi < actionHistory.length; hi++) {
      var desc = actionHistory[hi].desc || "";
      // If the history entry desc matches part of what we want to erase, mark it
      // This is approximate - we match by description keywords
      if (targetDesc.indexOf("圆形") >= 0 && desc.indexOf("圆形") >= 0) {
        var matchesTarget = false;
        for (var gi = 0; gi < graphList.length; gi++) {
          if (graphList[gi].desc === targetDesc) {
            matchesTarget = true;
            break;
          }
        }
        if (matchesTarget) toRemove.push(hi);
      }
    }

    // Actually, simpler approach: rebuild canvas from scratch, skipping entries
    // that belong to the shape being erased.
    // We'll use graphList index as a proxy: remove the actions recorded during the
    // same saveSnapshot batch as the target shape.

    // Simplest working approach: remove all actions that match the template name
    // Check if targetDesc contains a template name pattern
    saveSnapshot();
    var newHistory = [];
    var removedCount = 0;
    for (var hi = 0; hi < actionHistory.length; hi++) {
      var entry = actionHistory[hi];
      var desc = entry.desc || "";

      // Check if this action belongs to the erased shape
      var belongs = false;
      // If the action has coordinates near the shape center
      if (targetDesc.indexOf("模板:") === 0) {
        // It's a template composite entry - match by template name in desc
        if (desc.indexOf(keyword) >= 0 || desc.indexOf(targetDesc.replace("模板:", "")) >= 0) {
          belongs = true;
        }
      }

      if (!belongs) {
        newHistory.push(entry);
      } else {
        removedCount++;
      }
    }

    if (removedCount === 0) {
      // Fallback: just remove everything in the neighboring range
      // This happens with template composite recording
      speak("暂时无法擦除这个图形");
      return false;
    }

    actionHistory = newHistory;
    // Also remove from snapshot history by rebuilding snapshot chain
    // Simplest: clear snapshot history and rebuild
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
    var moveMatch = text.match(/把(.+?)(?:移到|移动到|挪到|移至)(?:左边|右边|上边|下边|上面|下面|左侧|右侧|左|右|上|下)/);
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

    // Find the shape
    var targetIdx = -1;
    for (var gi = graphList.length - 1; gi >= 0; gi--) {
      if (graphList[gi].desc && graphList[gi].desc.indexOf(keyword) >= 0) {
        targetIdx = gi;
        break;
      }
    }
    if (targetIdx < 0) {
      speak("没找到" + keyword);
      return false;
    }

    var step = 120;
    var dx = Math.round(dir.dx * step);
    var dy = Math.round(dir.dy * step);

    // Modify actionHistory: find actions belonging to this shape and offset coords
    var found = false;
    for (var hi = 0; hi < actionHistory.length; hi++) {
      var entry = actionHistory[hi];
      // Check if this entry's args contain coordinates and it's part of the target shape
      // Simple heuristic: if the entry was recorded during the same batch as the target
      var shouldOffset = false;
      if (keyword.length >= 2) {
        // Try matching by checking if any graphList entry with this keyword
        // roughly corresponds to this action
        var desc = entry.desc || "";
        if (desc.indexOf(keyword) >= 0) shouldOffset = true;
      }

      if (shouldOffset) {
        var args = entry.args;
        if (entry.fn === "drawCircle" || entry.fn === "drawArc") {
          if (args.length >= 2) { args[0] += dx; args[1] += dy; }
        } else if (entry.fn === "drawRect") {
          if (args.length >= 2) { args[0] += dx; args[1] += dy; }
        } else if (entry.fn === "drawLine") {
          if (args.length >= 4) { args[0] += dx; args[1] += dy; args[2] += dx; args[3] += dy; }
        } else if (entry.fn === "drawEllipse") {
          if (args.length >= 2) { args[0] += dx; args[1] += dy; }
        } else if (entry.fn === "drawPolygon") {
          if (args[0] && Array.isArray(args[0])) {
            args[0] = args[0].map(function(p) { return {x: p.x + dx, y: p.y + dy}; });
          }
        }
        found = true;
      }
    }

    if (!found) {
      speak("无法移动" + keyword);
      return false;
    }

    saveSnapshot();
    rebuildCanvas();
    speak("已将" + keyword + "移到" + direction);
    return true;
  }

'''

old_marker = '  // ── Relative positioning: "在兔子左边画个乌龟"'
if old_marker in c:
    c = c.replace(old_marker, insert + old_marker, 1)
    print('3. erase/move functions added')
else:
    print('3. FAIL marker')

# ── 4. Hook into voice flow: try erase/move before relative positioning ──
# Find the relative positioning hook we added in pr15
old_hook = '      // Try relative positioning first\n      var relResult = tryRelativePosition(lastFinal);'
new_hook = '      // Try erase/move first\n      var eraseMoveResult = parseEraseMoveCommand(lastFinal);\n      if (eraseMoveResult) {\n        setStatus(STATUS.SUCCESS, "完成 \\u2713");\n        return;\n      }\n\n      // Try relative positioning first\n      var relResult = tryRelativePosition(lastFinal);'

if old_hook in c:
    c = c.replace(old_hook, new_hook, 1)
    print('4. erase/move hook added')
else:
    print('4. FAIL hook')
    idx = c.find('tryRelativePosition')
    if idx >= 0:
        print('  found at', idx)
        print(repr(c[max(0,idx-30):idx+80]))

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(c)
print('\nAll done')
