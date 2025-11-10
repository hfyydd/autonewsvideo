import feedparser
from typing import List, Dict
from models.news import NewsItem
from datetime import datetime


def fetch_single_source(url: str, source_name: str, count: int = 5) -> List[NewsItem]:
    """
    从单个 RSS 源获取新闻

    Args:
        url: RSS 源 URL
        source_name: 来源名称
        count: 获取数量

    Returns:
        新闻列表
    """
    news_list = []

    try:
        feed = feedparser.parse(url)

        if not feed.entries:
            print(f"警告: {source_name} 未获取到内容")
            return news_list

        for entry in feed.entries[:count]:
            # 提取发布时间
            published = entry.get("published", "")
            if not published and hasattr(entry, "published_parsed"):
                try:
                    published = datetime(*entry.published_parsed[:6]).isoformat()
                except:
                    published = datetime.now().isoformat()

            # 提取内容
            raw_content = entry.get("summary", entry.get("description", ""))

            # 提取图片URL（最多2张）
            image_urls = []

            # 方法1: media_content (Media RSS)
            if hasattr(entry, 'media_content'):
                for media in entry.media_content[:2]:
                    if media.get('medium') == 'image' or media.get('type', '').startswith('image/'):
                        image_urls.append(media.get('url'))

            # 方法2: enclosures (附件)
            if len(image_urls) < 2 and hasattr(entry, 'enclosures'):
                for enc in entry.enclosures:
                    if enc.get('type', '').startswith('image/'):
                        image_urls.append(enc.get('href', ''))
                        if len(image_urls) >= 2:
                            break

            # 方法3: media_thumbnail
            if len(image_urls) < 2 and hasattr(entry, 'media_thumbnail'):
                for thumb in entry.media_thumbnail[:2-len(image_urls)]:
                    image_urls.append(thumb.get('url'))

            news = NewsItem(
                title=entry.get("title", "无标题"),
                source=source_name,
                url=entry.get("link", ""),
                published=published,
                raw_content=raw_content[:500],  # 限制长度
                selected=False,
                image_urls=image_urls[:2]  # 最多保留2张
            )
            news_list.append(news)

    except Exception as e:
        print(f"获取 {source_name} 失败: {e}")

    return news_list


def fetch_multiple_sources(sources: List[Dict]) -> List[NewsItem]:
    """
    从多个 RSS 源批量获取新闻

    Args:
        sources: RSS 源配置列表
                 [{"name": "36氪", "url": "...", "count": 5}, ...]

    Returns:
        所有新闻的合并列表（按时间排序）
    """
    all_news = []

    for source in sources:
        url = source.get("url", "")
        name = source.get("name", "未知来源")
        count = source.get("count", 5)

        if not url:
            continue

        news_list = fetch_single_source(url, name, count)
        all_news.extend(news_list)

    # 按发布时间排序（最新的在前）
    all_news.sort(key=lambda x: x.published, reverse=True)

    return all_news
