#!/usr/bin/env python3
"""测试片头生成功能"""

import asyncio
from models.news import NewsItem, CardPoint
from services.ai_writer import generate_opening_script
from services.tts_service import generate_opening_audio
from services.image_generator import create_opening_slide


def create_mock_news_list():
    """创建模拟新闻列表用于测试"""
    news_list = []

    # 新闻1
    news1 = NewsItem(
        title="月之暗面发布 Kimi K2 Thinking 模型",
        source="36氪",
        url="https://example.com/1",
        published="2025-11-07T00:10:00Z",
        raw_content="月之暗面发布最新AI模型Kimi K2 Thinking，具有强大的推理能力。"
    )
    news1.card_title = "Kimi K2 Thinking模型发布"
    news1.card_points = [
        CardPoint(subtitle="模型发布", content="月之暗面正式发布Kimi K2 Thinking模型"),
        CardPoint(subtitle="核心能力", content="具备强大的逻辑推理和问题解决能力"),
    ]
    news_list.append(news1)

    # 新闻2
    news2 = NewsItem(
        title="OpenAI修复云任务问题并提供免费积分",
        source="IT之家",
        url="https://example.com/2",
        published="2025-11-07T01:19:00Z",
        raw_content="OpenAI修复了云任务问题，并为受影响用户提供免费积分补偿。"
    )
    news2.card_title = "OpenAI修复问题送积分"
    news2.card_points = [
        CardPoint(subtitle="问题修复", content="OpenAI成功修复云任务服务问题"),
        CardPoint(subtitle="用户补偿", content="为受影响用户提供免费API积分"),
    ]
    news_list.append(news2)

    # 新闻3
    news3 = NewsItem(
        title="GPT-5.1 thinking 字符现身OpenAI网站",
        source="机器之心",
        url="https://example.com/3",
        published="2025-11-07T03:05:00Z",
        raw_content="GPT-5.1 thinking模型的字符串意外出现在OpenAI官方网站代码中。"
    )
    news3.card_title = "GPT-5.1 thinking曝光"
    news3.card_points = [
        CardPoint(subtitle="模型曝光", content="GPT-5.1 thinking字符现身OpenAI网站"),
        CardPoint(subtitle="新特性", content="可能具备更强大的思维链推理能力"),
    ]
    news_list.append(news3)

    return news_list


async def test_opening():
    """测试片头生成"""
    print("=" * 60)
    print("测试片头生成功能")
    print("=" * 60)

    # 创建模拟新闻
    news_list = create_mock_news_list()
    print(f"\n✓ 已创建 {len(news_list)} 条模拟新闻")

    # 测试1: 生成片头文案
    print("\n[1/3] 测试片头文案生成...")
    try:
        opening_script = generate_opening_script(news_list)
        print(f"✓ 片头文案生成成功:")
        print(f"  {opening_script}")
    except Exception as e:
        print(f"✗ 片头文案生成失败: {e}")
        return

    # 测试2: 生成片头语音
    print("\n[2/3] 测试片头语音生成...")
    try:
        opening_audio_path, opening_duration = await generate_opening_audio(opening_script)
        print(f"✓ 片头语音生成成功:")
        print(f"  路径: {opening_audio_path}")
        print(f"  时长: {opening_duration:.1f} 秒")
    except Exception as e:
        print(f"✗ 片头语音生成失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 测试3: 生成片头图片
    print("\n[3/3] 测试片头图片生成...")
    try:
        opening_image_path = create_opening_slide(news_list, style="blue")
        print(f"✓ 片头图片生成成功:")
        print(f"  路径: {opening_image_path}")
    except Exception as e:
        print(f"✗ 片头图片生成失败: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n" + "=" * 60)
    print("✓ 所有测试通过！")
    print("=" * 60)
    print(f"\n片头资源:")
    print(f"  - 文案: {opening_script}")
    print(f"  - 语音: {opening_audio_path} ({opening_duration:.1f}秒)")
    print(f"  - 图片: {opening_image_path}")


if __name__ == "__main__":
    asyncio.run(test_opening())
