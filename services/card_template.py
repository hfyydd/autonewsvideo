from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from models.news import NewsItem, CardPoint
import config


def create_vscode_style_card(
    news: NewsItem,
    style: str = "blue",
    index: int = 0
) -> str:
    """
    按照 VS Code 模板样式生成卡片

    核心逻辑：
    - 一张图片 = 一个新闻的完整展示
    - 包含：主标题(有阴影) + 多个要点卡片(网格布局，有阴影) + 底部信息
    - 每个卡片有独立title和横线
    - 布局灵活：2个=1x2, 3个=1x3, 4个=2x2
    """

    width = 1920
    height = 1080

    # 模板配色方案
    border_colors = [
        (0, 0, 0),           # 黑色
        (233, 78, 139),      # 粉色 #E94E8B
        (76, 175, 80),       # 绿色 #4CAF50
        (33, 150, 243),      # 蓝色 #2196F3
    ]

    icon_backgrounds = [
        (227, 242, 253),     # 蓝色背景 #E3F2FD
        (252, 228, 236),     # 粉色背景 #FCE4EC
        (232, 245, 233),     # 绿色背景 #E8F5E9
        (227, 242, 253),     # 蓝色背景
    ]

    icons = ["〈 〉", "🚩", "🔧", "📈"]

    # 创建浅粉色背景 #FDF0F0
    img = Image.new('RGB', (width, height), (253, 240, 240))
    draw = ImageDraw.Draw(img)

    # === 加载字体 ===
    def get_font(size: int):
        """加载中文字体"""
        font_paths = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue

        return ImageFont.load_default()

    # 字体
    main_title_font = get_font(80)          # 主标题
    box_title_font = get_font(36)           # 卡片标题
    box_text_font = get_font(26)            # 卡片正文
    footer_font = get_font(24)              # 底部文字

    # === 主标题（粉红色，顶部居中，带阴影）===
    main_title_color = (233, 78, 139)       # #E94E8B
    title_y = 70

    # 计算标题宽度以居中
    bbox = draw.textbbox((0, 0), news.card_title, font=main_title_font)
    title_width = bbox[2] - bbox[0]
    title_x = (width - title_width) // 2

    # 绘制标题阴影（粉红色半透明）
    shadow_offset = 3
    shadow_color = (main_title_color[0] // 2, main_title_color[1] // 2, main_title_color[2] // 2)
    draw.text(
        (title_x + shadow_offset, title_y + shadow_offset),
        news.card_title,
        font=main_title_font,
        fill=shadow_color
    )

    # 绘制主标题
    draw.text(
        (title_x, title_y),
        news.card_title,
        font=main_title_font,
        fill=main_title_color
    )

    # === 计算网格布局 ===
    num_points = min(len(news.card_points), 8)  # 最多8个

    # 根据要点数量决定网格（优化布局）
    if num_points == 1:
        cols, rows = 1, 1
    elif num_points == 2:
        cols, rows = 2, 1  # 1x2 横向
    elif num_points == 3:
        cols, rows = 3, 1  # 1x3 横向
    elif num_points == 4:
        cols, rows = 2, 2  # 2x2
    elif num_points == 5:
        cols, rows = 3, 2  # 2x3 (前3后2)
    elif num_points == 6:
        cols, rows = 3, 2  # 2x3
    elif num_points == 7:
        cols, rows = 4, 2  # 2x4 (前4后3)
    else:  # 8个
        cols, rows = 4, 2  # 2x4

    # 内容区域
    content_top = title_y + 150
    content_bottom = height - 100
    content_height = content_bottom - content_top
    content_left = 100
    content_right = width - 100
    content_width = content_right - content_left

    # 单个卡片尺寸
    gap = 30  # 卡片间距
    card_width = (content_width - gap * (cols - 1)) // cols
    card_height = (content_height - gap * (rows - 1)) // rows

    # === 绘制要点卡片 ===
    for i, point in enumerate(news.card_points[:num_points]):
        # 计算位置
        col = i % cols
        row = i // cols

        card_x = content_left + col * (card_width + gap)
        card_y = content_top + row * (card_height + gap)

        # 选择颜色和图标
        border_color = border_colors[i % len(border_colors)]
        icon_bg = icon_backgrounds[i % len(icon_backgrounds)]
        icon = icons[i % len(icons)]

        # 获取卡片标题和内容（兼容新旧格式）
        if isinstance(point, CardPoint):
            card_title_text = point.subtitle
            point_content = point.content
        else:
            # 旧格式：字符串
            card_title_text = point[:5]  # 前5个字作为标题
            point_content = point

        # === 绘制卡片阴影（与边框颜色一致的半透明版本）===
        shadow_offset = 4
        shadow_color = (border_color[0] // 3, border_color[1] // 3, border_color[2] // 3)
        shadow_rect = [
            card_x + shadow_offset,
            card_y + shadow_offset,
            card_x + card_width + shadow_offset,
            card_y + card_height + shadow_offset
        ]
        draw.rounded_rectangle(
            shadow_rect,
            radius=12,
            fill=shadow_color
        )

        # === 绘制白色卡片 + 彩色边框 ===
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_width, card_y + card_height],
            radius=12,
            fill=(255, 255, 255),
            outline=border_color,
            width=2
        )

        # === 卡片头部区域 ===
        header_y = card_y + 30

        # 左上角图标
        icon_x = card_x + 30
        icon_y = header_y
        icon_size = 32

        # 图标背景
        draw.rounded_rectangle(
            [icon_x, icon_y, icon_x + icon_size, icon_y + icon_size],
            radius=6,
            fill=icon_bg
        )

        # 图标文字
        draw.text(
            (icon_x + icon_size // 2, icon_y + icon_size // 2),
            icon,
            font=get_font(20),
            fill=border_color,
            anchor="mm"
        )

        # === 卡片标题（右侧，黑色，加粗）===
        title_x = icon_x + icon_size + 15
        title_y = header_y + 3

        draw.text(
            (title_x, title_y),
            card_title_text,
            font=box_title_font,
            fill=(0, 0, 0)
        )

        # === 标题下方的横线 ===
        line_y = header_y + 45
        line_x1 = card_x + 30
        line_x2 = card_x + card_width - 30

        draw.line(
            [line_x1, line_y, line_x2, line_y],
            fill=border_color,
            width=2
        )

        # === 正文内容（更详细）===
        text_y = line_y + 25
        text_x = card_x + 30
        max_text_width = card_width - 60

        # 智能换行：基于实际文字宽度而非字符数
        def wrap_text_by_width(text, font, max_width):
            """根据实际像素宽度换行"""
            lines = []
            current_line = ""

            for char in text:
                test_line = current_line + char
                bbox = draw.textbbox((0, 0), test_line, font=font)
                line_width = bbox[2] - bbox[0]

                if line_width <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char

            if current_line:
                lines.append(current_line)

            return lines

        wrapped_lines = wrap_text_by_width(point_content, box_text_font, max_text_width)

        # 显示所有换行后的文本（最多显示到卡片底部）
        for line in wrapped_lines:
            # 检查是否还有足够空间显示这一行
            if text_y + 36 > card_y + card_height - 30:
                break

            draw.text(
                (text_x, text_y),
                line,
                font=box_text_font,
                fill=(51, 51, 51)
            )
            text_y += 36

    # 保存图片
    output_path = os.path.join(config.IMAGE_DIR, f"news_card_{index:03d}.png")
    os.makedirs(config.IMAGE_DIR, exist_ok=True)
    img.save(output_path, quality=95)

    print(f"✅ 卡片已生成: {output_path} (包含 {num_points} 个要点, {cols}x{rows} 布局)")

    return output_path


# 兼容旧接口
def create_adaptive_news_card(news: NewsItem, style: str = "blue", index: int = 0) -> str:
    """使用VS Code风格"""
    return create_vscode_style_card(news, style, index)
