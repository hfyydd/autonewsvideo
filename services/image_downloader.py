"""新闻配图下载和处理服务"""

import os
import requests
from PIL import Image
from typing import List
from models.news import NewsItem
import config


def download_and_process_images(news: NewsItem, index: int) -> List[str]:
    """
    下载并处理新闻配图

    Args:
        news: 新闻项
        index: 新闻索引（用于文件命名）

    Returns:
        下载的图片本地路径列表
    """
    downloaded_paths = []

    if not news.image_urls:
        return downloaded_paths

    # 确保目录存在
    os.makedirs(config.IMAGE_DIR, exist_ok=True)

    for i, url in enumerate(news.image_urls[:2]):  # 最多2张
        try:
            # 下载图片
            response = requests.get(url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            response.raise_for_status()

            # 保存原始图片
            temp_path = os.path.join(config.IMAGE_DIR, f"news_{index:03d}_photo_{i}.jpg")
            with open(temp_path, 'wb') as f:
                f.write(response.content)

            # 处理图片：调整尺寸为800x600（保持比例）
            processed_path = process_news_image(temp_path, index, i)
            downloaded_paths.append(processed_path)

            # 删除临时文件
            if os.path.exists(temp_path) and temp_path != processed_path:
                os.remove(temp_path)

        except Exception as e:
            print(f"  ⚠️ 下载图片失败 ({url}): {e}")
            continue

    return downloaded_paths


def process_news_image(image_path: str, news_index: int, photo_index: int) -> str:
    """
    处理新闻配图：调整尺寸、添加边距、居中显示

    目标：在1920x1080画布上居中显示，图片最大尺寸800x600

    Args:
        image_path: 原始图片路径
        news_index: 新闻索引
        photo_index: 图片索引

    Returns:
        处理后的图片路径
    """
    try:
        # 打开图片
        img = Image.open(image_path)
        img = img.convert('RGB')

        # 计算缩放比例（保持比例，最大800x600）
        max_width, max_height = 800, 600
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)

        # 创建1920x1080的白色画布
        canvas_width, canvas_height = 1920, 1080
        canvas = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))

        # 计算居中位置
        x = (canvas_width - img.width) // 2
        y = (canvas_height - img.height) // 2

        # 粘贴图片到画布中央
        canvas.paste(img, (x, y))

        # 保存处理后的图片
        output_path = os.path.join(config.IMAGE_DIR, f"news_{news_index:03d}_photo_{photo_index}_processed.jpg")
        canvas.save(output_path, quality=90)

        return output_path

    except Exception as e:
        print(f"  ⚠️ 处理图片失败: {e}")
        return image_path  # 返回原始路径


def download_images_for_news_list(news_list: List[NewsItem]) -> None:
    """
    批量下载新闻列表的配图

    Args:
        news_list: 新闻列表
    """
    for i, news in enumerate(news_list):
        if news.image_urls:
            print(f"  📥 下载新闻配图 ({i+1}/{len(news_list)}): {news.title[:20]}...")
            downloaded = download_and_process_images(news, i)
            news.downloaded_images = downloaded
            if downloaded:
                print(f"  ✅ 已下载 {len(downloaded)} 张配图")
