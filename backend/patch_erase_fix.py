"""Patch erase function to use _batch_start markers"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('script.js', 'r', encoding='utf-8') as f:
    c = f.read()

# Replace the eraseShapeByKeyword function with a better version
old_fn_start = '  function eraseShapeByKeyword(keyword) {'
old_fn_end = '    return true;\n  }'

# Find the function
idx = c.find(old_fn_start)
if idx >= 0:
    # Find the matching end (return true;\n  } pattern)
    fn_end = c.find('\n  function parseEraseMoveCommand', idx)
    if fn_end < 0:
        fn_end = c.find('\n  // ──', idx)

    print(f'Found eraseShapeByKeyword at {idx}, ends at {fn_end}')

    new_fn = '''  function eraseShapeByKeyword(keyword) {
    // Find shape batch marker in actionHistory
    var markerIdx = -1;
    var markerName = "";
    for (var hi = 0; hi < actionHistory.length; hi++) {
      var entry = actionHistory[hi];
      if (entry.fn === "_batch_start") {
        var desc = entry.desc || "";
        if (desc.indexOf(keyword) >= 0 || desc.indexOf("模板开始:") >= 0) {
          markerIdx = hi;
          markerName = desc.replace("模板开始:", "");
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
'''

    before = c[:idx]
    after = c[fn_end:]
    c = before + new_fn + after
    print('OK erase function replaced')
else:
    print('FAIL: erase function not found')
    eidx = c.find('eraseShapeByKeyword')
    if eidx >= 0:
        print('Found at', eidx, ':')
        print(repr(c[eidx:eidx+200]))

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')
