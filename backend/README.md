# Voice Draw — Qwen2.5-0.5B NLP Backend

基于 Qwen2.5-0.5B-Instruct 的中文语音命令解析服务。

## 环境要求

- Python 3.10+
- 4GB+ 内存（CPU 运行）
- 约 2GB 磁盘空间（模型下载）

## 安装

```bash
# 进入后端目录
cd backend

# 安装依赖
pip install -r requirements.txt
```

## 启动

```bash
# 加载模型 + 启动服务
uvicorn server:app --host 0.0.0.0 --port 8080
```

首次启动需要下载模型（约 1GB），下载一次后会自动缓存。

## API

### `GET /load`
加载模型到内存。启动后首次使用前调用。

### `POST /parse`
解析自然语言命令。

**请求：**
```json
{"text": "在左上角画一个红色的圆"}
```

**响应：**
```json
{
  "intent": "DRAW_SHAPE",
  "shape": "circle",
  "color": "red",
  "position": {"x": 50, "y": 50}
}
```

### `GET /`
健康检查。

## 前端使用

1. 启动后端服务
2. 打开 `index.html`
3. 点击 `🧠 本地模式` 按钮切换为 `🧠 AI模式`
4. AI 模式会调用后端解析命令，失败时自动回退到本地模式
