from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from funcs import *

zhipuai.api_key = zhipuai_config.get("ZHIPU_API_KEY")

app = FastAPI()

# 解决跨域问题
# origins = [
#     "http://localhost",
#     "http://localhost:8080",
# ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

"""
zhipu api 的大模型
"""


class ZhipuPrompt(BaseModel):
    question: str
    history: list


@app.post("/zhipu_text")
async def zhipu_text(item: ZhipuPrompt):
    print(item.question)
    print(item.history)

    # todo 构造prompt
    prompt = structure_prompt(item.question, item.history)
    return StreamingResponse(invoke_zhipu_model_curr(prompt))


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app="main_text:app", host="0.0.0.0", port=22223, workers=1)
