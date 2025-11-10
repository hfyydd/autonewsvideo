import json
import re
from typing import Dict, List
from openai import OpenAI
from models.news import NewsItem, CardPoint
import config


def clean_html_tags(text: str) -> str:
    """
    清理HTML标签和特殊符号

    Args:
        text: 原始文本

    Returns:
        清理后的纯文本
    """
    if not text:
        return ""

    # 移除HTML标签
    text = re.sub(r'<[^>]+>', '', text)

    # 移除常见的HTML实体
    text = text.replace('&nbsp;', ' ')
    text = text.replace('&lt;', '<')
    text = text.replace('&gt;', '>')
    text = text.replace('&amp;', '&')
    text = text.replace('&quot;', '"')
    text = text.replace('&#39;', "'")

    # 移除多余的空白
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()

    return text


def generate_news_content(news: NewsItem) -> Dict[str, any]:
    """
    使用 AI 为单条新闻生成内容（TTS文案 + 卡片内容）

    Args:
        news: 新闻对象

    Returns:
        {
            "tts_script": "完整的播报文案",
            "card_title": "卡片标题",
            "card_points": ["要点1", "要点2", "要点3"]
        }
    """

    # 检查 API Key
    if not config.AI_API_KEY:
        print("警告: 未配置 AI_API_KEY，使用模拟数据")
        return _generate_mock_content(news)

    try:
        client = OpenAI(
            api_key=config.AI_API_KEY,
            base_url=config.AI_BASE_URL
        )

        prompt = f"""你是专业的新闻编辑。请将以下新闻改写为适合短视频的格式。

原新闻：
标题：{news.title}
内容：{news.raw_content}
来源：{news.source}

请生成两部分内容：

1. **播报文案**（用于语音合成）：
   - 150-200字的完整新闻播报稿
   - 语言口语化、流畅自然
   - 包含核心信息和关键细节
   - 适合直接朗读
   - **纯文本，不包含任何HTML标签、特殊符号、markdown格式**

2. **卡片内容**（用于视觉展示）：
   - 主标题：简洁有力，8-12字
   - 要点列表：根据新闻内容丰富程度生成3-8个关键信息点
     * 每个要点包含：
       - subtitle: 4-6字的精炼小标题（提炼该要点的核心关键词）
       - content: 25-35字的详细内容
     * 新闻内容丰富：生成6-8个要点
     * 新闻内容一般：生成4-5个要点
     * 新闻内容简单：生成3个要点即可
     * **宁可减少要点数量，也要保证每个要点内容详实（25-35字）**
   - **纯文本，不包含任何特殊符号**

请严格按照以下JSON格式返回：
{{
    "tts_script": "完整的播报文案...",
    "card_title": "主标题",
    "card_points": [
        {{"subtitle": "功能开源", "content": "微软VS Code团队正式宣布AI编辑器内联补全功能已作为Copilot Chat扩展的一部分开源"}},
        {{"subtitle": "里程碑", "content": "这是微软开源AI编辑器计划的第二个重要里程碑，继6月开源GitHub Copilot Chat扩展之后"}},
        ...
    ]
}}"""

        response = client.chat.completions.create(
            model=config.AI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

        # 验证返回结果
        if "tts_script" not in result or "card_title" not in result or "card_points" not in result:
            raise ValueError("AI 返回格式错误")

        if not isinstance(result["card_points"], list) or len(result["card_points"]) < 3 or len(result["card_points"]) > 8:
            raise ValueError(f"要点数量应为3-8个，当前为{len(result['card_points'])}个")

        # 验证每个要点的格式
        for point in result["card_points"]:
            if not isinstance(point, dict) or "subtitle" not in point or "content" not in point:
                raise ValueError("要点格式错误，应包含subtitle和content字段")

        # 清理HTML标签和特殊符号，并转换为CardPoint对象
        result["tts_script"] = clean_html_tags(result["tts_script"])
        result["card_title"] = clean_html_tags(result["card_title"])
        result["card_points"] = [
            CardPoint(
                subtitle=clean_html_tags(p["subtitle"]),
                content=clean_html_tags(p["content"])
            )
            for p in result["card_points"]
        ]

        return result

    except Exception as e:
        print(f"AI 生成失败: {e}，使用备用方案")
        return _generate_mock_content(news)


def _generate_mock_content(news: NewsItem) -> Dict[str, any]:
    """
    备用方案：不使用 AI 的简单内容生成

    Args:
        news: 新闻对象

    Returns:
        TTS文案和卡片内容
    """
    # 清理原始内容的HTML标签
    clean_content = clean_html_tags(news.raw_content)
    clean_title = clean_html_tags(news.title)

    # 生成播报文案
    sentences = clean_content.split("。")[:3]
    tts_script = f"{clean_title}。" + "。".join(s.strip() for s in sentences if s.strip()) + "。"

    # 限制播报文案长度
    if len(tts_script) > 200:
        tts_script = tts_script[:200] + "..."

    # 简化标题
    card_title = clean_title[:12] + ("..." if len(clean_title) > 12 else "")

    # 生成要点（25-35字，内容丰满，带小标题）
    card_points = []
    for idx, sentence in enumerate(sentences[:8]):  # 最多8个要点
        sentence = sentence.strip()
        if len(sentence) > 15:
            # 每个要点保持在25-35字之间
            if len(sentence) <= 35:
                content = sentence
            else:
                # 如果太长，截取前35字
                content = sentence[:35] + "..."

            # 生成简单的小标题（取前4-5个字）
            subtitle = content[:min(5, len(content))]

            card_points.append(CardPoint(subtitle=subtitle, content=content))

    # 至少保留3个要点，如果不够就扩充
    while len(card_points) < 3:
        if len(card_points) == 0:
            card_points.append(CardPoint(
                subtitle="新闻来源",
                content=f"来源：{news.source}，发布时间：{news.published[:10]}"
            ))
        elif len(card_points) == 1:
            card_points.append(CardPoint(
                subtitle="报道详情",
                content=f"这是一条来自{news.source}的新闻报道"
            ))
        else:
            # 从标题扩充
            card_points.append(CardPoint(
                subtitle="更多详情",
                content=f"更多详情：{card_title}"
            ))

    return {
        "tts_script": tts_script,
        "card_title": card_title,
        "card_points": card_points[:8]  # 最多8个
    }


def batch_generate_news_content(news_list: List[NewsItem]) -> List[NewsItem]:
    """
    批量为多条新闻生成内容

    Args:
        news_list: 新闻列表

    Returns:
        更新后的新闻列表
    """
    for i, news in enumerate(news_list):
        print(f"正在生成第 {i+1}/{len(news_list)} 条新闻内容...")

        content = generate_news_content(news)
        news.tts_script = content["tts_script"]
        news.card_title = content["card_title"]
        news.card_points = content["card_points"]

    return news_list
