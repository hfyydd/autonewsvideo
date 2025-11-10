#!/usr/bin/env python3
"""测试不同数量要点的卡片布局"""

from models.news import NewsItem, CardPoint
from services.card_template import create_vscode_style_card
import os

# 确保输出目录存在
os.makedirs("output/images", exist_ok=True)

# 基础要点（带小标题和内容）
base_points = [
    CardPoint(
        subtitle="功能开源",
        content="微软VS Code团队正式宣布AI编辑器内联补全功能已作为Copilot Chat扩展的一部分开源"
    ),
    CardPoint(
        subtitle="里程碑",
        content="这是微软开源AI编辑器计划的第二个重要里程碑，继6月开源GitHub Copilot Chat扩展之后"
    ),
    CardPoint(
        subtitle="重构计划",
        content="下一阶段计划是将Copilot Chat扩展中的AI功能和组件重构到VS Code核心中"
    ),
    CardPoint(
        subtitle="持续改进",
        content="团队承诺将继续积极改进内联补全体验，开发者可以关注官方最新的迭代计划和路线图"
    ),
    CardPoint(
        subtitle="创新可能",
        content="开源内联补全功能将为开发者社区带来更多的创新可能性和个性化定制选项"
    ),
    CardPoint(
        subtitle="投资承诺",
        content="微软表示将持续投资AI辅助编程工具领域，致力于提升开发者生产力和代码质量"
    ),
    CardPoint(
        subtitle="自定义扩展",
        content="社区开发者现在可以基于开源代码构建自己专属的AI编程助手和智能扩展"
    ),
    CardPoint(
        subtitle="战略布局",
        content="这一举措标志着微软在开源AI工具领域的重要战略布局和长期投入承诺"
    ),
]

print("🎨 测试不同数量要点的卡片布局...")
print("=" * 60)

# 测试 3-8 个要点
for num in range(3, 9):
    print(f"\n📊 测试 {num} 个要点...")

    # 创建测试新闻
    test_news = NewsItem(
        title="VS Code 内联补全功能开源",
        source="IT之家",
        url="https://example.com",
        published="2024-11-08T10:00:00",
        raw_content="测试内容",
        card_title="VS Code 内联补全开源",
        card_points=base_points[:num]  # 取前 num 个要点
    )

    # 生成卡片
    path = create_vscode_style_card(test_news, "blue", num - 3)
    print(f"✅ 已保存: {path}")

print("\n" + "=" * 60)
print("✅ 测试完成！")
print()
print("生成的卡片：")
print("  - news_card_000.png (3个要点，3x1)")
print("  - news_card_001.png (4个要点，2x2)")
print("  - news_card_002.png (5个要点，3x2)")
print("  - news_card_003.png (6个要点，3x2)")
print("  - news_card_004.png (7个要点，4x2)")
print("  - news_card_005.png (8个要点，4x2)")
print()
print("请检查 output/images/ 目录查看生成的卡片")
