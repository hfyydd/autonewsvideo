#!/usr/bin/env python
"""
快速测试配置功能
"""

from services.config_manager import ConfigManager

def test_config_manager():
    print("=" * 50)
    print("测试配置管理器")
    print("=" * 50)

    # 创建配置管理器
    cm = ConfigManager()
    print("\n✓ 配置管理器初始化成功")

    # 测试 LLM 配置
    llm_config = cm.get_llm_config()
    print(f"\n当前 LLM 配置:")
    print(f"  API Key: {'*' * 20 if llm_config.get('api_key') else '(未设置)'}")
    print(f"  Base URL: {llm_config.get('base_url')}")
    print(f"  Model: {llm_config.get('model')}")

    # 测试 RSS 配置
    categories = cm.get_rss_categories()
    print(f"\n当前 RSS 分类: {categories}")

    for category in categories:
        sources = cm.get_rss_sources(category)
        print(f"\n{category}:")
        for source in sources:
            print(f"  - {source['name']}: {source['url'][:50]}... ({source['default_count']}条)")

    print("\n" + "=" * 50)
    print("配置管理器测试通过！")
    print("=" * 50)

if __name__ == "__main__":
    test_config_manager()
