# LightOnOCR-1B-1025 运行指南

## 概述

LightOnOCR-1B-1025 是一个紧凑的端到端视觉-语言模型，用于光学字符识别 (OCR) 和文档理解。它在同类产品中达到最先进的准确率，同时比更大的通用 VLM 更快、更便宜。

## 环境要求

- **Docker**: 用于在 Ubuntu 容器中运行 vLLM
- **内存**: 建议 16GB+ RAM
- **CPU**: 支持 AVX512/AVX2 指令集

## 快速启动

### 1. 启动 Docker 服务

```bash
docker run -d -p 8000:8000 \
  -v /Users/ezgrid-dev/ai/ocr/model_cache:/root/.cache/huggingface \
  --name lighton-ocr \
  --privileged \
  --cap-add=SYS_NICE \
  --security-opt=seccomp:unconfined \
  -e VLLM_CPU_OMP_THREADS_BIND=0-3 \
  vllm/vllm-openai-cpu:latest-x86_64 \
  --model lightonai/LightOnOCR-1B-1025 \
  --limit-mm-per-prompt '{"image": 1}' \
  --api-key token-abc123
```

### 2. 验证服务状态

```bash
curl -s -H "Authorization: Bearer token-abc123" http://localhost:8000/v1/models
```

## 使用示例

### Python API 调用

```python
import base64
import requests
from PIL import Image
import io

ENDPOINT = "http://localhost:8000/v1/chat/completions"
MODEL = "lightonai/LightOnOCR-1B-1025"
API_KEY = "token-abc123"

# 读取图片并转为 base64
image = Image.open("your_image.jpg")
buffer = io.BytesIO()
image.save(buffer, format="JPEG")
image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

payload = {
    "model": MODEL,
    "messages": [{
        "role": "user",
        "content": [{
            "type": "image_url",
            "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
        }]
    }],
    "max_tokens": 4096,
    "temperature": 0.2,
    "top_p": 0.9,
}

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=600)
text = response.json()['choices'][0]['message']['content']
print(text)
```

### 测试脚本

项目中已包含测试脚本 `test_ocr_simple.py`，可以直接运行：

```bash
source .venv/bin/activate && python3 test_ocr_simple.py
```

## API 文档

服务启动后，可访问 OpenAPI 文档：

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 可用端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/v1/chat/completions` | POST | 聊天完成 (用于 OCR) |
| `/v1/completions` | POST | 文本完成 |
| `/v1/models` | GET | 列出可用模型 |
| `/health` | GET | 健康检查 |
| `/tokenize` | POST | 分词 |
| `/detokenize` | POST | 解码 |

## 性能说明

- **CPU 模式**: 首次请求需要较长时间进行模型编译和预热
- **内存占用**: 约需 8GB+ RAM
- **支持格式**: PDF (需转换为图片)、JPEG、PNG 等常见图片格式

## 注意事项

1. 首次启动会下载模型 (约 2GB)，请耐心等待
2. CPU 模式下推理速度较慢，单次 OCR 可能需要几分钟
3. 建议使用高分辨率图片以获得更好的识别效果
4. 模型缓存目录挂载到宿主机的 `/Users/ezgrid-dev/ai/ocr/model_cache`，避免重复下载

## 停止服务

```bash
docker stop lighton-ocr
docker rm lighton-ocr
```

## 参考

- [LightOnOCR Hugging Face](https://huggingface.co/lightonai/LightOnOCR-1B-1025)
- [vLLM 官方文档](https://docs.vllm.ai/)
