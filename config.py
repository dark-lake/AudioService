# 语音识别配置
# 这个需要去百度的那个控制台里面注册账号,创建应用之后就可以得到
API_KEY = 'rAq59wfcAeGfAHmGhMsINulr'
SECRET_KEY = 'sB3leyHa6ZhYIcAQyfcugtn3GSbbOGCP'

CUID = 'chronic_disease'

# 采样率 固定不变
RATE = 16000

# 模型的版本设置, 申请的接口 scope可以去具体查,这里就不用动了
DEV_PID = 1537  # 1537 表示识别普通话，使用输入法模型。根据文档填写PID，选择语言及识别模型,
ENG_PID = 1737  # 英文模型
ASR_URL = 'http://vop.baidu.com/server_api'
SCOPE = 'audio_voice_assistant_get'  # 有此scope表示有asr能力，没有请在网页里勾选，非常旧的应用可能没有

# 调用语音识别接口前,需要先经过一个身份验证, 这个是验证时候的请求地址
TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'

# 语音合成配置
HC_API_KEY = "CYrPvnAW6ktFkezSb4hBQqWY"
HC_SECRET_KEY = "PqaV3LgRg81YCFG0BatAvvvxccV1HQaA"
# 发音人选择, 基础音库：0为度小美，1为度小宇，3为度逍遥，4为度丫丫，
# 精品音库：5为度小娇，103为度米朵，106为度博文，110为度小童，111为度小萌，默认为度小美
PER = 0
# 语速，取值0-15，默认为5中语速
SPD = 5
# 音调，取值0-15，默认为5中语调
PIT = 5
# 音量，取值0-9，默认为5中音量
VOL = 5
# 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
AUE = 3

FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
FORMAT = FORMATS[AUE]

# 语音合成地址
TTS_URL = 'http://tsn.baidu.com/text2audio'

# 对话大模型调用地址
url = 'https://Sdia-LLM-KG-qm1yr71e2p69.serv-c1.openbayes.net'  # 替换成你的URL

# 音频文件保存路径
audio_save_path = "zhipu_api"

# 科大讯飞
APPID = "3ba265fd"
APISecret = "ZjczMjg2YjQ2YTFlMjM0N2IyMjgzZDhi"
APIKey = "bc7f337419878c954ca248d2de8fa6da"

# zhipu api key
zhipuai_config = {
    'ZHIPU_API_KEY': 'fe559d96a17366af7b891b6f0890abb3.j0oDGLMnttt7R824',
    'MODEL_TYPE': 'chatglm_turbo',
    'TEMPERATURE': 0.95,
    'TOP_P': 0.7,
    'INCREMENTAL': True
}

# redis
redis_config = {
    'host': '182.92.154.119',
    'port': 6379,
    'db': 0,
    'password': 'Sigsit123',
    'max_connections': 30
}
# fixed recovery
fixed_recovery = {

}