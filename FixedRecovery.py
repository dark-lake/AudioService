import config
import os

# todo 获取固定回复音频文件的基本路径
base_path = config.audio_save_path

fixed_audio = {
    # todo 异常情况回复的固定语音
    "exception": {
        "poor_quality": {
            "audio_path": "./" + base_path + "/" + "poor_quality.mp3",
            "audio_text": "不好意思，我没有听清您说的话。"
        },
        "repeat": {
            "audio_path": "./" + base_path + "/" + "repeat.mp3",
            "audio_text": "您可以再说一遍吗?"
        }
    },
    # todo 提示用户
    "tips": {
        "help": {
            "audio_path": "./" + base_path + "/" + "help.mp3",
            "audio_text": "您还有什么问题吗?"
        }
    }
}

