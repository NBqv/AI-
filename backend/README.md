# Voice Draw — Qwen2.5 NLP Backend

基于 Qwen2.5 系列模型的中文语音命令解析服务（默认使用 1.5B，支持 0.5B）。

## 环境要求

- Python 3.10+
- 4GB+ 内存（CPU 运行）
- 约 3GB 磁盘空间（模型下载）

## 安装

```bash
cd backend
pip install -r requirements.txt
```

## 启动

```bash
# 默认启动（Qwen2.5-1.5B-Instruct + 8bit量化）
uvicorn server:app --host 0.0.0.0 --port 8080
```

首次启动会自动下载模型，下载一次后缓存。

## 配置

通过环境变量切换：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| `MODEL_NAME` | 模型名称 | `Qwen/Qwen2.5-1.5B-Instruct` |
| `MODEL_8BIT` | 是否启用 8bit 量化（减少内存） | `1` (启用) |

**示例：使用 0.5B 模型，关闭量化**
```bash
MODEL_NAME=Qwen/Qwen2.5-0.5B-Instruct MODEL_8BIT=0 uvicorn server:app --port 8080
```

**推荐模型：**

| 模型 | 参数量 | 内存 | 推理速度 | 适合 |
|------|--------|------|---------|------|
| Qwen2.5-0.5B-Instruct | 0.5B | ~1GB | ~2-4s | 低内存设备 |
| Qwen2.5-1.5B-Instruct | 1.5B | ~2GB (8bit) | ~5-10s | **默认推荐** |

## API

### `GET /load`
加载模型到内存。调用一次即可。

### `POST /parse`
解析自然语言命令。

```json
{"text": "在左上角画一个红色的圆"}

→ {"intent": "DRAW_SHAPE", "shape": "circle", "color": "red", "position": {"x": 50, "y": 50}}
```

### `GET /`
健康检查。

## 前端使用

1. 启动后端
2. 打开 `index.html`
3. 点击 `🧠 本地模式` → 切换为 `🧠 AI模式`
4. 语音命令会自动发往后端解析
