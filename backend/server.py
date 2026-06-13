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
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
LOCAL_MODEL_NAME = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")

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

SYSTEM_PROMPT = """你是AI绘图指令解析器。将用户描述转化为JSON格式的绘图指令。

如果已知画布上已有哪些图形，只输出新图形的指令，不要重复画已有的图形。

画布尺寸: 宽800, 高600
坐标参考: 左上角(50,50) 右上角(750,50) 左下角(50,550) 右下角(750,550) 中心(400,300)
方向参考（口语"边/面"都行）: 左边/左面(100,300) 右边/右面(700,300) 上边/上面(400,100) 下边/下面(400,500)

支持的颜色: red红 blue蓝 green绿 yellow黄 black黑 white白 orange橙 purple紫 pink粉

简单指令用单意图格式：
SET_COLOR: {"intent":"SET_COLOR","color":"red"}
SET_SIZE: {"intent":"SET_SIZE","size":80}
CLEAR: {"intent":"CLEAR"}  UNDO: {"intent":"UNDO"}  SAVE: {"intent":"SAVE"}
MOVE: {"intent":"MOVE","direction":"左/右/上/下/左上/左下/右上/右下"}
LINE: {"intent":"LINE","direction":"左/右/上/下"} or {"intent":"LINE","from_pos":{"x":N,"y":N},"to_pos":{"x":N,"y":N}}
DRAW_SHAPE: {"intent":"DRAW_SHAPE","shape":"circle/rect","color":"颜色","position":{"x":N,"y":N}}
方向词自动映射坐标: 右边≈(700,300) 左边≈(100,300) 上边≈(400,100) 下边≈(400,500)

复杂图形必须拆解为actions数组。支持的原子操作:
drawCircle: {"action":"drawCircle","x":N,"y":N,"radius":N,"color":"颜色"}
drawRect: {"action":"drawRect","x":N,"y":N,"width":N,"height":N,"color":"颜色"}
drawLine: {"action":"drawLine","x1":N,"y1":N,"x2":N,"y2":N,"color":"颜色"}
drawPolygon: {"action":"drawPolygon","points":[{"x":N,"y":N},...],"color":"颜色"}
drawArc: {"action":"drawArc","x":N,"y":N,"radius":N,"startAngle":N,"endAngle":N,"color":"颜色"}
setColor: {"action":"setColor","color":"颜色"}
setSize: {"action":"setSize","size":N}

示例—必须严格遵循JSON格式，不要有任何额外文字：

红色 → {"intent":"SET_COLOR","color":"red"}
半径80 → {"intent":"SET_SIZE","size":80}
在中心画一个红色的圆 → {"intent":"DRAW_SHAPE","shape":"circle","color":"red","position":{"x":400,"y":300}}
在下面画一个绿色的圆 → {"intent":"DRAW_SHAPE","shape":"circle","color":"green","position":{"x":400,"y":500}}

画一个房子 → {"actions":[
{"action":"drawRect","x":300,"y":250,"width":200,"height":150,"color":"orange"},
{"action":"drawPolygon","points":[{"x":280,"y":250},{"x":400,"y":150},{"x":520,"y":250}],"color":"red"},
{"action":"drawRect","x":360,"y":340,"width":80,"height":60,"color":"brown"},
{"action":"drawCircle","x":400,"y":360,"radius":10,"color":"yellow"}]}

在右边画一个蓝色的圆 → {"intent":"DRAW_SHAPE","shape":"circle","color":"blue","position":{"x":700,"y":300}}
在左边画一个矩形 → {"intent":"DRAW_SHAPE","shape":"rect","position":{"x":100,"y":300}}

画一棵树 → {"actions":[
{"action":"drawRect","x":385,"y":400,"width":30,"height":100,"color":"brown"},
{"action":"drawCircle","x":400,"y":370,"radius":50,"color":"green"},
{"action":"drawCircle","x":370,"y":390,"radius":40,"color":"darkgreen"},
{"action":"drawCircle","x":430,"y":390,"radius":40,"color":"darkgreen"}]}

画一朵花 → {"actions":[
{"action":"drawCircle","x":400,"y":330,"radius":12,"color":"yellow"},
{"action":"drawCircle","x":400,"y":290,"radius":18,"color":"pink"},
{"action":"drawCircle","x":430,"y":310,"radius":18,"color":"pink"},
{"action":"drawCircle","x":420,"y":345,"radius":18,"color":"pink"},
{"action":"drawCircle","x":380,"y":345,"radius":18,"color":"pink"},
{"action":"drawCircle","x":370,"y":310,"radius":18,"color":"pink"},
{"action":"drawLine","x1":400,"y1":350,"x2":400,"y2":420,"color":"green"}]}

画一个笑脸 → {"actions":[
{"action":"drawCircle","x":400,"y":300,"radius":80,"color":"yellow"},
{"action":"drawCircle","x":370,"y":280,"radius":10,"color":"black"},
{"action":"drawCircle","x":430,"y":280,"radius":10,"color":"black"},
{"action":"drawArc","x":400,"y":320,"radius":35,"startAngle":0.15,"endAngle":2.99,"color":"black"}]}

画一个太阳在左上角 → {"actions":[
{"action":"drawCircle","x":80,"y":80,"radius":35,"color":"yellow"},
{"action":"drawLine","x1":80,"y1":20,"x2":80,"y2":140,"color":"orange"},
{"action":"drawLine","x1":20,"y1":80,"x2":140,"y2":80,"color":"orange"},
{"action":"drawLine","x1":35,"y1":35,"x2":125,"y2":125,"color":"orange"},
{"action":"drawLine","x1":125,"y1":35,"x2":35,"y2":125,"color":"orange"}]}

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

    resp = requests.post(f"{OLLAMA_URL}/api/chat", json=payload, timeout=60)
    resp.raise_for_status()
    raw = resp.json()["message"]["content"]
    parsed = extract_json(raw)
    return to_response(parsed, text, backend=f"ollama:{OLLAMA_MODEL}")


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

def parse_text(text: str, context: str = "") -> ParseResponse:
    """Route to the appropriate backend."""

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
    """Parse a natural language voice command."""
    t0 = time.time()
    result = parse_text(req.text, context=req.context or "")
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
