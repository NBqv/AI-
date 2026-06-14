# Voice Draw — Ollama + Local AI Backend
# Start: uvicorn server:app --host 0.0.0.0 --port 8080
#
# Backend modes (BACKEND env var):
#   ollama — Ollama API (default, requires ollama serve)
#   local  — local transformers model (Qwen2.5-1.5B)
#   auto   — Ollama preferred, falls back to local

import json
import os
import re
import ssl
import time
from pathlib import Path
from typing import Optional

# SSL fix for Windows: disable cert verification
ssl._create_default_https_context = ssl._create_unverified_context

import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ── Config ─────────────────────────────────────────────────
BACKEND = os.environ.get("BACKEND", "ollama").lower()  # ollama | local | auto
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
LOCAL_MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")

# ── Response cache (same text+context = reuse) ────────────
response_cache = {}
MAX_CACHE = 50

# ── Load aliases dictionary ───────────────────────────────
ALIASES_PATH = Path(__file__).parent / "aliases.json"
aliases = {}
if ALIASES_PATH.exists():
    with open(ALIASES_PATH, "r", encoding="utf-8") as f:
        aliases = json.load(f)
    print(f"[Aliases] Loaded {sum(len(v) if isinstance(v, list) else len(v) for v in aliases.values())} entries from {ALIASES_PATH.name}")
else:
    print(f"[Aliases] {ALIASES_PATH.name} not found, running without alias lookup")

# ── Build alias context for AI inference ───────────────

def build_alias_context_dict() -> str:
    """Build a compact alias table from aliases.json for AI context injection."""
    if not aliases:
        return ""

    sections = []

    if "position_absolute" in aliases:
        parts = [f"{e['names'][0]}({e['x']},{e['y']})" for e in aliases["position_absolute"]]
        sections.append("位置: " + " ".join(parts))

    if "color" in aliases:
        parts = [f"{v[0]}={k}" for k, v in aliases["color"].items()]
        sections.append("颜色: " + " ".join(parts))

    if "shape" in aliases:
        parts = [f"{v[0]}={k}" for k, v in aliases["shape"].items()]
        sections.append("形状: " + " ".join(parts))

    if "complex_shapes" in aliases:
        names = list(aliases["complex_shapes"].keys())
        sections.append("预定义复杂图形: " + " ".join(names))

    if "size_relative" in aliases:
        parts = [e["names"][0] for e in aliases["size_relative"]]
        sections.append("大小等级: " + " ".join(parts))

    return "\n".join(sections)

ALIAS_CONTEXT = build_alias_context_dict()

# ── FastAPI ───────────────────────────────────────────────
app = FastAPI(title="Voice Draw NLP Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Request / Response schemas ────────────────────────────

class Command(BaseModel):
    action: str
    x: Optional[int] = None
    y: Optional[int] = None
    x1: Optional[int] = None
    y1: Optional[int] = None
    x2: Optional[int] = None
    y2: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    radius: Optional[int] = None
    radiusX: Optional[int] = None
    radiusY: Optional[int] = None
    rx: Optional[int] = None
    ry: Optional[int] = None
    points: Optional[list] = None
    color: Optional[str] = None
    size: Optional[int] = None
    startAngle: Optional[float] = None
    endAngle: Optional[float] = None

class ParseRequest(BaseModel):
    text: str
    context: Optional[str] = None

class Position(BaseModel):
    x: int
    y: int

class ParseResponse(BaseModel):
    intent: str = ""
    shape: Optional[str] = None
    color: Optional[str] = None
    position: Optional[Position] = None
    from_pos: Optional[Position] = None
    to_pos: Optional[Position] = None
    size: Optional[int] = None
    direction: Optional[str] = None
    commands: Optional[list[Command]] = None
    actions: Optional[list[Command]] = None
    raw_text: str = ""
    reasoning: str = ""
    backend: str = ""

# ── System prompt ─────────────────────────────────────────

SYSTEM_PROMPT = """你是AI图形设计师。将用户描述转化为actions数组。

允许的action（只能用这些，不要自创）:
drawCircle — 圆: x, y, radius, color
drawEllipse — 椭圆: x, y, radiusX, radiusY, color
drawRect — 矩形: x, y, width, height, color
drawLine — 线段: x1, y1, x2, y2, color
drawPolygon — 多边形: points=[{"x":N,"y":N},...], color  (用于三角形/屋顶/鱼鳍/翅膀等)
drawArc — 弧线: x, y, radius, startAngle, endAngle, color  (用于笑脸嘴巴)
clear — 清空画布（换一个时用）
setColor/setSize — 设置属性

画布: 800x600. 坐标: 左上(50,50) 右上(750,50) 左下(50,550) 右下(750,550) 中心(400,300) 左(100,300) 右(700,300) 上(400,100) 下(400,500)
颜色: red红 blue蓝 green绿 yellow黄 black黑 white白 orange橙 purple紫 pink粉 brown棕 gold金

拆解方法：想象图形由哪些基本几何体组成，分别画出来。例如:
- 鱼 = 椭圆身体 + 三角尾巴 + 圆眼睛
- 蝴蝶 = 椭圆身体 + 两个多边形翅膀
- 火箭 = 矩形机身 + 三角形头 + 三角翼 + 圆窗

考虑用户说"换一个/换一种方式"时对画布上已有的图形不满意，需要先输出clear清空再画新的。
考虑用户说"修改/调整/改一下/把...改成..."时是在现有图形上修改，不要clear。

先构思再输出。坐标和尺寸必须合理，确保图形看起来协调好看。

你的输出必须严格遵循JSON格式，不要有任何额外文字。

示例：

画一个房子 → 墙壁+屋顶+门+把手:
{"actions":[
{"action":"drawRect","x":300,"y":250,"width":200,"height":150,"color":"orange"},
{"action":"drawPolygon","points":[{"x":280,"y":250},{"x":400,"y":150},{"x":520,"y":250}],"color":"red"},
{"action":"drawRect","x":360,"y":340,"width":80,"height":60,"color":"brown"},
{"action":"drawCircle","x":400,"y":360,"radius":10,"color":"yellow"}]}

画一条鱼 → 椭圆身体+三角尾巴+圆眼睛:
{"actions":[
{"action":"drawEllipse","x":350,"y":300,"radiusX":70,"radiusY":35,"color":"blue"},
{"action":"drawPolygon","points":[{"x":420,"y":300},{"x":470,"y":270},{"x":470,"y":330}],"color":"blue"},
{"action":"drawCircle","x":310,"y":290,"radius":6,"color":"black"}]}

画一只猫 → 脸+耳朵+眼睛:
{"actions":[
{"action":"drawCircle","x":400,"y":300,"radius":60,"color":"orange"},
{"action":"drawPolygon","points":[{"x":350,"y":260},{"x":365,"y":200},{"x":385,"y":255}],"color":"orange"},
{"action":"drawPolygon","points":[{"x":450,"y":260},{"x":435,"y":200},{"x":415,"y":255}],"color":"orange"},
{"action":"drawCircle","x":380,"y":290,"radius":8,"color":"black"},
{"action":"drawCircle","x":420,"y":290,"radius":8,"color":"black"}]}

你的输出必须严格遵循JSON格式，不要有任何额外文字。"""


# ── JSON extraction (shared by both backends) ─────────────

def extract_json(raw: str) -> dict:
    """Try to parse JSON from model output — handle common wrap issues."""
    text = raw.strip()
    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]
    # Remove markdown code blocks
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


# ── Response mapper ───────────────────────────────────────

def to_response(data: dict, raw_text: str, backend: str = "") -> ParseResponse:
    def to_pos(p):
        if isinstance(p, dict) and "x" in p and "y" in p:
            return Position(x=int(p["x"]), y=int(p["y"]))
        return None

    def to_cmd_list(key):
        raw = data.get(key)
        if isinstance(raw, list):
            return [Command(**c) if isinstance(c, dict) else c for c in raw]
        return None

    return ParseResponse(
        intent=data.get("intent", ""),
        shape=data.get("shape"),
        color=data.get("color"),
        position=to_pos(data.get("position")),
        from_pos=to_pos(data.get("from_pos")),
        to_pos=to_pos(data.get("to_pos")),
        size=data.get("size"),
        direction=data.get("direction"),
        commands=to_cmd_list("commands"),
        actions=to_cmd_list("actions"),
        raw_text=raw_text,
        reasoning=data.get("reasoning", ""),
        backend=backend,
    )


# ═══════════════════════════════════════════════════════════
#  Backend: Ollama
# ═══════════════════════════════════════════════════════════

def check_ollama() -> bool:
    """Check if Ollama service is reachable."""
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def inference_ollama(text: str, context: str = "") -> ParseResponse:
    """Parse via Ollama API."""
    # Inject alias context into system prompt
    system_content = SYSTEM_PROMPT
    if ALIAS_CONTEXT:
        system_content = ALIAS_CONTEXT + "\n\n" + system_content
    messages = [{"role": "system", "content": system_content}]
    if context.strip():
        messages[0]["content"] = context.strip() + "\n\n" + messages[0]["content"]
    messages.append({"role": "user", "content": text})

    payload = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0,
            "num_predict": 512,
        }
    }

    try:
        resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=180)
        resp.raise_for_status()
        raw = resp.json()["message"]["content"]
        parsed = extract_json(raw)
        return to_response(parsed, text, backend=f"ollama:{OLLAMA_MODEL}")
    except requests.RequestException as e:
        print(f"[Ollama] Error: {e}")
        return to_response({"intent": "UNKNOWN"}, text, backend=f"ollama:{OLLAMA_MODEL}:error")


# ═══════════════════════════════════════════════════════════
#  Backend: Local (transformers)
# ═══════════════════════════════════════════════════════════

local_model = None
local_tokenizer = None

def load_local_model():
    """Load local transformers model into memory."""
    global local_model, local_tokenizer

    if local_model is not None:
        return {"status": "already_loaded"}

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[Local] Loading {LOCAL_MODEL_NAME} on cpu...")
    t0 = time.time()

    local_tokenizer = AutoTokenizer.from_pretrained(LOCAL_MODEL_NAME)
    local_model = AutoModelForCausalLM.from_pretrained(
        LOCAL_MODEL_NAME,
        torch_dtype=torch.float32,
        low_cpu_mem_usage=True,
    )
    local_model.to("cpu")
    local_model.eval()

    elapsed = time.time() - t0
    print(f"[Local] Done in {elapsed:.1f}s")
    return {"status": "loaded", "model": LOCAL_MODEL_NAME, "device": "cpu", "elapsed_s": round(elapsed, 1)}


def build_local_prompt(user_text: str, context: str = "") -> str:
    """Build chat prompt for local model using its chat template."""
    system_content = SYSTEM_PROMPT
    if ALIAS_CONTEXT:
        system_content = ALIAS_CONTEXT + "\n\n" + system_content
    messages = [{"role": "system", "content": system_content}]
    if context.strip():
        messages[0]["content"] = context.strip() + "\n\n" + messages[0]["content"]
    messages.append({"role": "user", "content": user_text})
    text = local_tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return text


def inference_local(text: str, context: str = "") -> ParseResponse:
    """Parse via local transformers model."""
    import torch

    if local_model is None:
        raise RuntimeError("Local model not loaded. Call GET /load first.")

    prompt = build_local_prompt(text, context)
    inputs = local_tokenizer(prompt, return_tensors="pt").to("cpu")

    with torch.no_grad():
        outputs = local_model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,
            pad_token_id=local_tokenizer.eos_token_id,
        )

    input_len = inputs["input_ids"].shape[1]
    response = local_tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True).strip()
    parsed = extract_json(response)
    return to_response(parsed, text, backend="local")


# ═══════════════════════════════════════════════════════════
#  Router
# ═══════════════════════════════════════════════════════════

# Build alias→name lookup for template matching
template_aliases = {}
for name, data in aliases.get("complex_shapes", {}).items():
    for alias in data.get("aliases", []):
        template_aliases[alias] = (name, data["actions"])


def match_template(text: str) -> Optional[ParseResponse]:
    """Check if user text matches a complex shape template. Returns template if found."""
    best_name = None
    best_actions = None
    best_len = 0
    for alias, (name, actions) in template_aliases.items():
        if alias in text and len(alias) > best_len:
            best_name = name
            best_actions = actions
            best_len = len(alias)
    if best_actions:
        print(f"[Template] matched \"{text}\" -> {best_name}")
        return ParseResponse(
            intent="", actions=[Command(**a) if isinstance(a, dict) else a for a in best_actions],
            raw_text=text, backend=f"template:{best_name}")
    return None


def parse_text(text: str, context: str = "") -> ParseResponse:
    """Route to the appropriate backend. Templates take priority."""

    # ── Template match (always first, regardless of context) ──
    template = match_template(text)
    if template:
        return template

    if BACKEND == "ollama":
        if not check_ollama():
            return ParseResponse(
                intent="UNKNOWN", raw_text=text,
                reasoning="Ollama service not reachable",
                backend="ollama:offline",
            )
        return inference_ollama(text, context)

    if BACKEND == "local":
        if local_model is None:
            return ParseResponse(
                intent="UNKNOWN", raw_text=text,
                reasoning="Local model not loaded. Call GET /load first.",
                backend="local:unloaded",
            )
        return inference_local(text, context)

    if BACKEND == "auto":
        # Try Ollama first, fall back to local
        if check_ollama():
            try:
                return inference_ollama(text, context)
            except Exception as e:
                print(f"[Auto] Ollama failed ({e}), falling back to local")

        if local_model is not None:
            return inference_local(text, context)

        return ParseResponse(
            intent="UNKNOWN", raw_text=text,
            reasoning="No backend available (Ollama offline, local not loaded)",
            backend="none",
        )

    return ParseResponse(
        intent="UNKNOWN", raw_text=text,
        reasoning=f"Unknown backend: {BACKEND}",
        backend="unknown",
    )


# ── API Routes ────────────────────────────────────────────

@app.post("/parse", response_model=ParseResponse)
async def parse(req: ParseRequest):
    """Parse a natural language voice command.
    Uses 7B by default for best quality. Results are cached:
    same text + same context → instant replay.
    Say '换一个' to get a fresh generation."""
    t0 = time.time()

    # ── Cache lookup: same text + same context ──
    cache_key = f"{req.text}||{req.context or ''}"
    cached = response_cache.get(cache_key)
    if cached and not req.context:
        print(f"[Cache] hit for \"{req.text[:20]}...\"")
        elapsed = time.time() - t0
        cached.reasoning = f"(cached: {elapsed:.2f}s)"
        return cached

    # ── Run inference ──
    result = parse_text(req.text, context=req.context or "")

    # ── Cache result (only if no context, i.e. fresh draws) ──
    if not req.context and (result.intent or (result.actions and len(result.actions) > 0)):
        response_cache[cache_key] = result
        if len(response_cache) > MAX_CACHE:
            oldest = next(iter(response_cache))
            del response_cache[oldest]
        print(f"[Cache] stored for \"{req.text[:20]}...\"")

    elapsed = time.time() - t0
    result.reasoning = (result.reasoning or "") + f" ({elapsed:.2f}s)"
    return result


@app.get("/aliases")
async def get_aliases():
    """Return the full aliases dictionary for frontend use."""
    if aliases:
        return aliases
    return {"error": "aliases.json not loaded"}


@app.get("/load")
async def load_model():
    """Load the local transformers model (needed for 'local' and 'auto' modes)."""
    return load_local_model()


@app.get("/clearcache")
async def clear_cache():
    """Clear the response cache. Call this when you want fresh generations."""
    response_cache.clear()
    return {"status": "cache_cleared", "entries": 0}


@app.get("/")
async def root():
    return {
        "service": "Voice Draw NLP Backend",
        "backend": BACKEND,
        "ollama_model": OLLAMA_MODEL,
        "local_model": LOCAL_MODEL_NAME.split("/")[-1],
        "ollama_online": check_ollama(),
        "local_loaded": local_model is not None,
        "status": "ok",
    }
