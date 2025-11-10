from dataclasses import dataclass, field
from typing import List, Union


@dataclass
class CardPoint:
    """卡片要点数据模型"""
    subtitle: str  # 4-6字的小标题
    content: str   # 25-35字的详细内容


@dataclass
class NewsItem:
    """单条新闻数据模型"""
    title: str
    source: str
    url: str
    published: str
    raw_content: str
    selected: bool = False
    image_urls: List[str] = field(default_factory=list)  # RSS中的新闻配图URL（最多2张）

    # AI 生成的内容
    # 1. TTS 文案（用于语音合成）- AI总结的新闻播报稿
    tts_script: str = ""  # 完整的播报文案，用于转语音

    # 2. 卡片内容（用于图片显示）- 从播报稿提取的关键信息
    card_title: str = ""  # 卡片标题
    card_points: List[Union[CardPoint, str]] = field(default_factory=list)  # 支持新旧格式

    # 生成的资源
    image_path: str = ""  # 生成的卡片图片路径
    audio_path: str = ""  # 生成的音频路径
    duration: float = 0.0  # 音频时长
    downloaded_images: List[str] = field(default_factory=list)  # 下载的新闻配图本地路径
    selected_images: List[bool] = field(default_factory=list)  # 标记哪些配图被用户选中使用（默认都不选中）


@dataclass
class VideoProject:
    """视频项目配置"""
    title: str
    news_items: List[NewsItem] = field(default_factory=list)
    template_style: str = "blue"  # blue/pink/green/purple
    output_path: str = ""

    def get_selected_news(self) -> List[NewsItem]:
        """获取已选中的新闻"""
        return [news for news in self.news_items if news.selected]

    def get_total_duration(self) -> float:
        """获取总时长"""
        return sum(news.duration for news in self.get_selected_news())
