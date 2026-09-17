from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import json
import re
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv() 

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv('KEY')
)

class FilterRequest(BaseModel):
    query: str

SYSTEM_PROMPT = """你是一个点云数据过滤指令解析器。
用户会用自然语言描述他们想对点云数据做什么操作。
你需要将用户的自然语言解析为 JSON 格式的过滤参数。

支持的过滤类型：
1. 按高度过滤：{"filter": {"minHeight": 数字}}
2. 按区域裁剪：{"filter": {"clipBox": {"size": [x, y, z], "position": [x, y, z]}}}

规则：
- 用户说"高度超过 10 米" → {"filter": {"minHeight": 10}}
- 用户说"裁剪一个 20x20x20 的区域" → {"filter": {"clipBox": {"size": [20,20,20], "position": [0,0,0]}}}
- 只返回 JSON，不要有其他内容。
- 无法解析时返回 {"filter": null}
"""

@app.post("/parse")
async def parse_filter(req: FilterRequest):
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": req.query}
            ],
            temperature=0.1,
            max_tokens=200
        )
        content = response.choices[0].message.content.strip()
        json_match = re.search(r'\{[\s\S]*\}', content)
        result = json.loads(json_match.group()) if json_match else {"filter": None}
        return result
    except Exception as e:
        return {"filter": None, "error": str(e)}

@app.get("/health")
async def health():
    return {"status": "ok"}