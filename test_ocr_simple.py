import base64
import requests
from PIL import Image
import io
import json

ENDPOINT = "http://localhost:8000/v1/chat/completions"
MODEL = "lightonai/LightOnOCR-1B-1025"
API_KEY = "token-abc123"

url = "https://huggingface.co/datasets/hf-internal-testing/fixtures_ocr/resolve/main/SROIE-receipt.jpeg"

print("Downloading image...")
response = requests.get(url)
image = Image.open(io.BytesIO(response.content))

print(f"Image size: {image.size}")

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

print("Sending request...")
response = requests.post(ENDPOINT, headers=headers, json=payload, timeout=600)
print(f"Status: {response.status_code}")

if response.status_code == 200:
    text = response.json()['choices'][0]['message']['content']
    print("\n=== OCR Result ===")
    print(text)
else:
    print(f"Error: {response.text}")
