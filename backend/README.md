# Voice Draw — NLP Backend（支持 Ollama + 本地模型）

支持两种后端模式，默认使用 Ollama API（Qwen2.5:7b），备选本地 transformers 模型。

## 环境要求

- Python 3.10+
- 4GB+ 内存（CPU 运行）
- [Ollama](https://ollama.com/)（默认模式需要）
- 约 3GB 磁盘空间（模型下载）

## 安装

```bash
cd backend
pip install -r requirements.txt
```

### 安装 Ollama 并拉取模型

```bash
# 安装 Ollama（如果还没装）
# https://ollama.com/download

# 拉取推荐模型
ollama pull qwen2.5:7b

# 确保 Ollama 服务在运行
ollama serve
```

## 启动

```bash
# 默认：使用 Ollama（qwen2.5:7b）
uvicorn server:app --host 0.0.0.0 --port 8080

# 本地模式：使用 transformers 模型
BACKEND=local uvicorn server:app --host 0.0.0.0 --port 8080

# 自动模式：Ollama 优先，离线时自动降级本地
BACKEND=auto uvicorn server:app --host 0.0.0.0 --port 8080
```

## 配置

通过环境变量切换：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `BACKEND` | 后端模式：ollama / local / auto | `ollama` |
| `OLLAMA_URL` | Ollama 服务地址 | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama 模型名 | `qwen2.5:7b` |
| `MODEL_NAME` | 本地 transformers 模型 | `Qwen/Qwen2.5-1.5B-Instruct` |

## API

### `GET /`
健康检查，返回当前后端状态。

### `POST /parse`
解析自然语言命令。

```json
{"text": "在左上角画一个红色的圆"}

→ {"intent": "DRAW_SHAPE", "shape": "circle", "color": "red", "position": {"x": 50, "y": 50}}
```

### `GET /load`
加载本地 transformers 模型（仅 local / auto 模式需要）。

## 前端使用

1. 启动后端
2. 打开 `index.html`
3. 点击 `🧠 本地模式` → 切换为 `🧠 AI模式`
4. 语音命令会自动发往后端解析
