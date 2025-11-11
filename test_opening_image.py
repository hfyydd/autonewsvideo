#!/usr/bin/env python3
"""快速测试片头图片生成"""

from models.news import NewsItem, CardPoint
from services.image_generator import create_opening_slide


def create_sample_news():
    """创建示例新闻列表"""
    news_list = []

    news_titles = [
        ("月之暗面发布 Kimi K2 Thinking 模型", "36氪"),
        ("inceptionlabs发布下一代扩散模型 Mercury", "IT之家"),
        ("VS Code 内联补全功能开源", "少数派"),
        ("OpenRouter上线新stealth模型 Polaris Alpha", "机器之心"),
        ("Gemini API 发布文件搜索工具", "TechCrunch"),
        ("科大讯飞发布飞鸿火 X1.5 及AI产品", "新浪科技"),
    ]

    for i, (title, source) in enumerate(news_titles):
        news = NewsItem(
            title=title,
            source=source,
            url=f"https://example.com/{i}",
            published=f"2025-11-07T0{i}:00:00Z",
            raw_content=f"{title}的详细内容..."
        )
        news.card_title = title[:20] + ("..." if len(title) > 20 else "")
        news_list.append(news)

    return news_list


def test_all_styles():
    """测试所有风格的片头图片"""
    print("=" * 60)
    print("生成不同风格的片头图片")
    print("=" * 60)

    news_list = create_sample_news()
    print(f"\n✓ 已创建 {len(news_list)} 条示例新闻")

    styles = ["blue", "pink", "green", "purple"]

    for style in styles:
        print(f"\n正在生成 {style} 风格的片头图片...")
        try:
            # 修改输出文件名以区分不同风格
            import config
            import os
            original_image_dir = config.IMAGE_DIR

            image_path = create_opening_slide(news_list, style=style)

            # 重命名文件以包含风格名称
            style_image_path = image_path.replace("opening_slide.png", f"opening_slide_{style}.png")
            os.rename(image_path, style_image_path)

            print(f"✓ {style} 风格生成成功: {style_image_path}")
        except Exception as e:
            print(f"✗ {style} 风格生成失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print("✓ 所有风格生成完成！")
    print("=" * 60)
    print(f"\n图片保存在: {config.IMAGE_DIR}")
    print("文件名: opening_slide_blue.png, opening_slide_pink.png, opening_slide_green.png, opening_slide_purple.png")


if __name__ == "__main__":
    test_all_styles()
