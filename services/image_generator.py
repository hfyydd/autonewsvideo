from PIL import Image, ImageDraw, ImageFont
import textwrap
import os
from typing import Tuple
from models.news import NewsItem
import config


def calculate_card_dimensions(
    title: str,
    points: list[str],
    canvas_width: int = None,
    canvas_height: int = None
) -> Tuple[int, int, int, int]:
    """
    根据内容计算卡片尺寸和位置

    Args:
        title: 标题文字
        points: 要点列表
        canvas_width: 画布宽度
        canvas_height: 画布高度

    Returns:
        (card_x, card_y, card_width, card_height)
    """

    if canvas_width is None:
        canvas_width = config.LAYOUT_CONFIG["canvas_width"]
    if canvas_height is None:
        canvas_height = config.LAYOUT_CONFIG["canvas_height"]

    # 布局参数
    padding = config.LAYOUT_CONFIG["padding"]
    title_line_height = config.LAYOUT_CONFIG["title_line_height"]
    line_height = config.LAYOUT_CONFIG["line_height"]
    point_spacing = config.LAYOUT_CONFIG["point_spacing"]
    separator_height = 40
    meta_height = 80

    # 计算标题行数
    title_chars_per_line = config.LAYOUT_CONFIG["title_chars_per_line"]
    title_lines = len(textwrap.wrap(title, width=title_chars_per_line))

    # 计算要点行数
    point_chars_per_line = config.LAYOUT_CONFIG["point_chars_per_line"]
    total_point_lines = 0
    for point in points:
        point_lines = len(textwrap.wrap(point, width=point_chars_per_line))
        total_point_lines += point_lines

    # 计算卡片高度
    card_height = (
        padding * 2 +
        title_lines * title_line_height +
        separator_height +
        len(points) * point_spacing +
        total_point_lines * line_height +
        meta_height
    )

    # 限制最小/最大高度
    min_height = config.LAYOUT_CONFIG["min_card_height"]
    max_height = config.LAYOUT_CONFIG["max_card_height"]
    card_height = max(min_height, min(card_height, max_height))

    # 卡片宽度
    card_width = int(canvas_width * config.LAYOUT_CONFIG["card_width_ratio"])

    # 居中
    card_x = (canvas_width - card_width) // 2
    card_y = (canvas_height - card_height) // 2

    return card_x, card_y, card_width, card_height


def create_adaptive_news_card(
    news: NewsItem,
    style: str = "blue",
    index: int = 0
) -> str:
    """
    生成自适应大小的新闻卡片图片

    Args:
        news: 新闻对象（需包含 card_title 和 card_points）
        style: 卡片风格（blue/pink/green/purple）
        index: 新闻索引

    Returns:
        图片路径
    """

    width = config.LAYOUT_CONFIG["canvas_width"]
    height = config.LAYOUT_CONFIG["canvas_height"]

    # 获取配色
    colors = config.CARD_STYLES.get(style, config.CARD_STYLES["blue"])

    # 创建画布
    img = Image.new('RGB', (width, height), colors["bg"])
    draw = ImageDraw.Draw(img)

    # 加载字体（优先使用配置的字体，失败则使用系统字体）
    def load_font(font_path: str, size: int, bold: bool = False):
        """加载字体，支持多种回退方案"""
        # 尝试1: 使用配置的字体
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass

        # 尝试2: macOS 系统字体
        mac_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]
        for mac_font in mac_fonts:
            if os.path.exists(mac_font):
                try:
                    return ImageFont.truetype(mac_font, size)
                except Exception:
                    pass

        # 尝试3: Linux 系统字体
        linux_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
        for linux_font in linux_fonts:
            if os.path.exists(linux_font):
                try:
                    return ImageFont.truetype(linux_font, size)
                except Exception:
                    pass

        # 尝试4: Windows 系统字体
        windows_fonts = [
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
        ]
        for win_font in windows_fonts:
            if os.path.exists(win_font):
                try:
                    return ImageFont.truetype(win_font, size)
                except Exception:
                    pass

        # 最后回退: 使用 PIL 默认字体（不支持中文，会显示为方框）
        print(f"警告: 未找到支持中文的字体，文字可能显示异常")
        return ImageFont.load_default()

    title_font = load_font(
        config.DEFAULT_FONT_BOLD,
        config.LAYOUT_CONFIG["title_font_size"],
        bold=True
    )
    point_font = load_font(
        config.DEFAULT_FONT_REGULAR,
        config.LAYOUT_CONFIG["point_font_size"]
    )
    meta_font = load_font(
        config.DEFAULT_FONT_REGULAR,
        config.LAYOUT_CONFIG["meta_font_size"]
    )
    bullet_font = load_font(
        config.DEFAULT_FONT_BOLD,
        config.LAYOUT_CONFIG["bullet_font_size"],
        bold=True
    )

    # 计算卡片尺寸
    card_x, card_y, card_w, card_h = calculate_card_dimensions(
        news.card_title,
        news.card_points,
        width,
        height
    )

    # 绘制阴影
    shadow_offset = 10
    shadow_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)
    shadow_draw.rounded_rectangle(
        [card_x + shadow_offset, card_y + shadow_offset,
         card_x + card_w + shadow_offset, card_y + card_h + shadow_offset],
        radius=25,
        fill=(0, 0, 0, 30)
    )
    img.paste(shadow_img, (0, 0), shadow_img)

    # 绘制卡片主体（更粗的彩色边框）
    draw.rounded_rectangle(
        [card_x, card_y, card_x + card_w, card_y + card_h],
        radius=20,
        fill=colors["card_bg"],
        outline=colors["border"],
        width=6  # 更粗的边框
    )

    # 绘制左上角图标（如果有）
    if "icon" in colors:
        icon_text = colors["icon"]
        icon_size = 40
        try:
            icon_font = load_font(config.DEFAULT_FONT_BOLD, icon_size, bold=True)
            # 绘制图标背景
            icon_bg_size = 60
            draw.rounded_rectangle(
                [card_x + 25, card_y + 25,
                 card_x + 25 + icon_bg_size, card_y + 25 + icon_bg_size],
                radius=12,
                fill=colors["border"]
            )
            # 绘制图标
            draw.text(
                (card_x + 55, card_y + 55),
                icon_text,
                font=icon_font,
                fill=(255, 255, 255),
                anchor="mm"
            )
        except:
            pass

    # 当前绘制位置（给图标留出空间）
    current_y = card_y + 100
    padding_x = 80

    # === 1. 绘制标题 ===
    title_lines = textwrap.wrap(
        news.card_title,
        width=config.LAYOUT_CONFIG["title_chars_per_line"]
    )
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = card_x + (card_w - text_width) // 2  # 居中
        draw.text((x, current_y), line, font=title_font, fill=colors["title_color"])
        current_y += config.LAYOUT_CONFIG["title_line_height"]

    # === 2. 分隔线 ===
    current_y += 30
    line_margin = 150
    draw.line(
        [card_x + line_margin, current_y,
         card_x + card_w - line_margin, current_y],
        fill=colors["accent"],
        width=4
    )
    current_y += 50

    # === 3. 绘制要点 ===
    for point in news.card_points:
        # Bullet 图标
        bullet_x = card_x + padding_x
        draw.text(
            (bullet_x, current_y),
            "●",
            font=bullet_font,
            fill=colors["accent"]
        )

        # 要点文字（自动换行）
        point_lines = textwrap.wrap(
            point,
            width=config.LAYOUT_CONFIG["point_chars_per_line"]
        )
        text_x = bullet_x + 70

        for p_line in point_lines:
            draw.text(
                (text_x, current_y),
                p_line,
                font=point_font,
                fill=colors["text_color"]
            )
            current_y += config.LAYOUT_CONFIG["line_height"]

        # 要点间距
        current_y += config.LAYOUT_CONFIG["point_spacing"]

    # === 4. 底部元信息 ===
    bottom_y = card_y + card_h - 70

    # 左侧：来源
    draw.text(
        (card_x + padding_x, bottom_y),
        f"来源: {news.source}",
        font=meta_font,
        fill=colors["meta_color"]
    )

    # 右侧：日期
    date_text = news.published.split('T')[0] if 'T' in news.published else news.published[:10]
    date_bbox = draw.textbbox((0, 0), date_text, font=meta_font)
    date_width = date_bbox[2] - date_bbox[0]
    draw.text(
        (card_x + card_w - padding_x - date_width, bottom_y),
        date_text,
        font=meta_font,
        fill=colors["meta_color"]
    )

    # 保存图片
    output_path = os.path.join(config.IMAGE_DIR, f"news_card_{index:03d}.png")
    img.save(output_path, quality=95)

    print(f"  卡片尺寸: {card_w} × {card_h}")

    return output_path


def create_opening_slide(news_list: list[NewsItem], style: str = "blue") -> str:
    """
    生成片头图片（多卡片网格布局，类似你的示例图）

    Args:
        news_list: 新闻列表
        style: 卡片风格

    Returns:
        片头图片路径
    """
    width = config.LAYOUT_CONFIG["canvas_width"]
    height = config.LAYOUT_CONFIG["canvas_height"]

    # 获取配色
    colors = config.CARD_STYLES.get(style, config.CARD_STYLES["blue"])

    # 创建画布 - 使用浅色背景
    img = Image.new('RGB', (width, height), (245, 245, 250))
    draw = ImageDraw.Draw(img)

    # 加载字体
    def load_font(font_path: str, size: int, bold: bool = False):
        """加载字体，支持多种回退方案"""
        # 尝试1: 使用配置的字体
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass

        # 尝试2: macOS 系统字体
        mac_fonts = [
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
        ]
        for mac_font in mac_fonts:
            if os.path.exists(mac_font):
                try:
                    return ImageFont.truetype(mac_font, size)
                except Exception:
                    pass

        # 尝试3: Linux 系统字体
        linux_fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        ]
        for linux_font in linux_fonts:
            if os.path.exists(linux_font):
                try:
                    return ImageFont.truetype(linux_font, size)
                except Exception:
                    pass

        # 尝试4: Windows 系统字体
        windows_fonts = [
            "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
            "C:/Windows/Fonts/simhei.ttf",  # 黑体
        ]
        for win_font in windows_fonts:
            if os.path.exists(win_font):
                try:
                    return ImageFont.truetype(win_font, size)
                except Exception:
                    pass

        # 最后回退: 使用 PIL 默认字体
        print(f"警告: 未找到支持中文的字体，文字可能显示异常")
        return ImageFont.load_default()

    # 字体
    title_font = load_font(config.DEFAULT_FONT_BOLD, 80, bold=True)
    card_title_font = load_font(config.DEFAULT_FONT_REGULAR, 28)
    card_time_font = load_font(config.DEFAULT_FONT_REGULAR, 26)

    # === 1. 绘制顶部标题 "今日速览" ===
    main_title = "今日速览"
    bbox = draw.textbbox((0, 0), main_title, font=title_font)
    text_width = bbox[2] - bbox[0]
    title_x = (width - text_width) // 2
    title_y = 40

    # 给标题添加描边效果
    from datetime import datetime
    title_color = (255, 105, 180)  # 粉红色标题
    draw.text((title_x, title_y), main_title, font=title_font, fill=title_color)

    # === 2. 计算网格布局 ===
    # 3列布局
    columns = 3
    top_margin = 150  # 标题下方留白
    card_spacing_x = 25  # 卡片之间的横向间距
    card_spacing_y = 20  # 卡片之间的纵向间距
    side_margin = 50  # 左右边距

    # 计算每个卡片的宽度
    total_spacing_x = card_spacing_x * (columns - 1) + side_margin * 2
    card_width = (width - total_spacing_x) // columns

    # 卡片高度固定
    card_height = 90

    # 配色方案 - 多种颜色循环使用
    card_colors = [
        (64, 169, 255),   # 蓝色
        (255, 105, 180),  # 粉色
        (120, 220, 120),  # 绿色
        (147, 112, 219),  # 紫色
        (255, 165, 0),    # 橙色
        (100, 200, 200),  # 青色
    ]

    # === 3. 绘制新闻卡片网格 ===
    for i, news in enumerate(news_list):
        # 计算当前卡片的行列位置
        row = i // columns
        col = i % columns

        # 计算卡片位置
        card_x = side_margin + col * (card_width + card_spacing_x)
        card_y = top_margin + row * (card_height + card_spacing_y)

        # 选择卡片颜色
        card_color = card_colors[i % len(card_colors)]

        # 绘制卡片阴影
        shadow_offset = 4
        shadow_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_draw.rounded_rectangle(
            [card_x + shadow_offset, card_y + shadow_offset,
             card_x + card_width + shadow_offset, card_y + card_height + shadow_offset],
            radius=12,
            fill=(0, 0, 0, 20)
        )
        img.paste(shadow_img, (0, 0), shadow_img)

        # 绘制卡片主体
        draw.rounded_rectangle(
            [card_x, card_y, card_x + card_width, card_y + card_height],
            radius=12,
            fill=(255, 255, 255),
            outline=card_color,
            width=4
        )

        # 绘制左侧彩色竖条
        bar_width = 8
        draw.rounded_rectangle(
            [card_x + 5, card_y + 15, card_x + 5 + bar_width, card_y + card_height - 15],
            radius=4,
            fill=card_color
        )

        # 获取新闻标题
        title_text = news.card_title if hasattr(news, 'card_title') and news.card_title else news.title

        # 标题需要自动换行（最多显示2行）
        max_chars_per_line = 22  # 每行最多字符数
        if len(title_text) > max_chars_per_line * 2:
            title_text = title_text[:max_chars_per_line * 2 - 3] + "..."

        # 绘制标题文字
        text_x = card_x + 25
        text_y = card_y + 18

        # 简单的文字换行
        if len(title_text) <= max_chars_per_line:
            # 单行显示
            draw.text((text_x, text_y), title_text, font=card_title_font, fill=(30, 30, 30))
        else:
            # 两行显示
            line1 = title_text[:max_chars_per_line]
            line2 = title_text[max_chars_per_line:]
            draw.text((text_x, text_y), line1, font=card_title_font, fill=(30, 30, 30))
            draw.text((text_x, text_y + 32), line2, font=card_title_font, fill=(30, 30, 30))

        # 绘制右上角时间标签（格式：00:10）
        # 使用索引生成假时间，每条新闻间隔约30秒
        minutes = i // 2
        seconds = (i % 2) * 30 + 10
        time_text = f"{minutes:02d}:{seconds:02d}"

        # 计算时间文字宽度并右对齐
        time_bbox = draw.textbbox((0, 0), time_text, font=card_time_font)
        time_width = time_bbox[2] - time_bbox[0]
        time_x = card_x + card_width - time_width - 15
        time_y = card_y + 15

        draw.text((time_x, time_y), time_text, font=card_time_font, fill=(140, 140, 140))

    # 保存图片
    output_path = os.path.join(config.IMAGE_DIR, "opening_slide.png")
    img.save(output_path, quality=95)

    print(f"  片头图片生成完成: {output_path}")
    return output_path


def batch_generate_images(news_list: list[NewsItem], style: str = "blue") -> list[NewsItem]:
    """
    批量生成新闻卡片图片

    Args:
        news_list: 新闻列表
        style: 卡片风格

    Returns:
        更新后的新闻列表
    """
    for i, news in enumerate(news_list):
        print(f"正在生成第 {i+1}/{len(news_list)} 条新闻图片...")

        image_path = create_adaptive_news_card(news, style, i)
        news.image_path = image_path

    return news_list
