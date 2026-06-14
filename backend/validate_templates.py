"""
模板验证器：检查 aliases.json 中所有 complex_shapes 的技术正确性。

用法:  python backend/validate_templates.py
       python backend/validate_templates.py --fix    (自动修复可修问题)
       python backend/validate_templates.py --json   (输出 JSON 格式报告)
"""

import json, sys, math, re
from pathlib import Path

ALIASES_PATH = Path(__file__).parent / "aliases.json"

# ── 允许的 action 集合 ──
ALLOWED_ACTIONS = {
    "drawCircle", "drawRect", "drawEllipse", "drawLine",
    "drawPolygon", "drawArc", "drawStar", "drawTriangle",
}

# ── 每种 action 必需的参数 ──
REQUIRED_PARAMS = {
    "drawCircle":   ["x", "y", "radius", "color"],
    "drawRect":     ["x", "y", "width", "height", "color"],
    "drawEllipse":  ["x", "y", "radiusX", "radiusY", "color"],
    "drawLine":     ["x1", "y1", "x2", "y2", "color"],
    "drawPolygon":  ["points", "color"],
    "drawArc":      ["x", "y", "radius", "startAngle", "endAngle", "color"],
    "drawStar":     ["x", "y", "radius", "color"],
    "drawTriangle": ["points", "color"],
}

# ── 推荐别名模式（检查是否缺儿童叠词） ──
RECOMMENDED_PATTERNS = [
    (r"(.)\1$", "叠词"),           # 猫猫、狗狗、兔兔
    (r"小.", "小字开头"),            # 小猫、小狗
    (r"(.)\1(.)\2$", "AABB叠词"),  # 高高低低
    (r"的$", "的字结尾"),            # 红色的、圆形的
]

CANVAS_W = 800
CANVAS_H = 600


# ════════════════════════════════════════════════════════════
#  Loading
# ════════════════════════════════════════════════════════════

def load_aliases():
    if not ALIASES_PATH.exists():
        print(f"[FATAL] {ALIASES_PATH} not found")
        sys.exit(1)
    with open(ALIASES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    shapes = data.get("complex_shapes", {})
    if not shapes:
        print(f"[WARN] no complex_shapes found in {ALIASES_PATH}")
    return shapes


# ════════════════════════════════════════════════════════════
#  Check 1.1 — JSON 结构完整性
# ════════════════════════════════════════════════════════════

def check_structure(name, template):
    errors = []
    warnings = []

    # 必须字段
    if not isinstance(template.get("aliases"), list) or len(template["aliases"]) == 0:
        errors.append("缺少或有空的 aliases 数组")

    if not isinstance(template.get("actions"), list) or len(template["actions"]) == 0:
        errors.append("缺少或有空的 actions 数组")
        return errors, warnings  # 无法继续检查

    for i, action in enumerate(template["actions"]):
        prefix = f"actions[{i}]"

        # action 字段
        act = action.get("action")
        if not act:
            errors.append(f"{prefix} 缺少 action 字段")
            continue
        if act not in ALLOWED_ACTIONS:
            errors.append(f"{prefix} action=\"{act}\" 不在允许集合中: {ALLOWED_ACTIONS}")
            continue

        # 必需参数
        required = REQUIRED_PARAMS.get(act, [])
        for param in required:
            val = action.get(param)
            if val is None:
                errors.append(f"{prefix} {act} 缺少必需参数 \"{param}\"")

        # 坐标边界检查
        if act == "drawCircle":
            _check_bounds(errors, prefix, action, ["x", "y", "radius"], skip_color=True)
        elif act == "drawRect":
            _check_bounds(errors, prefix, action, ["x", "y", "width", "height"], skip_color=True)
        elif act == "drawEllipse":
            _check_bounds(errors, prefix, action, ["x", "y", "radiusX", "radiusY"], skip_color=True)
        elif act == "drawLine":
            _check_bounds(errors, prefix, action, ["x1", "y1", "x2", "y2"], skip_color=True)
        elif act == "drawArc":
            _check_bounds(errors, prefix, action, ["x", "y", "radius"], skip_color=True)
            _check_angle(warnings, prefix, action)
        elif act == "drawPolygon" or act == "drawTriangle":
            pts = action.get("points")
            if pts:
                _check_points_bounds(errors, prefix, pts)

    return errors, warnings


def _check_bounds(errors, prefix, action, fields, skip_color=False):
    for f in fields:
        val = action.get(f)
        if val is None:
            continue
        if not isinstance(val, (int, float)):
            errors.append(f"{prefix} 参数 {f} 应为数值, 当前={val}")
            continue
        if f in ("x", "x1", "x2", "width", "radius", "radiusX"):
            if val < 0 or val > CANVAS_W:
                errors.append(f"{prefix} {f}={val} 超出画布宽度 (0-{CANVAS_W})")
        if f in ("y", "y1", "y2", "height", "radius", "radiusY"):
            if val < 0 or val > CANVAS_H:
                errors.append(f"{prefix} {f}={val} 超出画布高度 (0-{CANVAS_H})")


def _check_angle(warnings, prefix, action):
    sa = action.get("startAngle")
    ea = action.get("endAngle")
    if sa is not None and ea is not None:
        if abs(sa) > 2 * math.pi + 0.1:
            warnings.append(f"{prefix} startAngle={sa} 异常大")
        if abs(ea) > 2 * math.pi + 0.1:
            warnings.append(f"{prefix} endAngle={ea} 异常大")


def _check_points_bounds(errors, prefix, points):
    for j, pt in enumerate(points):
        x = pt.get("x") if isinstance(pt, dict) else (pt[0] if isinstance(pt, (list, tuple)) else None)
        y = pt.get("y") if isinstance(pt, dict) else (pt[1] if isinstance(pt, (list, tuple)) else None)
        if x is not None and (x < 0 or x > CANVAS_W):
            errors.append(f"{prefix} points[{j}].x={x} 超出画布宽度")
        if y is not None and (y < 0 or y > CANVAS_H):
            errors.append(f"{prefix} points[{j}].y={y} 超出画布高度")


# ════════════════════════════════════════════════════════════
#  Check 1.2 — 语义合理性
# ════════════════════════════════════════════════════════════

def check_semantics(name, template):
    warnings = []
    actions = template.get("actions", [])

    # 查找对称部件（近似坐标的成对元素）
    circles = [(i, a) for i, a in enumerate(actions) if a.get("action") == "drawCircle"]
    for i in range(len(circles)):
        for j in range(i + 1, len(circles)):
            _, a = circles[i]
            _, b = circles[j]
            # 两颗半径相似、y 坐标接近、x 坐标分别在中线两侧 → 可能是一对眼睛
            if (a.get("color") == b.get("color") and
                abs(a.get("radius", 0) - b.get("radius", 0)) <= 3 and
                abs(a.get("y", 0) - b.get("y", 0)) <= 15):
                cx, cy = a.get("x", 0), b.get("x", 0)
                mid = (cx + cy) / 2
                if abs(mid - CANVAS_W / 2) > 50:
                    warnings.append(f"疑似对称部件（圆 {circles[i][0]} 和 {circles[j][0]}）的中心不在画布中线上")

    # 检查耳朵是否在头上方（drawRect 屋顶？）
    rects = [(i, a) for i, a in enumerate(actions) if a.get("action") == "drawRect"]
    if rects:
        # 如果有一个大矩形（身体/墙壁）和另一个矩形（门）
        sorted_rects = sorted(rects, key=lambda x: x[1].get("height", 0), reverse=True)
        # 略过，因为"耳朵在上方"这种检查需要语义理解，比较难通用

    return warnings


# ════════════════════════════════════════════════════════════
#  Check 1.3 — 性能检查
# ════════════════════════════════════════════════════════════

def check_performance(name, template):
    warnings = []
    actions = template.get("actions", [])
    n = len(actions)

    if n > 30:
        warnings.append(f"actions 数量={n}，超过建议上限 30")
    elif n > 20:
        warnings.append(f"actions 数量={n}，接近上限 30")

    # 检查是否有大量线段/多边形
    line_count = sum(1 for a in actions if a.get("action") == "drawLine")
    poly_count = sum(1 for a in actions if a.get("action") == "drawPolygon")
    if line_count > 10:
        warnings.append(f"drawLine 太多 ({line_count}条)，建议合并")
    if poly_count > 5:
        warnings.append(f"drawPolygon 太多 ({poly_count}个)，可能卡顿")

    # 检查冗余动作
    for i in range(1, n):
        if actions[i].get("action") == actions[i - 1].get("action"):
            a, b = actions[i], actions[i - 1]
            # 相同的 setColor/setSize 连续出现
            if a.get("action") in ("setColor", "setSize") and a.get("color") == b.get("color"):
                warnings.append(f"actions[{i}] 与 [{i-1}] 重复的 {a['action']}")

    return warnings


# ════════════════════════════════════════════════════════════
#  Check 1.4 — 别名覆盖检查
# ════════════════════════════════════════════════════════════

def check_aliases(name, template):
    warnings = []
    aliases = template.get("aliases", [])

    # 检查叠词
    has_dieci = any(len(a) == 2 and a[0] == a[1] for a in aliases if len(a) >= 2)
    if not has_dieci:
        # 允许 name 本身是叠词
        if not (len(name) == 2 and name[0] == name[1]):
            warnings.append(f"缺乏叠词别名（如 \"{name[0]}{name[0]}\"）")

    # 检查是否有拼音/发音变体（允许英文/拼音）
    has_pinyin = any(not all('一' <= c <= '鿿' or c in ' abcdefghijklmnopqrstuvwxyz' for c in a) for a in aliases)
    # 放宽 - 只提醒完全没有非中文别名的情况
    all_cn = all(all('一' <= c <= '鿿' for c in a) for a in aliases if a)
    if all_cn and len(aliases) < 3:
        warnings.append(f"别名全部为中文且数量较少（{len(aliases)}个），建议添加发音变体")

    return warnings


# ════════════════════════════════════════════════════════════
#  别名冲突检测（跨模板）
# ════════════════════════════════════════════════════════════

def check_alias_conflicts(shapes):
    errors = []
    alias_map = {}  # alias -> [(name, count)]
    for name, template in shapes.items():
        for alias in template.get("aliases", []):
            if alias not in alias_map:
                alias_map[alias] = []
            alias_map[alias].append(name)

    conflicts = {k: v for k, v in alias_map.items() if len(v) > 1}
    # 过滤：真正的冲突是同一个 alias 映射到不同模板
    for alias, names in sorted(conflicts.items()):
        # 如果都是同一个 name 的不同写法（大小写等），不算冲突
        unique = set(names)
        if len(unique) > 1:
            errors.append(f"别名 \"{alias}\" 冲突: {list(unique)}")

    return errors


# ════════════════════════════════════════════════════════════
#  Main
# ════════════════════════════════════════════════════════════

def main():
    fix_mode = "--fix" in sys.argv
    json_mode = "--json" in sys.argv

    shapes = load_aliases()
    total = len(shapes)

    report = {
        "total": total,
        "passed": 0,
        "with_errors": 0,
        "with_warnings": 0,
        "details": [],
    }

    if json_mode:
        skip_color = lambda: None
    else:
        skip_color = lambda: None

    print(f"\n{'='*60}")
    print(f"  模板验证报告 — 共 {total} 个模板")
    print(f"{'='*60}")

    all_conflicts = check_alias_conflicts(shapes)

    for name in sorted(shapes.keys()):
        template = shapes[name]
        errors = []
        warnings = []

        e1, w1 = check_structure(name, template)
        w2 = check_semantics(name, template)
        w3 = check_performance(name, template)
        w4 = check_aliases(name, template)

        errors.extend(e1)
        warnings.extend(w1)
        warnings.extend(w2)
        warnings.extend(w3)
        warnings.extend(w4)

        if json_mode:
            detail = {"name": name, "errors": errors, "warnings": warnings}
        else:
            status = "PASS" if not errors else "FAIL"
            extra = " ⚠" if warnings else ""
            color = "\033[32m" if status == "PASS" else "\033[31m"
            reset = "\033[0m" if status == "FAIL" else ""
            # Simple print without colors for Windows compat
            if not errors and not warnings:
                print(f"  [OK]   {name}")
            elif not errors and warnings:
                print(f"  [OK⚠]  {name} — {'; '.join(warnings[:2])}{'...' if len(warnings) > 2 else ''}")
            else:
                print(f"  [FAIL] {name}")
                for e in errors:
                    print(f"         ├ {e}")
                for w in warnings:
                    print(f"         └ (warn) {w}")

        if not errors and not warnings:
            report["passed"] += 1
        if errors:
            report["with_errors"] += 1
        if warnings and not errors:
            report["with_warnings"] += 1

        report["details"].append({
            "name": name,
            "errors": errors,
            "warnings": warnings,
        })

    # 别名冲突
    if all_conflicts:
        print(f"\n  [CONFLICT] 别名冲突:")
        for c in all_conflicts:
            print(f"             {c}")

    report["alias_conflicts"] = all_conflicts

    # 统计
    print(f"\n{'='*60}")
    print(f"  摘要:")
    print(f"    通过:       {report['passed']}/{total}")
    print(f"    有警告:     {report['with_warnings']}")
    print(f"    有错误:     {report['with_errors']}")
    print(f"    别名冲突:   {len(all_conflicts)}")
    print(f"{'='*60}")

    if json_mode:
        print(json.dumps(report, ensure_ascii=False, indent=2))

    return len(all_conflicts) + report["with_errors"]


if __name__ == "__main__":
    sys.exit(main())
