import os
import json
from typing import Dict, List
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# ===== API 配置 =====
# 尝试从用户配置文件加载
def _load_user_config():
    """加载用户配置文件"""
    config_file = "user_config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

_user_config = _load_user_config()
_llm_config = _user_config.get("llm", {})

# AI API 配置（支持 OpenAI 兼容接口）
# 优先级：用户配置 > 环境变量 > 默认值
AI_API_KEY = _llm_config.get("api_key") or os.getenv("AI_API_KEY", os.getenv("KIMI_API_KEY", ""))
AI_BASE_URL = _llm_config.get("base_url") or os.getenv("AI_BASE_URL", "https://api.moonshot.cn/v1")
AI_MODEL = _llm_config.get("model") or os.getenv("AI_MODEL", "kimi-k2-turbo-preview")

# 兼容旧配置
QWEN_API_KEY = AI_API_KEY  # 保持向后兼容
QWEN_BASE_URL = AI_BASE_URL
QWEN_MODEL = AI_MODEL

# ===== RSS 源预设配置 =====
# 从用户配置加载，如果没有则使用默认配置
_default_rss_presets = {
    "科技新闻": [
        {"name": "36氪", "url": "https://36kr.com/feed", "default_count": 5},
        {"name": "IT之家", "url": "https://www.ithome.com/rss/", "default_count": 3},
        {"name": "少数派", "url": "https://sspai.com/feed", "default_count": 3},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "default_count": 3},
    ],
    "财经新闻": [
        {"name": "华尔街见闻", "url": "https://wallstreetcn.com/feed", "default_count": 5},
        {"name": "财联社", "url": "https://www.cls.cn/rss", "default_count": 3},
    ],
    "国际新闻": [
        {"name": "BBC中文", "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml", "default_count": 5},
    ],
}

RSS_PRESETS: Dict[str, List[Dict[str, any]]] = _user_config.get("rss_sources", _default_rss_presets)

# ===== 图片生成配置 =====
LAYOUT_CONFIG = {
    "canvas_width": 1920,
    "canvas_height": 1080,
    "padding": 80,
    "title_font_size": 70,
    "point_font_size": 45,
    "meta_font_size": 35,
    "bullet_font_size": 50,
    "title_chars_per_line": 25,
    "point_chars_per_line": 35,
    "line_height": 65,
    "title_line_height": 90,
    "point_spacing": 25,
    "min_card_height": 500,
    "max_card_height": 980,
    "card_width_ratio": 0.85,
}

# 卡片配色方案（参考VS Code风格）
CARD_STYLES = {
    "blue": {
        "bg": (245, 245, 250),  # 浅灰背景
        "card_bg": (255, 255, 255),  # 纯白卡片
        "border": (64, 169, 255),  # 亮蓝色边框
        "accent": (64, 169, 255),  # 亮蓝色强调
        "title_color": (30, 30, 30),  # 深黑标题
        "text_color": (60, 60, 60),  # 深灰文字
        "meta_color": (140, 140, 140),  # 中灰元信息
        "icon": "💬",  # 图标
    },
    "pink": {
        "bg": (245, 245, 250),
        "card_bg": (255, 255, 255),
        "border": (255, 105, 180),  # 粉色边框
        "accent": (255, 105, 180),
        "title_color": (30, 30, 30),
        "text_color": (60, 60, 60),
        "meta_color": (140, 140, 140),
        "icon": "🚩",
    },
    "green": {
        "bg": (245, 245, 250),
        "card_bg": (255, 255, 255),
        "border": (120, 220, 120),  # 绿色边框
        "accent": (120, 220, 120),
        "title_color": (30, 30, 30),
        "text_color": (60, 60, 60),
        "meta_color": (140, 140, 140),
        "icon": "🔧",
    },
    "purple": {
        "bg": (245, 245, 250),
        "card_bg": (255, 255, 255),
        "border": (147, 112, 219),  # 紫色边框
        "accent": (147, 112, 219),
        "title_color": (30, 30, 30),
        "text_color": (60, 60, 60),
        "meta_color": (140, 140, 140),
        "icon": "📊",
    },
}

# ===== TTS 配置 =====
TTS_VOICES = {
    "中文女声": "zh-CN-XiaoxiaoNeural",
    "中文男声": "zh-CN-YunxiNeural",
    "中文女声2": "zh-CN-XiaoyiNeural",
    "中文男声2": "zh-CN-YunyangNeural",
}

TTS_DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"
TTS_RATE = "+0%"  # 语速
TTS_PITCH = "+0Hz"  # 音调

# ===== 视频配置 =====
VIDEO_FPS = 30
VIDEO_CODEC = "libx264"
VIDEO_AUDIO_CODEC = "aac"
VIDEO_BITRATE = "8000k"

# 字幕配置
SUBTITLE_CONFIG = {
    "enabled": False,  # 默认禁用字幕（字幕功能可能在某些环境下有问题）
    "font_size": 48,  # 字幕字体大小
    "font_color": "white",  # 字幕颜色
    "bg_color": (0, 0, 0),  # 字幕背景色（黑色）
    "bg_opacity": 0.6,  # 背景透明度
    "position": "bottom",  # 字幕位置：bottom/top/center
    "margin": 80,  # 距离底部的边距
    "max_width": 1600,  # 字幕最大宽度
}

# ===== 路径配置 =====
# 使用用户文档目录作为输出路径（跨平台兼容）
def _get_output_base_dir():
    """获取输出文件的基础目录（用户文档目录）"""
    from pathlib import Path

    # 获取用户文档目录
    if os.name == 'nt':  # Windows
        import ctypes.wintypes
        CSIDL_PERSONAL = 5  # My Documents
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        documents_dir = buf.value
    else:  # macOS, Linux
        documents_dir = str(Path.home() / "Documents")

    # 在文档目录下创建应用专属文件夹
    app_dir = os.path.join(documents_dir, "AutoNewsVideo")

    # 确保目录存在
    os.makedirs(app_dir, exist_ok=True)

    return app_dir

OUTPUT_DIR = os.path.join(_get_output_base_dir(), "output")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
AUDIO_DIR = os.path.join(OUTPUT_DIR, "audio")
VIDEO_DIR = os.path.join(OUTPUT_DIR, "videos")

# 字体目录使用应用程序所在目录的相对路径
FONT_DIR = "assets/fonts"

# 默认字体路径（如果没有字体文件，PIL 会使用默认字体）
DEFAULT_FONT_REGULAR = f"{FONT_DIR}/NotoSansSC-Regular.ttf"
DEFAULT_FONT_BOLD = f"{FONT_DIR}/NotoSansSC-Bold.ttf"


# ===== 配置检查 =====
def is_api_key_configured() -> bool:
    """检查 API Key 是否已配置"""
    return bool(AI_API_KEY and AI_API_KEY.strip())
