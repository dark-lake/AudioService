from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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


@app.websocket("/zhipu/{session_id}")
async def zhipu_api(websocket: WebSocket, session_id: str):
    await websocket.accept()
    print(session_id)
    while True:
        # todo 接收用户音频文件
        data = await websocket.receive_json()
        user_account = data.get("account")
        user_upload_audio = data.get('audio_data')
        user_upload_history = data.get('history')
        user_lang_type = data.get('lang_type', 'zh')
        user_upload_history = [] if user_upload_history is None else user_upload_history
        print(f'user_upload_base64: {len(user_upload_audio)}')
        if len(user_upload_audio) <= 0:
            text_data = await send_text_data("音频数据长度异常", [], 205)
            await websocket.send_json(text_data)
            continue
        async with aiofiles.open("audio_file/user_audio.wav", "wb") as f:
            await f.write(base64.b64decode(user_upload_audio))

        # todo 直接调用语音转文字接口
        response = await audio2text("audio_file/user_audio.wav", "zh")
        print(response)
        try:
            text = response.get("result")[0]
        except Exception:
            text_data = await send_text_data("音频质量太差", [], 207)
            await websocket.send_json(text_data)
            continue
        text_data = send_text_data(text, [], 203)

        # todo 保存用户聊天记录
        user_record = structure_record(user_account, session_id, "user", [text], [user_upload_audio], "wav")
        await save_record(user_record)

        # todo 返回大模型语音识别后的结果
        await websocket.send_json(text_data)
        print(f'打印语音转文字结果: {text}')
        # todo 处理英文回答的情况
        if user_lang_type in ['zh', 'en']:
            if user_lang_type != 'zh':
                text = text + ", 请用英文回答"
        else:
            data = await send_text_data("只能处理中文(zh)以及英文(en), 请检查输入lang_type类型是否存在", [], 208)
            await websocket.send_json(data)
            continue
        # todo 拿到完整的文字信息后请求大模型获得回答
        prompt = structure_prompt(text, user_upload_history)
        audio_str_all = ""  # 用于保存这次回答的所有句子连在一起, 用于返回用户历史使用
        text_data = []  # 用于存这次回答返回的句子数组, 用于保存聊天记录使用
        audio_data = []  # 用户保存单次的模型返回语音后转base64的字符串 , 用于保存聊天记录使用
        if user_lang_type == "en":
            async for to_audio_str in ask_model(prompt, 'en'):
                text = to_audio_str["text"]
                total_length = to_audio_str["length"]
                count = to_audio_str["count"]
                # over = to_audio_str["over"]  # 用于判断是否回答完毕了
                print(f'大模型回答:|{text}| length: {total_length}| count: {count}')

                # todo 将文字转为语音发送出去
                save_path = await text2audio(text, "zhipu_api/", "result" + str(count))
                data = await send_audio_data(save_path, text, [], 200)
                await websocket.send_json(data)

                audio_str_all += text
                text_data.append(text)
                audio_data.append(data.get("response"))
        else:
            async for to_audio_str in ask_model(prompt, 'zh'):
                text = to_audio_str["text"]
                total_length = to_audio_str["length"]
                count = to_audio_str["count"]
                # over = to_audio_str["over"]  # 用于判断是否回答完毕了
                print(f'大模型回答:|{text}| length: {total_length}| count: {count}')

                # todo 将文字转为语音发送出去
                save_path = await text2audio(text, "zhipu_api/", "result" + str(count))
                data = await send_audio_data(save_path, text, [], 200)
                await websocket.send_json(data)

                audio_str_all += text
                text_data.append(text)
                audio_data.append(data.get("response"))

        # todo 保存聊天assistant的record
        as_record = structure_record(user_account, session_id, "assistant", text_data, audio_data, "mp3")
        await save_record(as_record)

        # todo 这里要将用户最新的历史返回回去
        prompt.append({"role": "assistant", "content": audio_str_all})
        end_packet = send_text_data("_end_", prompt, 300)

        await websocket.send_json(end_packet)


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

    uvicorn.run(app=app, host="0.0.0.0", port=22222)
