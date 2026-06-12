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

class ParseRequest(BaseModel):
    text: str

class Position(BaseModel):
    x: int
    y: int

class ParseResponse(BaseModel):
    intent: str
    shape: Optional[str] = None
    color: Optional[str] = None
    position: Optional[Position] = None
    from_pos: Optional[Position] = None
    to_pos: Optional[Position] = None
    size: Optional[int] = None
    direction: Optional[str] = None
    raw_text: str = ""
    reasoning: str = ""

# ── Model globals (lazy-loaded) ───────────────────────────
model = None
tokenizer = None
device = "cpu"

# ── System prompt ─────────────────────────────────────────

SYSTEM_PROMPT = """你是一个语音绘图助手的命令解析器。用户说一句话，你需要理解意图并提取参数。

可用的意图（intent）：
- DRAW_SHAPE: 画图形（圆、矩形等）
- LINE: 画线
- MOVE: 移动画笔位置
- SET_COLOR: 设置颜色
- SET_SIZE: 设置半径/大小
- CLEAR: 清空画布
- UNDO: 撤销
- SAVE: 保存图片

可用的形状（shape）：
- circle: 圆、圆形、圆圈
- rect: 矩形、长方形、正方形、方块

可用的颜色（color）：
- red: 红色、红
- blue: 蓝色、蓝
- green: 绿色、绿
- yellow: 黄色、黄
- black: 黑色、黑
- white: 白色、白
- orange: 橙色、橙
- purple: 紫色、紫
- pink: 粉色、粉

可用的位置（position / from_pos / to_pos）：
- 左上角 → x:50, y:50
- 右上角 → x:750, y:50
- 左下角 → x:50, y:550
- 右下角 → x:750, y:550
- 中心 / 中央 / 中间 → x:400, y:300
- 也支持直接数字坐标: x:100, y:200

可用的方向（direction）：
- 左 / 往左 / 向左
- 右 / 往右 / 向右
- 上 / 往上 / 向上
- 下 / 往下 / 向下
- 左上 / 左下 / 右上 / 右下

只输出JSON，不要任何其他文字。
JSON字段只包含有意义的参数，不要随意填充。

示例1: "在左上角画一个红色的圆"
{"intent":"DRAW_SHAPE","shape":"circle","color":"red","position":{"x":50,"y":50}}

示例2: "从左上角到右下角画线"
{"intent":"LINE","from_pos":{"x":50,"y":50},"to_pos":{"x":750,"y":550}}

示例3: "红色"
{"intent":"SET_COLOR","color":"red"}

示例4: "撤销"
{"intent":"UNDO"}

示例5: "半径80"
{"intent":"SET_SIZE","size":80}

示例6: "往左一点"
{"intent":"MOVE","direction":"左"}

示例7: "向右画线"
{"intent":"LINE","direction":"右"}

示例8: "保存"
{"intent":"SAVE"}

示例9: "清空"
{"intent":"CLEAR"}"""


# ── Prompt builder ────────────────────────────────────────

def build_prompt(user_text: str) -> str:
    return f"""<|im_start|>system
{SYSTEM_PROMPT}
<|im_end|>
<|im_start|>user
{user_text}
<|im_end|>
<|im_start|>assistant
"""


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

    return ParseResponse(
        intent=data.get("intent", ""),
        shape=data.get("shape"),
        color=data.get("color"),
        position=to_pos(data.get("position")),
        from_pos=to_pos(data.get("from_pos")),
        to_pos=to_pos(data.get("to_pos")),
        size=data.get("size"),
        direction=data.get("direction"),
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
            max_new_tokens=128,
            temperature=0.1,
            top_p=0.9,
            do_sample=True,
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
    use_8bit = os.environ.get("MODEL_8BIT", "1") == "1"  # default on for 1.5B
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
    return {"service": "Voice Draw NLP Backend", "model": "Qwen2.5-0.5B-Instruct", "status": "ok"}
