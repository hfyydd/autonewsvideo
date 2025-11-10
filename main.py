import flet as ft
import asyncio
import threading
from typing import List
import config
from models.news import NewsItem, VideoProject
from services import (
    fetch_multiple_sources,
    generate_news_audio,
    create_adaptive_news_card,
    compose_news_collection_video,
)
from services.config_manager import ConfigManager

# 强制导入 certifi 以确保打包时包含
import certifi  # noqa: F401


def main(page: ft.Page):
    page.title = "新闻视频自动生成器"
    page.window.width = 1000
    page.window.height = 750
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 10
    page.scroll = ft.ScrollMode.AUTO  # 启用页面滚动

    # ===== 配置管理器 =====
    config_manager = ConfigManager()

    # ===== 数据状态 =====
    all_news: List[NewsItem] = []
    project = VideoProject(title="今日新闻")

    # ===== UI 组件 =====

    # 步骤1: RSS 源选择
    rss_category_dropdown = ft.Dropdown(
        label="RSS 源分类",
        options=[ft.dropdown.Option(key) for key in config_manager.get_rss_categories()],
        value=config_manager.get_rss_categories()[0] if config_manager.get_rss_categories() else None,
        width=180,
    )

    fetch_status = ft.Text("", size=12, color=ft.Colors.BLUE)

    # 步骤2: 新闻列表
    news_list_view = ft.Column(
        spacing=3,
        scroll=ft.ScrollMode.AUTO,
    )

    selected_count_text = ft.Text("已选: 0 条", size=12, weight=ft.FontWeight.BOLD)

    # 步骤2的空状态提示
    step2_empty_hint = ft.Container(
        content=ft.Text(
            "👆 请先点击上方「获取新闻」按钮",
            size=12,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
        ),
        alignment=ft.alignment.center,
        height=60,
    )

    # 步骤2的列表容器（初始隐藏）
    step2_list_container = ft.Container(visible=False)

    # 步骤3: 文案预览和编辑
    preview_container = ft.Column([], spacing=10, scroll=ft.ScrollMode.AUTO)
    preview_status = ft.Text("", size=12, color=ft.Colors.BLUE)

    # 步骤3的空状态提示
    step3_empty_hint = ft.Container(
        content=ft.Text(
            "👆 请先选择新闻并生成文案预览",
            size=12,
            color=ft.Colors.GREY_600,
            text_align=ft.TextAlign.CENTER,
        ),
        alignment=ft.alignment.center,
        height=60,
    )

    # 步骤3的预览容器（初始隐藏）
    step3_preview_container = ft.Container(visible=False)

    # 生成文案预览按钮（需要在函数外定义以便在函数内修改状态）
    generate_preview_button = ft.ElevatedButton(
        "生成文案预览",
        icon=ft.Icons.EDIT_NOTE,
        height=35,
        on_click=None,  # 稍后设置
    )

    # 步骤4: 设置
    style_dropdown = ft.Dropdown(
        label="卡片风格",
        options=[
            ft.dropdown.Option("blue", "蓝色"),
            ft.dropdown.Option("pink", "粉色"),
            ft.dropdown.Option("green", "绿色"),
            ft.dropdown.Option("purple", "紫色"),
        ],
        value="blue",
        width=140,
    )

    # 音色选择已移至设置页面,这里不再需要

    # 步骤5: 进度显示
    progress_bar = ft.ProgressBar(value=0)
    progress_text = ft.Text("", size=12)
    video_info_text = ft.Text("", size=11)

    # ===== 事件处理 =====

    def fetch_news_clicked(e):
        """获取新闻"""
        nonlocal all_news

        fetch_status.value = "正在获取新闻..."
        page.update()

        try:
            # 获取选中分类的 RSS 源
            category = rss_category_dropdown.value
            sources = config_manager.get_rss_sources(category)

            # 批量获取
            all_news = fetch_multiple_sources(sources)

            # 更新 UI
            news_list_view.controls.clear()

            for news in all_news:
                checkbox = ft.Checkbox(
                    label=f"{news.title[:45]}... ({news.source})",
                    value=False,
                    on_change=lambda e, n=news: toggle_news_selection(n, e.control.value),
                    label_style=ft.TextStyle(size=12)
                )
                news_list_view.controls.append(checkbox)

            fetch_status.value = f"✓ 已获取 {len(all_news)} 条新闻"
            fetch_status.color = ft.Colors.GREEN

            # 隐藏空状态提示，显示列表
            step2_empty_hint.visible = False
            step2_list_container.visible = True

        except Exception as ex:
            fetch_status.value = f"✗ 获取失败: {ex}"
            fetch_status.color = ft.Colors.RED

        page.update()

    def toggle_news_selection(news: NewsItem, selected: bool):
        """切换新闻选中状态"""
        news.selected = selected
        update_selected_count()

    def update_selected_count():
        """更新已选数量"""
        count = sum(1 for news in all_news if news.selected)
        selected_count_text.value = f"已选: {count} 条"
        page.update()

    def select_all_clicked(e):
        """全选"""
        for news in all_news:
            news.selected = True
        for control in news_list_view.controls:
            if isinstance(control, ft.Checkbox):
                control.value = True
        update_selected_count()

    def clear_selection_clicked(e):
        """清空选择"""
        for news in all_news:
            news.selected = False
        for control in news_list_view.controls:
            if isinstance(control, ft.Checkbox):
                control.value = False
        update_selected_count()

    def reset_all_clicked(e):
        """清空所有，重新开始"""
        nonlocal all_news

        # 清空所有数据
        all_news = []
        news_list_view.controls.clear()
        preview_container.controls.clear()

        # 重置状态文本
        fetch_status.value = ""
        selected_count_text.value = "已选: 0 条"
        preview_status.value = ""

        # 隐藏步骤2和步骤3的内容，显示空状态提示
        step2_empty_hint.visible = True
        step2_list_container.visible = False
        step3_empty_hint.visible = True
        step3_preview_container.visible = False

        # 重置进度
        progress_bar.value = 0
        progress_text.value = ""
        video_info_text.value = ""

        page.update()

    def generate_preview_clicked(e):
        """生成文案预览"""
        selected_news = [news for news in all_news if news.selected]

        if not selected_news:
            preview_status.value = "请先选择新闻！"
            preview_status.color = ft.Colors.RED
            page.update()
            return

        # 禁用按钮，显示加载状态
        generate_preview_button.disabled = True
        generate_preview_button.text = "正在生成..."
        preview_status.value = "正在生成文案..."
        preview_status.color = ft.Colors.BLUE
        preview_container.controls.clear()
        page.update()

        try:
            # 为每条新闻生成文案
            from services.ai_writer import generate_news_content
            from services.image_downloader import download_and_process_images

            for i, news in enumerate(selected_news):
                preview_status.value = f"正在生成文案... ({i+1}/{len(selected_news)})"
                page.update()

                # 生成AI文案
                content = generate_news_content(news)
                news.tts_script = content["tts_script"]
                news.card_title = content["card_title"]
                news.card_points = content["card_points"]

                # 下载新闻配图
                if news.image_urls:
                    preview_status.value = f"正在下载配图... ({i+1}/{len(selected_news)})"
                    page.update()
                    downloaded = download_and_process_images(news, i)
                    news.downloaded_images = downloaded
                    # 初始化选中状态（默认都不选中）
                    news.selected_images = [False] * len(downloaded)

                # 创建预览卡片
                preview_card = create_preview_card(news, i)
                preview_container.controls.append(preview_card)
                page.update()

            preview_status.value = f"✓ 已生成 {len(selected_news)} 条文案，请检查并编辑"
            preview_status.color = ft.Colors.GREEN

            # 隐藏空状态提示，显示预览
            step3_empty_hint.visible = False
            step3_preview_container.visible = True

        except Exception as ex:
            preview_status.value = f"✗ 生成失败: {ex}"
            preview_status.color = ft.Colors.RED
            import traceback
            traceback.print_exc()

        finally:
            # 恢复按钮状态
            generate_preview_button.disabled = False
            generate_preview_button.text = "生成文案预览"
            page.update()

    # 设置按钮事件
    generate_preview_button.on_click = generate_preview_clicked

    def create_preview_card(news: NewsItem, index: int):
        """创建文案预览卡片"""

        # TTS文案编辑框（用于语音）
        tts_field = ft.TextField(
            label=f"新闻 {index+1} - 播报文案（用于语音）",
            value=news.tts_script,
            multiline=True,
            min_lines=4,
            max_lines=8,
            on_change=lambda e, n=news: setattr(n, 'tts_script', e.control.value),
            hint_text="这段文字将用于语音合成",
            text_size=11,  # 减小字体以显示更多内容
        )

        # 卡片标题编辑框
        card_title_field = ft.TextField(
            label="卡片标题（图片显示）",
            value=news.card_title,
            multiline=False,
            on_change=lambda e, n=news: setattr(n, 'card_title', e.control.value),
            hint_text="8-12字"
        )

        # 要点编辑框列表
        point_fields = []
        for i, point in enumerate(news.card_points):
            # 兼容CardPoint对象和字符串
            from models.news import CardPoint
            if isinstance(point, CardPoint):
                point_value = f"{point.subtitle}: {point.content}"
            else:
                point_value = point

            point_field = ft.TextField(
                label=f"卡片要点 {i+1}（图片显示）",
                value=point_value,
                multiline=True,
                min_lines=1,
                max_lines=2,
                on_change=lambda e, n=news, idx=i: update_point(n, idx, e.control.value),
                hint_text="小标题: 详细内容"
            )
            point_fields.append(point_field)

        # 新闻配图选择（如果有配图）
        image_selection = []
        if news.downloaded_images:
            def toggle_image_selection(img_index: int, selected: bool):
                """切换图片选中状态"""
                if img_index < len(news.selected_images):
                    news.selected_images[img_index] = selected

            image_checkboxes = []
            for img_idx, img_path in enumerate(news.downloaded_images):
                checkbox = ft.Checkbox(
                    label=f"使用配图 {img_idx+1}",
                    value=news.selected_images[img_idx] if img_idx < len(news.selected_images) else False,
                    on_change=lambda e, idx=img_idx: toggle_image_selection(idx, e.control.value)
                )

                # 创建缩略图容器
                try:
                    img_container = ft.Container(
                        content=ft.Image(
                            src=img_path,
                            width=150,
                            height=100,
                            fit=ft.ImageFit.CONTAIN,
                        ),
                        border=ft.border.all(1, ft.Colors.GREY_400),
                        border_radius=4,
                    )

                    image_checkboxes.append(
                        ft.Row([checkbox, img_container], spacing=10)
                    )
                except:
                    image_checkboxes.append(checkbox)

            image_selection = [
                ft.Divider(height=1),
                ft.Text("📷 新闻配图（默认不使用）", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                ft.Column(image_checkboxes, spacing=8),
            ]

        return ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text(f"📰 新闻 {index+1}", size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    ft.Text(f"来源: {news.source}", size=11, color=ft.Colors.GREY_600),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),

                ft.Divider(height=1),

                # TTS文案
                ft.Text("🎤 TTS播报文案", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                tts_field,

                ft.Divider(height=1),

                # 卡片内容
                ft.Text("🖼️ 卡片显示内容", size=12, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
                card_title_field,
                ft.Text("要点:", size=11, weight=ft.FontWeight.BOLD),
                *point_fields,

                # 配图选择
                *image_selection,
            ], spacing=6),
            padding=10,
            border=ft.border.all(2, ft.Colors.BLUE_300),
            border_radius=8,
            bgcolor=ft.Colors.BLUE_50,
        )

    def update_point(news: NewsItem, idx: int, value: str):
        """更新新闻要点"""
        if idx < len(news.card_points):
            news.card_points[idx] = value

    def generate_video_clicked(e):
        """生成视频"""
        # 获取选中的新闻
        selected_news = [news for news in all_news if news.selected]

        if not selected_news:
            progress_text.value = "请先选择新闻！"
            progress_text.color = ft.Colors.RED
            page.update()
            return

        # 检查是否已生成文案
        if not all(news.tts_script and news.card_title and news.card_points for news in selected_news):
            progress_text.value = "请先生成文案预览并确认！"
            progress_text.color = ft.Colors.RED
            page.update()
            return

        # 在后台线程中运行
        def run_generation():
            # 创建新的事件循环用于异步任务
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(_generate_video_async(selected_news))
            finally:
                loop.close()

        # 启动后台线程
        thread = threading.Thread(target=run_generation, daemon=True)
        thread.start()

    async def _generate_video_async(selected_news: List[NewsItem]):
        """异步生成视频的实际逻辑"""
        progress_text.color = ft.Colors.BLUE
        total_steps = len(selected_news) * 3  # 语音 + 图片 + 视频合成
        current_step = 0

        def update_progress(current, total, message):
            """更新进度条和文本"""
            progress_bar.value = current / total
            progress_text.value = message
            page.update()

        try:
            # 获取设置
            style = style_dropdown.value

            # 从配置中获取语音设置 (Edge TTS 使用)
            tts_config = config_manager.get_tts_config()
            voice_name = tts_config.get("edge_voice", "中文女声")
            voice = config.TTS_VOICES.get(voice_name, config.TTS_DEFAULT_VOICE)

            # 步骤1: 生成语音
            for i, news in enumerate(selected_news):
                progress_text.value = f"[{i+1}/{len(selected_news)}] 正在生成语音..."
                page.update()

                audio_path, duration = await generate_news_audio(news, i, voice)
                news.audio_path = audio_path
                news.duration = duration

                current_step += 1
                progress_bar.value = current_step / total_steps
                page.update()

            # 步骤2: 生成图片
            for i, news in enumerate(selected_news):
                progress_text.value = f"[{i+1}/{len(selected_news)}] 正在生成图片..."
                page.update()

                image_path = create_adaptive_news_card(news, style, i)
                news.image_path = image_path

                current_step += 1
                progress_bar.value = current_step / total_steps
                page.update()

            # 步骤3: 合成视频（带进度回调）
            def video_progress_callback(current, total, message):
                """视频合成进度回调"""
                # 映射到总进度
                video_base = len(selected_news) * 2  # 前面已完成的步骤
                video_progress = current / total if total > 0 else 0
                overall_progress = (video_base + video_progress * len(selected_news)) / total_steps
                progress_bar.value = overall_progress
                progress_text.value = message
                page.update()

            video_path = compose_news_collection_video(selected_news, progress_callback=video_progress_callback)

            # 完成
            progress_bar.value = 1.0
            progress_text.value = "✓ 视频生成成功！"
            progress_text.color = ft.Colors.GREEN

            total_duration = sum(news.duration for news in selected_news)
            video_info_text.value = f"视频路径: {video_path}\n总时长: {total_duration:.1f} 秒"

        except Exception as ex:
            progress_text.value = f"✗ 生成失败: {ex}"
            progress_text.color = ft.Colors.RED
            import traceback
            traceback.print_exc()

        page.update()

    def open_output_folder(e):
        """打开输出文件夹"""
        import subprocess
        import platform
        import os

        # 打开父目录（AutoNewsVideo）而不是 output 子目录
        output_dir = os.path.dirname(config.OUTPUT_DIR)  # 获取 AutoNewsVideo 目录

        try:
            system = platform.system()
            if system == "Darwin":  # macOS
                subprocess.run(["open", output_dir])
            elif system == "Windows":
                subprocess.run(["explorer", output_dir])
            else:  # Linux
                subprocess.run(["xdg-open", output_dir])
        except Exception as ex:
            print(f"打开文件夹失败: {ex}")

    # ===== 配置对话框 =====

    def show_settings_dialog(e, show_api_key_warning=False):
        """显示设置对话框"""
        # LLM 配置
        llm_config = config_manager.get_llm_config()
        api_key_field = ft.TextField(
            label="API Key",
            value=llm_config.get("api_key", ""),
            password=True,
            can_reveal_password=True,
            width=400,
        )
        base_url_field = ft.TextField(
            label="Base URL",
            value=llm_config.get("base_url", ""),
            width=400,
        )
        model_field = ft.TextField(
            label="模型名称",
            value=llm_config.get("model", ""),
            width=400,
        )

        # TTS 配置
        tts_config = config_manager.get_tts_config()
        tts_engine_dropdown = ft.Dropdown(
            label="TTS 引擎",
            options=[
                ft.dropdown.Option("edge", "Edge TTS (免费)"),
                ft.dropdown.Option("minimax", "MiniMax TTS (需 API Key)"),
            ],
            value=tts_config.get("engine", "edge"),
            width=400,
        )

        # Edge TTS 音色选择
        edge_voice_dropdown = ft.Dropdown(
            label="Edge TTS 音色",
            options=[ft.dropdown.Option(key) for key in config.TTS_VOICES.keys()],
            value=tts_config.get("edge_voice", "中文女声"),
            width=400,
            visible=tts_config.get("engine", "edge") == "edge",
        )

        # MiniMax TTS 配置
        minimax_api_key_field = ft.TextField(
            label="MiniMax API Key",
            value=tts_config.get("minimax_api_key", ""),
            password=True,
            can_reveal_password=True,
            width=400,
            visible=tts_config.get("engine") == "minimax",
        )

        from services.minimax_tts import MinimaxTTSService
        voice_options = MinimaxTTSService.get_available_voices()

        minimax_voice_dropdown = ft.Dropdown(
            label="MiniMax 音色",
            options=[ft.dropdown.Option(voice_id, display_name) for display_name, voice_id in voice_options.items()],
            value=tts_config.get("minimax_voice_id", "male-qn-qingse"),
            width=400,
            visible=tts_config.get("engine") == "minimax",
        )

        def tts_engine_changed(e):
            """TTS 引擎切换时显示/隐藏相关字段"""
            is_minimax = e.control.value == "minimax"
            is_edge = e.control.value == "edge"

            # Edge TTS 字段
            edge_voice_dropdown.visible = is_edge

            # MiniMax TTS 字段
            minimax_api_key_field.visible = is_minimax
            minimax_voice_dropdown.visible = is_minimax

            page.update()

        tts_engine_dropdown.on_change = tts_engine_changed

        # RSS 配置
        rss_category_field = ft.TextField(label="分类名称", width=180)
        rss_name_field = ft.TextField(label="RSS 源名称", width=180)
        rss_url_field = ft.TextField(label="RSS URL", width=300)
        rss_count_field = ft.TextField(label="默认数量", value="5", width=100)

        rss_list_view = ft.Column([], spacing=5, scroll=ft.ScrollMode.AUTO, height=200)

        # 配置对话框（先定义，后面才能在 refresh_rss_list 中检查状态）
        settings_dialog = ft.AlertDialog(
            open=False,  # 初始为关闭状态
        )

        def refresh_rss_list():
            """刷新 RSS 列表显示"""
            rss_list_view.controls.clear()

            for category in config_manager.get_rss_categories():
                sources = config_manager.get_rss_sources(category)

                # 分类标题
                category_title = ft.Container(
                    content=ft.Row([
                        ft.Text(f"📁 {category}", size=13, weight=ft.FontWeight.BOLD),
                        ft.IconButton(
                            icon=ft.Icons.DELETE,
                            icon_size=16,
                            tooltip="删除分类",
                            on_click=lambda e, cat=category: delete_category(cat)
                        )
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=ft.Colors.BLUE_50,
                    padding=5,
                    border_radius=5,
                )
                rss_list_view.controls.append(category_title)

                # RSS 源列表
                for i, source in enumerate(sources):
                    source_row = ft.Container(
                        content=ft.Row([
                            ft.Text(f"  • {source['name']}", size=11, width=120),
                            ft.Text(source['url'][:40] + "...", size=10, width=250, color=ft.Colors.GREY_700),
                            ft.Text(f"({source['default_count']}条)", size=10, width=50),
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                icon_size=14,
                                tooltip="删除",
                                on_click=lambda e, cat=category, idx=i: delete_rss_source(cat, idx)
                            )
                        ], spacing=5),
                        padding=ft.padding.only(left=10, top=2, bottom=2),
                    )
                    rss_list_view.controls.append(source_row)

            # 只在对话框已经添加到页面时才更新
            if settings_dialog.open:
                page.update()

        def delete_category(category):
            """删除分类"""
            config_manager.remove_rss_category(category)
            refresh_rss_list()

        def delete_rss_source(category, index):
            """删除 RSS 源"""
            config_manager.remove_rss_source(category, index)
            refresh_rss_list()

        def add_rss_source_clicked(e):
            """添加 RSS 源"""
            category = rss_category_field.value.strip()
            name = rss_name_field.value.strip()
            url = rss_url_field.value.strip()

            if not category or not name or not url:
                return

            try:
                count = int(rss_count_field.value)
            except:
                count = 5

            # 如果分类不存在，先添加分类
            if category not in config_manager.get_rss_categories():
                config_manager.add_rss_category(category)

            # 添加 RSS 源
            config_manager.add_rss_source(category, name, url, count)

            # 清空输入框
            rss_category_field.value = ""
            rss_name_field.value = ""
            rss_url_field.value = ""
            rss_count_field.value = "5"

            refresh_rss_list()

        def save_settings_clicked(e):
            """保存设置"""
            # 保存 LLM 配置
            config_manager.set_llm_config(
                api_key_field.value,
                base_url_field.value,
                model_field.value
            )

            # 保存 TTS 配置
            config_manager.set_tts_config(
                engine=tts_engine_dropdown.value,
                edge_voice=edge_voice_dropdown.value,
                minimax_api_key=minimax_api_key_field.value,
                minimax_voice_id=minimax_voice_dropdown.value
            )

            # 保存到文件
            if config_manager.save_config():
                # 更新环境变量（供 AI writer 使用）
                import os
                os.environ["AI_API_KEY"] = api_key_field.value
                os.environ["AI_BASE_URL"] = base_url_field.value
                os.environ["AI_MODEL"] = model_field.value

                # 更新主界面的 RSS 下拉框
                rss_category_dropdown.options = [
                    ft.dropdown.Option(key) for key in config_manager.get_rss_categories()
                ]
                if config_manager.get_rss_categories():
                    rss_category_dropdown.value = config_manager.get_rss_categories()[0]

                page.update()

                settings_dialog.open = False
                page.update()

        # 更新对话框内容
        settings_dialog.title = ft.Text("设置", size=18, weight=ft.FontWeight.BOLD)

        # API Key 警告提示（如果需要）
        api_warning = []
        if show_api_key_warning:
            api_warning = [
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE, size=24),
                        ft.Text(
                            "⚠️ 请先配置 AI API Key 才能使用文案生成功能",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.ORANGE_700
                        ),
                    ], spacing=10),
                    bgcolor=ft.Colors.ORANGE_50,
                    padding=10,
                    border=ft.border.all(2, ft.Colors.ORANGE_300),
                    border_radius=8,
                ),
                ft.Divider(height=10),
            ]

        settings_dialog.content = ft.Container(
            content=ft.Column([
                # API Key 警告
                *api_warning,

                # LLM 配置区
                ft.Text("🤖 LLM 配置", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                ft.Divider(height=1),
                api_key_field,
                base_url_field,
                model_field,

                ft.Divider(height=20),

                # TTS 配置区
                ft.Text("🎙️ TTS 配置", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.PURPLE_700),
                ft.Divider(height=1),
                tts_engine_dropdown,
                edge_voice_dropdown,
                minimax_api_key_field,
                minimax_voice_dropdown,
                ft.Text("提示: Edge TTS 免费但音质一般,MiniMax TTS 音质更好但需要API Key", size=11, color=ft.Colors.GREY_700),

                ft.Divider(height=20),

                # RSS 配置区
                ft.Text("📡 RSS 源配置", size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                ft.Divider(height=1),

                ft.Text("添加新的 RSS 源:", size=12, weight=ft.FontWeight.BOLD),
                ft.Row([rss_category_field, rss_name_field], spacing=10),
                ft.Row([rss_url_field, rss_count_field], spacing=10),
                ft.ElevatedButton(
                    "添加",
                    on_click=add_rss_source_clicked,
                    icon=ft.Icons.ADD,
                    bgcolor=ft.Colors.GREEN,
                    color=ft.Colors.WHITE,
                ),

                ft.Divider(height=10),
                ft.Text("现有 RSS 源:", size=12, weight=ft.FontWeight.BOLD),
                rss_list_view,

            ], spacing=10, scroll=ft.ScrollMode.AUTO),
            width=600,
            height=600,
        )
        settings_dialog.actions = [
            ft.TextButton("取消", on_click=lambda e: close_dialog()),
            ft.ElevatedButton(
                "保存",
                on_click=save_settings_clicked,
                bgcolor=ft.Colors.BLUE,
                color=ft.Colors.WHITE,
            ),
        ]
        settings_dialog.actions_alignment = ft.MainAxisAlignment.END

        def close_dialog():
            settings_dialog.open = False
            page.update()

        # 刷新 RSS 列表并显示对话框
        refresh_rss_list()
        page.overlay.append(settings_dialog)
        settings_dialog.open = True
        page.update()

    # ===== 设置步骤容器的内容 =====

    # 步骤2列表容器内容
    step2_list_container.content = ft.Column([
        ft.Row([
            selected_count_text,
        ], alignment=ft.MainAxisAlignment.END),
        ft.Container(
            news_list_view,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=8,
            height=140,
        ),
        ft.Row([
            ft.TextButton("全选", on_click=select_all_clicked),
            ft.TextButton("清空", on_click=clear_selection_clicked),
            generate_preview_button,
        ], spacing=10),
    ], spacing=5)

    # 步骤3预览容器内容
    step3_preview_container.content = ft.Column([
        preview_status,
        ft.Container(
            preview_container,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=5,
            padding=8,
            height=250,
        ),
    ], spacing=5)

    # ===== 布局 =====

    page.add(
        ft.Column([
            # 标题栏（带设置和重置按钮）
            ft.Container(
                ft.Row([
                    ft.Text("新闻视频自动生成器", size=20, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        ft.ElevatedButton(
                            "清空重新开始",
                            icon=ft.Icons.REFRESH,
                            on_click=reset_all_clicked,
                            bgcolor=ft.Colors.ORANGE_300,
                            color=ft.Colors.WHITE,
                            height=35,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.SETTINGS,
                            tooltip="设置",
                            on_click=show_settings_dialog,
                            icon_size=20,
                        ),
                    ], spacing=10),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                padding=5,
            ),

            ft.Divider(height=1),

            # 步骤1: 获取新闻
            ft.Container(
                ft.Column([
                    ft.Text("步骤 1: 获取新闻", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        rss_category_dropdown,
                        ft.ElevatedButton("获取新闻", on_click=fetch_news_clicked, icon=ft.Icons.DOWNLOAD, height=40),
                    ], spacing=10),
                    fetch_status,
                ], spacing=5),
                padding=8,
                bgcolor=ft.Colors.BLUE_50,
                border_radius=8,
            ),

            # 步骤2: 选择新闻
            ft.Container(
                ft.Column([
                    ft.Text("步骤 2: 选择新闻", size=14, weight=ft.FontWeight.BOLD),
                    step2_empty_hint,
                    step2_list_container,
                ], spacing=5),
                padding=8,
                bgcolor=ft.Colors.GREEN_50,
                border_radius=8,
            ),

            # 步骤3: 文案预览和编辑
            ft.Container(
                ft.Column([
                    ft.Text("步骤 3: 文案预览和编辑", size=14, weight=ft.FontWeight.BOLD),
                    step3_empty_hint,
                    step3_preview_container,
                ], spacing=5),
                padding=8,
                bgcolor=ft.Colors.PURPLE_50,
                border_radius=8,
            ),

            # 步骤4: 视频设置
            ft.Container(
                ft.Column([
                    ft.Text("步骤 4: 视频设置", size=14, weight=ft.FontWeight.BOLD),
                    ft.Row([
                        style_dropdown,
                        ft.ElevatedButton(
                            "开始生成",
                            on_click=generate_video_clicked,
                            icon=ft.Icons.PLAY_ARROW,
                            bgcolor=ft.Colors.BLUE,
                            color=ft.Colors.WHITE,
                            height=40,
                        ),
                    ], spacing=10),
                ], spacing=5),
                padding=8,
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=8,
            ),

            # 步骤5: 进度
            ft.Container(
                ft.Column([
                    ft.Text("步骤 5: 生成进度", size=14, weight=ft.FontWeight.BOLD),
                    progress_bar,
                    progress_text,
                    video_info_text,
                    ft.ElevatedButton(
                        "打开输出文件夹",
                        icon=ft.Icons.FOLDER_OPEN,
                        on_click=open_output_folder,
                        height=35,
                    ),
                ], spacing=5),
                padding=8,
                bgcolor=ft.Colors.CYAN_50,
                border_radius=8,
            ),

        ], spacing=10, scroll=ft.ScrollMode.AUTO)
    )

    # ===== 首次运行检查 =====
    # 检查 API Key 是否配置
    if not config.is_api_key_configured():
        # 延迟显示对话框，确保页面已完全加载
        def check_api_key_on_start():
            import time
            time.sleep(0.5)  # 等待页面渲染完成
            show_settings_dialog(None, show_api_key_warning=True)

        threading.Thread(target=check_api_key_on_start, daemon=True).start()


if __name__ == "__main__":
    ft.app(target=main)
