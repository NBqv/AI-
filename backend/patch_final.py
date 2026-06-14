"""Final patch: relative positioning support in script.js"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('script.js', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Add lastTemplateName variable
old1 = '  const graphList = [];\n\n  const MAX_GRAPH_HISTORY = 10;\n\n  // Store loaded complex_shapes templates'
new1 = '  const graphList = [];\n  var lastTemplateName = "";\n\n  const MAX_GRAPH_HISTORY = 10;\n\n  // Store loaded complex_shapes templates'
c = c.replace(old1, new1, 1)
print('1 OK')

# 2. Insert composite recording after speak
old2 = 'speak(actions.length > 1 ? "绘制完成" : "完成");\n\n      return true;\n\n    }\n\n\n\n    //'
new2 = ('speak(actions.length > 1 ? "绘制完成" : "完成");\n'
        + '      if (lastTemplateName) {\n'
        + '        var _sx = 0, _sy = 0, _sc = 0;\n'
        + '        for (var _ri = 0; _ri < graphList.length; _ri++) {\n'
        + '          var _g = graphList[_ri];\n'
        + '          if (_g.cx != null) { _sx += _g.cx; _sy += _g.cy; _sc++; }\n'
        + '        }\n'
        + '        if (_sc > 0) recordShape(lastTemplateName, "模板:" + lastTemplateName, Math.round(_sx/_sc), Math.round(_sy/_sc));\n'
        + '        lastTemplateName = "";\n'
        + '      }\n'
        + '\n      return true;\n\n    }\n\n\n\n    //')
c = c.replace(old2, new2, 1)
print('2 OK')

# 3. Set lastTemplateName in onresult handler
idx = c.find('if (hasActions || hasIntent)')
if idx >= 0:
    old3 = c[idx:idx + 200]
    # Find the line containing "const ok = executeAIResponse(data);"
    lines = old3.split('\n')
    for i, line in enumerate(lines):
        if 'const ok = executeAIResponse(data);' in line:
            indent = line[:len(line) - len(line.lstrip())]
            insert_line = indent + 'if (data.backend && data.backend.indexOf("template:") === 0) {\n'
            insert_line += indent + '  lastTemplateName = data.backend.replace("template:", "");\n'
            insert_line += indent + '}\n'
            lines.insert(i, insert_line)
            break
    c = c[:idx] + '\n'.join(lines) + c[idx + 200:]
    print('3 OK')
else:
    print('3 FAIL')

with open('script.js', 'w', encoding='utf-8') as f:
    f.write(c)
print('\nAll done')
