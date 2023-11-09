import base64
import datetime
import aiofiles
import zhipuai
from AudioTextAudio import *
import RedisConnectionPool

# todo 获取redis连接
redis_conn = RedisConnectionPool.redis_conn


async def invoke_zhipu_model(prompt: list):
    try:
        """
        prompt: [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "我是人工智能助手"},
            {"role": "user", "content": "你叫什么名字"},
            {"role": "assistant", "content": "我叫chatGLM"},
            {"role":"user", "content": "你都可以做些什么事"},
        ]
        """
        response = zhipuai.model_api.sse_invoke(
            model=zhipuai_config.get("MODEL_TYPE"),
            prompt=prompt,
            temperature=zhipuai_config.get("TEMPERATURE"),
            top_p=zhipuai_config.get("TOP_P"),
            incremental=zhipuai_config.get("INCREMENTAL")
        )
    except Exception as e:
        print(f'请求失败的情况')
        print(e)
        return

    for event in response.events():
        yield event


async def invoke_zhipu_model_curr(prompt: list):
    """
    同步版本的调用zhipuai的接口, 如何把整个接口弄成异步的还是有点困惑
    """
    try:
        """
        prompt: [
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "我是人工智能助手"},
            {"role": "user", "content": "你叫什么名字"},
            {"role": "assistant", "content": "我叫chatGLM"},
            {"role":"user", "content": "你都可以做些什么事"},
        ]
        """
        response = zhipuai.model_api.sse_invoke(
            model=zhipuai_config.get("MODEL_TYPE"),
            prompt=prompt,
            temperature=zhipuai_config.get("TEMPERATURE"),
            top_p=zhipuai_config.get("TOP_P"),
            incremental=zhipuai_config.get("INCREMENTAL")
        )
    except Exception as e:
        print(f'请求失败的情况')
        print(e)
        return

    resp_str_all = ''
    for response in response.events():
        event_status = response.event
        if event_status == "add":
            resp_str_all += response.data
            data_packet = send_text_data(response.data, [], 200)
            print(data_packet)
            yield json.dumps(data_packet, ensure_ascii=False).encode()
        elif event_status == "error" or event_status == "interrupted":
            data_packet = send_text_data("_error_", [], 500)
            yield json.dumps(data_packet, ensure_ascii=False).encode()
            break
        elif event_status == "finish":
            prompt.append(pack_record("assistant", resp_str_all))
            end_packet = send_text_data("_end_", prompt, 300)
            print(end_packet)
            yield json.dumps(end_packet, ensure_ascii=False).encode()
            break
        else:
            break


def invoke_zhipu_model_tb(prompt: list):
    """
    调用zhipu的同步版本
    :param prompt:
    :return:
    """
    try:
        """
            {"role": "user", "content": "你好"},
            {"role": "assistant", "content": "我是人工智能助手"},
            {"role": "user", "content": "你叫什么名字"},
            {"role": "assistant", "content": "我叫chatGLM"},
            {"role": "user", "content": "你都可以做些什么事"},
        """
        response = zhipuai.model_api.invoke(
            model=zhipuai_config.get("MODEL_TYPE"),
            prompt=prompt
        )
        code = response['code']
        if code != 200:
            print(response['msg'])
            return send_text_data('请求异常', [], code)
        else:
            assistant_data = response.get('data').get('choices')[0]
            prompt.append(assistant_data)
            text = assistant_data.get('content')
            return send_text_data(text, prompt, 200)
    except Exception as e:
        print(f'请求失败')
        print(e)
        return send_text_data('服务器异常', [], 500)


def structure_prompt(text: str, user_history: list):
    """
    负责建立提问大模型的prompt
    """
    if len(text) == 0:
        raise Exception("用户问题长度为0")

    # todo 处理多轮对话的长度,这里保留3轮,也就是6条即可
    if len(user_history) > 6:
        user_history = user_history[-6:]

    # todo 将用户最新的问题包装好加入到history 对于zhipu 此时的history就是 prompt
    user_question = pack_record("user", text)
    user_history.append(user_question)

    print(user_history)

    return user_history


def pack_record(role: str, content: str):
    return {"role": role, "content": content}


async def ask_model(prompt: list, lang_type='zh'):
    """
    实际的返回转音频的字符串, 主要目的就是调整转音频字符串的长度
    """
    if len(prompt) == 0:
        raise Exception("prompt长度为0")

    to_audio_str = ""
    first = True
    total_length = 0  # 记录这次回答的总长度
    count = 0  # 记录这次回答一共走了生成了多少次回答
    async for response in invoke_zhipu_model(prompt):
        event_status = response.event
        if lang_type == 'en':
            response_data = response.data.replace("\n", "").replace("\t", "")
        else:
            response_data = response.data.replace("\n", "").replace("\t", "").replace(" ", "")
        total_length += len(response_data)
        count += 1
        if event_status == "add":
            to_audio_str += response_data
            print(f'------------>此时的 {to_audio_str}')
            if response_data[-1:] in [',', '，', '.', '。', '!', '?']:
                yield {"text": to_audio_str, "length": total_length, "count": count, "over": False}
                to_audio_str = ''
            # if len(to_audio_str) >= 4 and first:
            #     yield {"text": to_audio_str, "length": total_length, "count": count, "over": False}
            #     to_audio_str = ''
            #     first = False
            # elif len(to_audio_str) >= 15:
            #     yield {"text": to_audio_str, "length": total_length, "count": count, "over": False}
            #     to_audio_str = ''
            else:
                continue
        elif event_status == "error" or response.event == "interrupted":
            # yield event.data
            break
        elif event_status == "finish":
            # todo 这里要处理一下如果刚好to_audio_str此时是''的情况
            if len(to_audio_str) != 0:
                yield {"text": to_audio_str, "length": total_length, "count": count, "over": True}
            print(f'event.meta: {response.meta}')
            break
        else:
            break


async def send_audio_data(audio_path, text_response, history, status, delete=True):
    async with aiofiles.open(audio_path, 'rb') as f:
        temp_data = await f.read()

    # todo 这里将该音频文件删除一下
    try:
        if delete:
            os.remove(audio_path)
    except Exception:
        pass

    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "text_response": text_response,
        "audio_response": base64.b64encode(temp_data).decode('utf-8'),
        # "audio_response": base64.b64encode(audio_path).decode('utf-8'),
        "history": history,
        "status": status,
        "time": time
    }


def send_text_data(text_response, history, status):
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "text_response": text_response,
        "history": history,
        "status": status,
        "time": time
    }


async def save_record(chat_record: dict):
    # 保存聊天记录
    """
    接受用户传过来的聊天记录格式,然后存入到redis

    下面很多异常处理都没有写, 虽然都是我自己写, 但是没有标准, 写了还要变, 就搞得很难受,
    希望以后能和后面的学弟学妹一起规定一套标准的异常规则
    """
    global redis_conn
    if not redis_conn.ping():
        # 这里写redis连接失败的情况
        redis_conn = RedisConnectionPool.redis_conn

    # todo 构建redis中的key 这里使用 account_session_id组合
    account = chat_record.get("account")
    session_id = chat_record.get("session_id")
    redis_key = account + "_" + session_id

    # todo 开始将聊天记录存入到里面, 这里使用 redis 的 list 类型
    result_code = redis_conn.rpush(redis_key, json.dumps(chat_record))
    if result_code != -1:
        # 这里可以写返回信息
        pass
    else:
        # 这里写保存失败的情况
        pass


def structure_record(account: str, session_id: str, role: str, text_data: list, audio_data: list,
                     audio_format: str):
    """
    构造聊天记录
    """
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    return {
        "account": account,
        "session_id": session_id,
        "role": role,
        "text_data": text_data,
        "audio_data": audio_data,
        "audio_format": audio_format,
        "time": time
    }


if __name__ == '__main__':
    pass
