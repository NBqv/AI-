"""修复 aliases.json 中所有非标准 drawTriangle 格式"""
import json, math
from pathlib import Path

path = Path(__file__).parent / "aliases.json"
with open(path, "r", encoding="utf-8") as f:
    data = json.load(f)

shapes = data.get("complex_shapes", {})
fixed = 0

for name, tpl in shapes.items():
    new_actions = []
    for action in tpl.get("actions", []):
        act = action.get("action", "")

        if act == "drawTriangle":
            # Already has points? Just rename to drawPolygon
            if action.get("points"):
                action["action"] = "drawPolygon"
                for k in ["x","y","x1","y1","x2","y2","width","height","base","angle","radius"]:
                    action.pop(k, None)
                new_actions.append(action)
                fixed += 1
                print(f"  [{name}] points -> drawPolygon")
                continue

            # Has x,y,width,height? Calculate points for a triangle
            x = action.pop("x", 400)
            y = action.pop("y", 300)
            w = action.pop("width", None)
            h = action.pop("height", None)
            base = action.pop("base", None)
            h2 = action.pop("height", h)  # may have been popped already
            angle = action.pop("angle", 0)

            if w and h and w > 0 and h > 0:
                # Triangle: bottom-left(x-w/2,y+h/2), bottom-right(x+w/2,y+h/2), top-center(x,y-h/2)
                pts = [
                    {"x": int(x - w/2), "y": int(y + h/2)},
                    {"x": int(x + w/2), "y": int(y + h/2)},
                    {"x": int(x), "y": int(y - h/2)},
                ]
                if angle == 90:
                    pts = [
                        {"x": int(x - w/2), "y": int(y - h/2)},
                        {"x": int(x + w/2), "y": int(y)},
                        {"x": int(x - w/2), "y": int(y + h/2)},
                    ]
            elif base and h and base > 0 and h > 0:
                pts = [
                    {"x": int(x - base/2), "y": int(y + h/2)},
                    {"x": int(x + base/2), "y": int(y + h/2)},
                    {"x": int(x), "y": int(y - h/2)},
                ]
                if angle == 90:
                    pts = [
                        {"x": int(x - base/2), "y": int(y - h/2)},
                        {"x": int(x + base/2), "y": int(y)},
                        {"x": int(x - base/2), "y": int(y + h/2)},
                    ]
            else:
                # Fallback: small default triangle
                pts = [{"x": x-15, "y": y+10}, {"x": x+15, "y": y+10}, {"x": x, "y": y-15}]

            action["action"] = "drawPolygon"
            action["points"] = pts
            for k in ["x1","y1","x2","y2","x3","y3","width","height","base","angle","radius"]:
                action.pop(k, None)
            fixed += 1
            print(f"  [{name}] converted to drawPolygon ({len(pts)} pts)")
            new_actions.append(action)
            continue

        new_actions.append(action)

    tpl["actions"] = new_actions

with open(path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n共修复 {fixed} 个 drawTriangle → drawPolygon")
