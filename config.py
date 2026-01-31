import os
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).parent

# 数据目录
DATA_DIR = BASE_DIR / "data"
MUSIC_DIR = DATA_DIR / "music"
OUTPUT_DIR = DATA_DIR / "outputs"

# 创建必要的目录
for dir_path in [DATA_DIR, MUSIC_DIR, OUTPUT_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# 允许的音乐文件扩展名
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'flac', 'm4a', 'aac'}

# 舞蹈风格关键词
DANCE_STYLES = {
    "赛乃姆": {
        "description": "维吾尔族传统舞蹈，柔美舒展",
        "tempo_range": (60, 90),
        "key_movements": ["移颈", "绕腕", "垫步", "点步"],
        "mood": ["抒情", "柔美", "舒展"]
    },
    "萨玛舞": {
        "description": "庄重肃穆的宗教舞蹈",
        "tempo_range": (50, 70),
        "key_movements": ["抬步俯身", "双手平展", "缓慢转身"],
        "mood": ["神圣", "庄重", "平缓"]
    },
    "刀郎舞": {
        "description": "活泼诙谐的民间舞蹈",
        "tempo_range": (90, 105),
        "key_movements": ["蹲步跳", "摇头晃肩", "模仿动物"],
        "mood": ["活泼", "幽默", "喜庆"]
    }
}

# 音乐处理配置
MUSIC_CONFIG = {
    "sample_rate": 22050,
    "n_fft": 2048,
    "hop_length": 512,
    "n_mels": 128
}

# 舞蹈生成配置
DANCE_CONFIG = {
    "frame_rate": 30,
    "joint_count": 25,  # 25个关节点
    "sequence_length": 300  # 10秒的序列
}