"""
简单测试脚本 - 验证各模块是否正常工作
"""

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")

    try:
        import config
        print("✓ config 导入成功")

        from models.news import NewsItem, VideoProject
        print("✓ models 导入成功")

        from services.rss_fetcher import fetch_single_source
        print("✓ rss_fetcher 导入成功")

        from services.ai_writer import generate_news_card_content
        print("✓ ai_writer 导入成功")

        from services.tts_service import generate_news_audio
        print("✓ tts_service 导入成功")

        from services.image_generator import create_adaptive_news_card
        print("✓ image_generator 导入成功")

        from services.video_composer import compose_news_collection_video
        print("✓ video_composer 导入成功")

        return True
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        return False


def test_config():
    """测试配置"""
    print("\n测试配置...")

    try:
        import config

        assert config.RSS_PRESETS, "RSS_PRESETS 不能为空"
        print(f"✓ 预设 RSS 源: {len(config.RSS_PRESETS)} 个分类")

        assert config.CARD_STYLES, "CARD_STYLES 不能为空"
        print(f"✓ 卡片样式: {list(config.CARD_STYLES.keys())}")

        assert config.TTS_VOICES, "TTS_VOICES 不能为空"
        print(f"✓ TTS 语音: {len(config.TTS_VOICES)} 种")

        return True
    except Exception as e:
        print(f"✗ 配置测试失败: {e}")
        return False


def test_models():
    """测试数据模型"""
    print("\n测试数据模型...")

    try:
        from models.news import NewsItem, VideoProject

        # 创建新闻对象
        news = NewsItem(
            title="测试新闻",
            source="测试源",
            url="https://example.com",
            published="2025-11-08",
            raw_content="这是测试内容"
        )

        assert news.title == "测试新闻"
        print("✓ NewsItem 创建成功")

        # 创建项目对象
        project = VideoProject(title="测试项目")
        assert project.title == "测试项目"
        print("✓ VideoProject 创建成功")

        return True
    except Exception as e:
        print(f"✗ 模型测试失败: {e}")
        return False


def test_rss_fetcher():
    """测试 RSS 获取（需要网络）"""
    print("\n测试 RSS 获取...")

    try:
        from services.rss_fetcher import fetch_single_source

        # 测试获取单个源
        news_list = fetch_single_source(
            url="https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
            source_name="BBC中文",
            count=2
        )

        if news_list:
            print(f"✓ 成功获取 {len(news_list)} 条新闻")
            print(f"  示例: {news_list[0].title[:30]}...")
        else:
            print("⚠ 未获取到新闻（可能是网络问题）")

        return True
    except Exception as e:
        print(f"✗ RSS 获取测试失败: {e}")
        return False


def test_ai_writer():
    """测试 AI 文案生成（使用 mock 模式）"""
    print("\n测试 AI 文案生成...")

    try:
        from models.news import NewsItem
        from services.ai_writer import _generate_mock_content

        news = NewsItem(
            title="OpenAI 发布新模型",
            source="36氪",
            url="https://example.com",
            published="2025-11-08",
            raw_content="OpenAI 今天发布了最新的语言模型。该模型在多项测试中表现优异。"
        )

        content = _generate_mock_content(news)

        assert "title" in content
        assert "points" in content
        assert len(content["points"]) >= 2

        print(f"✓ 文案生成成功")
        print(f"  标题: {content['title']}")
        print(f"  要点数: {len(content['points'])}")

        return True
    except Exception as e:
        print(f"✗ AI 文案测试失败: {e}")
        return False


def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始测试 autonewsvideo 项目")
    print("=" * 50)

    results = []

    results.append(("模块导入", test_imports()))
    results.append(("配置验证", test_config()))
    results.append(("数据模型", test_models()))
    results.append(("RSS 获取", test_rss_fetcher()))
    results.append(("AI 文案", test_ai_writer()))

    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{name:15} {status}")

    passed = sum(1 for _, r in results if r)
    total = len(results)

    print(f"\n总计: {passed}/{total} 项测试通过")

    if passed == total:
        print("\n🎉 所有测试通过！项目基本功能正常。")
    else:
        print("\n⚠️ 部分测试失败，请检查相关模块。")


if __name__ == "__main__":
    main()
