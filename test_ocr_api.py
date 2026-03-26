import base64
import requests
import pypdfium2 as pdfium
import io
import json

ENDPOINT = "http://localhost:8000/v1/chat/completions"
MODEL = "lightonai/LightOnOCR-1B-1025"
API_KEY = "token-abc123"

pdf_url = "https://arxiv.org/pdf/2412.13663"
pdf_data = requests.get(pdf_url).content

pdf = pdfium.PdfDocument(pdf_data)
page = pdf[0]
pil_image = page.render(scale=2.77).to_pil()

buffer = io.BytesIO()
pil_image.save(buffer, format="PNG")
image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

payload = {
    "model": MODEL,
    "messages": [{
        "role": "user",
        "content": [{
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{image_base64}"}
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

print("Sending request to OCR service...")
response = requests.post(ENDPOINT, headers=headers, json=payload)

print(f"Status code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    text = result['choices'][0]['message']['content']
    print("\n=== OCR Result ===")
    print(text[:2000])
    if len(text) > 2000:
        print(f"\n... ({len(text) - 2000} more characters)")
else:
    print(f"Error: {response.text}")
