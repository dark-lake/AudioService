import io

import aiofiles
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import wave
from funcs import *

app = FastAPI()

"""
zhipu api 的大模型
"""


@app.websocket("/")
async def audio_stream_test(websocket: WebSocket):
    await websocket.accept()
    while True:
        audio_data = await websocket.receive_bytes()
        # 将数据转换为音频流格式
        audio_stream = io.BytesIO(audio_data)
        with wave.open(audio_stream, "rb") as wave_file:
            wave_file.setnchannels(1)
            wave_file.setsampwidth(2)
            wave_file.setframerate(16000)
            with open('audio_file/audio_stream.wav', 'wb') as output_file:
                output_file.write(wave_file.readframes(wave_file.getnframes()))
        await websocket.close()

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app=app, host="0.0.0.0", port=22222)
