# Voice Draw — Qwen2.5-0.5B AI Backend
# Start: uvicorn server:app --host 0.0.0.0 --port 8080

import json
import os
import re
import ssl
import time
from typing import Optional

# SSL fix for Windows: disable cert verification
ssl._create_default_https_context = ssl._create_unverified_context

# Use Chinese mirror for HuggingFace (faster downloads in CN)
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

import torch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer

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

# ── Model globals (lazy-loaded) ───────────────────────────
model = None
tokenizer = None
device = "cpu"

# ── System prompt ─────────────────────────────────────────

SYSTEM_PROMPT = """你是AI绘图指令解析器。将用户描述转化为JSON格式的绘图指令。

画布尺寸: 宽800, 高600
坐标参考: 左上角(50,50) 右上角(750,50) 左下角(50,550) 右下角(750,550) 中心(400,300)

支持的颜色: red红 blue蓝 green绿 yellow黄 black黑 white白 orange橙 purple紫 pink粉

简单指令用单意图格式：
SET_COLOR: {"intent":"SET_COLOR","color":"red"}
SET_SIZE: {"intent":"SET_SIZE","size":80}
CLEAR: {"intent":"CLEAR"}  UNDO: {"intent":"UNDO"}  SAVE: {"intent":"SAVE"}
MOVE: {"intent":"MOVE","direction":"左/右/上/下/左上/左下/右上/右下"}
LINE: {"intent":"LINE","direction":"左/右/上/下"} or {"intent":"LINE","from_pos":{"x":N,"y":N},"to_pos":{"x":N,"y":N}}
DRAW_SHAPE: {"intent":"DRAW_SHAPE","shape":"circle/rect","color":"颜色","position":{"x":N,"y":N}}

复杂图形必须拆解为actions数组。支持的原子操作:
drawCircle: {"action":"drawCircle","x":N,"y":N,"radius":N,"color":"颜色"}
drawRect: {"action":"drawRect","x":N,"y":N,"width":N,"height":N,"color":"颜色"}
drawLine: {"action":"drawLine","x1":N,"y1":N,"x2":N,"y2":N,"color":"颜色"}
drawPolygon: {"action":"drawPolygon","points":[{"x":N,"y":N},...],"color":"颜色"}
drawArc: {"action":"drawArc","x":N,"y":N,"radius":N,"startAngle":N,"endAngle":N,"color":"颜色"}
setColor: {"action":"setColor","color":"颜色"}  — 设置后续使用的颜色
setSize: {"action":"setSize","size":N}  — 设置圆半径

示例—必须严格遵循JSON格式，不要有任何额外文字：

红色 → {"intent":"SET_COLOR","color":"red"}
半径80 → {"intent":"SET_SIZE","size":80}
在中心画一个红色的圆 → {"intent":"DRAW_SHAPE","shape":"circle","color":"red","position":{"x":400,"y":300}}

画一个房子 → {"actions":[
{"action":"drawRect","x":300,"y":250,"width":200,"height":150,"color":"orange"},
{"action":"drawPolygon","points":[{"x":280,"y":250},{"x":400,"y":150},{"x":520,"y":250}],"color":"red"},
{"action":"drawRect","x":360,"y":340,"width":80,"height":60,"color":"brown"},
{"action":"drawCircle","x":400,"y":360,"radius":10,"color":"yellow"}]}

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


# ── Prompt builder ────────────────────────────────────────

def build_prompt(user_text: str) -> str:
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_text},
    ]
    # Apply Qwen2.5 chat template — requires tokenizer to be loaded
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    return text


# ── JSON extraction from model output ─────────────────────

def extract_json(raw: str) -> dict:
    """Try to parse JSON from model output — handle common wrap issues."""
    # Strip the assistant prefix if present
    text = raw.strip()
    if text.startswith("<|im_start|>assistant"):
        text = text.split("<|im_start|>assistant")[-1].strip()

    # Find first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start:end + 1]

    # Remove markdown code blocks if present
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


# ── Response mapper ───────────────────────────────────────

def to_response(data: dict, raw_text: str) -> ParseResponse:
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
    )


# ── Inference ─────────────────────────────────────────────

def inference(text: str) -> ParseResponse:
    global model, tokenizer

    if model is None:
        raise RuntimeError("Model not loaded. Call GET /load first.")

    prompt = build_prompt(text)
    inputs = tokenizer(prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            do_sample=False,  # greedy = deterministic, more reliable
            pad_token_id=tokenizer.eos_token_id,
        )

    # Decode only the newly generated tokens
    input_len = inputs["input_ids"].shape[1]
    response = tokenizer.decode(outputs[0][input_len:], skip_special_tokens=True).strip()

    parsed = extract_json(response)
    return to_response(parsed, text)


# ── API Routes ────────────────────────────────────────────

@app.on_event("startup")
async def startup():
    """Auto-load model on startup (optional — or use GET /load)."""
    pass  # Lazy-load on first parse request


@app.get("/load")
async def load_model():
    """Load the model into memory. Call once on startup."""
    global model, tokenizer, device

    if model is not None:
        return {"status": "already_loaded"}

    model_name = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct")
    use_8bit = os.environ.get("MODEL_8BIT", "0") == "1"  # off by default (affects output quality)
    print(f"[Load] Loading {model_name} on {device} (8bit={use_8bit})...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float32,  # CPU needs float32
        low_cpu_mem_usage=True,
    )

    # Dynamic quantization: reduces memory ~4x on CPU with minimal quality loss
    if use_8bit and device == "cpu":
        model = torch.ao.quantization.quantize_dynamic(
            model, {torch.nn.Linear}, dtype=torch.qint8
        )
        print(f"[Load] Dynamic quantization applied (qint8)")

    model.to(device)
    model.eval()

    elapsed = time.time() - t0
    print(f"[Load] Done in {elapsed:.1f}s")
    return {"status": "loaded", "model": model_name, "device": device, "elapsed_s": round(elapsed, 1)}


@app.post("/parse", response_model=ParseResponse)
async def parse(req: ParseRequest):
    """Parse a natural language voice command."""
    if model is None:
        return ParseResponse(
            intent="UNKNOWN",
            raw_text=req.text,
            reasoning="Model not loaded. Call GET /load first.",
        )

    t0 = time.time()
    result = inference(req.text)
    elapsed = time.time() - t0
    result.reasoning = (result.reasoning or "") + f" (inference: {elapsed:.2f}s)"
    return result


@app.get("/")
async def root():
    m = os.environ.get("MODEL_NAME", "Qwen/Qwen2.5-1.5B-Instruct").split("/")[-1]
    return {"service": "Voice Draw NLP Backend", "model": m, "status": "ok"}
