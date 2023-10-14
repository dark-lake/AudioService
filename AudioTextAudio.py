import json
import os
from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode

from config import *
from urllib.parse import quote_plus


# todo 用于抛出异常
class DemoError(Exception):
    pass


def fetch_token(api_key, secret_key):
    """
    用于身份验证的,不用管
    :return:
    """
    params = {'grant_type': 'client_credentials',
              'client_id': api_key,
              'client_secret': secret_key}
    post_data = urlencode(params)
    post_data = post_data.encode('utf-8')
    req = Request(TOKEN_URL, post_data)
    try:
        f = urlopen(req)
        result_str = f.read()
    except URLError as err:
        print('token http response http code : ' + str(err.code))
        result_str = err.read()

    result_str = result_str.decode()

    result = json.loads(result_str)
    if ('access_token' in result.keys() and 'scope' in result.keys()):
        if SCOPE and (not SCOPE in result['scope'].split(' ')):  # SCOPE = False 忽略检查
            raise DemoError('scope is not correct')
        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
        return result['access_token']
    else:
        raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')


async def audio2text(audio_path, lang_type="zh") -> dict:
    """
    音频转文本函数, 输入音频文件的路径, 默认识别是中文类型
    """

    token = fetch_token(HC_API_KEY, HC_SECRET_KEY)

    # todo 设置识别语言类型
    lang_type = DEV_PID if lang_type == "zh" else ENG_PID

    # 文件格式 文件后缀只支持 pcm/wav/amr 格式，极速版额外支持m4a 格式, m4a主要是针对微信小程序的格式
    format = audio_path[-3:]

    with open(audio_path, 'rb') as f:
        speech_data = f.read()

    audio_length = len(speech_data)

    if audio_length == 0:
        raise DemoError('file %s length read 0 bytes' % audio_path)

    params = {'cuid': CUID, 'token': token, 'dev_pid': lang_type}
    params_query = urlencode(params)
    headers = {
        'Content-Type': 'audio/' + format + '; rate=' + str(RATE),
        'Content-Length': audio_length
    }
    req = Request(ASR_URL + "?" + params_query, speech_data, headers)

    try:
        f = urlopen(req)
        result_str = f.read()
        """
            {
                'corpus_no': '7255603449714004102', 
                'err_msg': 'success.', 
                'err_no': 0, 
                'result': ['北京科技馆。'], 
                'sn': '693622223131689326821'
            }
        """
        result_str = json.loads(result_str)
    except URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()

    return result_str


async def text2audio(text, save_path, file_name):
    if len(text) == 0:
        return "文本长度为0,请检查输入文本是否正确"

    token = fetch_token(HC_API_KEY, HC_SECRET_KEY)
    tex = quote_plus(text)  # 此处TEXT需要两次urlencode
    params = {'tok': token, 'tex': tex, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': AUE, 'cuid': CUID,
              'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数

    data = urlencode(params)
    # print('test on Web Browser' + TTS_URL + '?' + data)

    req = Request(TTS_URL, data.encode('utf-8'))
    has_error = False
    try:
        f = urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        has_error = ('content-type' not in headers.keys() or headers['content-type'].find('audio/') < 0)
    except URLError as err:
        print('asr http response http code : ' + str(err.code))
        result_str = err.read()
        has_error = True

    save_file = "error.txt" if has_error else file_name + "." + FORMAT
    save_path = os.path.join(save_path, save_file)

    with open(save_path, 'wb') as of:
        of.write(result_str)

    if has_error:
        result_str = str(result_str, 'utf-8')
        print("tts api error:" + result_str)

    return save_path


if __name__ == '__main__':
    result = text2audio("hello my name is fengtao", "zhipu_api/", "result1")
    print(result)
