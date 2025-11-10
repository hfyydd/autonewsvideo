#!/usr/bin/env python
"""
测试应用启动 - 不打开 GUI，只验证模块导入
"""

import sys

def test_imports():
    """测试所有模块导入"""
    print("测试模块导入...")

    try:
        print("  ✓ 导入 config")
        import config

        print("  ✓ 导入 models.news")
        from models.news import NewsItem, VideoProject

        print("  ✓ 导入 services")
        from services import (
            fetch_multiple_sources,
            generate_news_audio,
            create_adaptive_news_card,
            compose_news_collection_video,
        )

        print("  ✓ 导入 config_manager")
        from services.config_manager import ConfigManager

        print("\n✓ 所有模块导入成功！")
        return True

    except Exception as e:
        print(f"\n✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n测试配置管理器...")

    try:
        from services.config_manager import ConfigManager

        cm = ConfigManager()
        print("  ✓ ConfigManager 初始化")

        categories = cm.get_rss_categories()
        print(f"  ✓ RSS 分类: {len(categories)} 个")

        llm = cm.get_llm_config()
        print(f"  ✓ LLM 配置: {llm.get('model')}")

        print("\n✓ 配置管理器测试通过！")
        return True

    except Exception as e:
        print(f"\n✗ 配置管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("应用启动测试")
    print("=" * 60)
    print()

    success = True
    success = test_imports() and success
    success = test_config_manager() and success

    print()
    print("=" * 60)
    if success:
        print("✓ 所有测试通过！应用可以正常启动。")
        print("\n运行应用: uv run main.py")
    else:
        print("✗ 测试失败，请检查错误信息。")
        sys.exit(1)
    print("=" * 60)
