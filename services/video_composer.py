from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip
import os
from typing import List, Callable, Optional
from models.news import NewsItem
import config
import threading
import time
from services.sound_effects import ensure_sound_effects


def compose_news_collection_video(
    news_list: List[NewsItem],
    output_path: str = None,
    progress_callback: Optional[Callable[[int, int, str], None]] = None
) -> str:
    """
    合成新闻合集视频

    Args:
        news_list: 新闻列表（需包含 image_path, audio_path, duration）
        output_path: 输出视频路径（可选）
        progress_callback: 进度回调函数 callback(current, total, message)

    Returns:
        输出视频路径
    """

    if output_path is None:
        output_path = os.path.join(config.VIDEO_DIR, "news_collection.mp4")

    # 确保输出目录存在
    os.makedirs(config.VIDEO_DIR, exist_ok=True)

    # 检查新闻数据
    if not news_list:
        raise ValueError("新闻列表为空")

    for news in news_list:
        if not news.image_path or not os.path.exists(news.image_path):
            raise ValueError(f"图片不存在: {news.image_path}")
        if not news.audio_path or not os.path.exists(news.audio_path):
            raise ValueError(f"音频不存在: {news.audio_path}")
        if news.duration <= 0:
            raise ValueError(f"无效的时长: {news.duration}")

    print(f"\n开始合成视频...")
    print(f"共 {len(news_list)} 条新闻")

    # 确保音效文件存在
    sound_effects = ensure_sound_effects()
    transition_sound_path = sound_effects["keyboard_click"]

    clips = []

    for i, news in enumerate(news_list):
        print(f"处理第 {i+1}/{len(news_list)} 条新闻...")

        if progress_callback:
            progress_callback(i, len(news_list) * 2, f"准备视频片段 {i+1}/{len(news_list)}")

        try:
            # 加载音频
            audio_clip = AudioFileClip(news.audio_path)

            # 1. 先添加新闻配图（如果用户选中了）
            if news.downloaded_images and news.selected_images:
                for img_idx, (img_path, is_selected) in enumerate(zip(news.downloaded_images, news.selected_images)):
                    if is_selected and os.path.exists(img_path):
                        # 每张配图显示2秒
                        photo_clip = ImageClip(img_path, duration=2.0)

                        # 添加过渡音效（除了第一个片段）
                        if len(clips) > 0:
                            try:
                                transition_audio = AudioFileClip(transition_sound_path)
                                # 配图没有语音，只有过渡音效
                                photo_clip = photo_clip.with_audio(transition_audio)
                                print(f"  ✓ 已添加配图 {img_idx+1}（2秒）")
                            except Exception as e:
                                print(f"  ⚠️ 过渡音效添加失败: {e}")
                        else:
                            # 第一张配图也添加过渡音效
                            try:
                                transition_audio = AudioFileClip(transition_sound_path)
                                photo_clip = photo_clip.with_audio(transition_audio)
                            except:
                                pass

                        clips.append(photo_clip)

            # 2. 创建卡片图片剪辑（使用完整音频时长）
            card_clip = ImageClip(news.image_path, duration=news.duration)

            # 添加过渡音效（如果前面有配图或其他片段）
            if len(clips) > 0:
                try:
                    transition_audio = AudioFileClip(transition_sound_path)
                    # 将过渡音效和原始音频合并
                    combined_audio = CompositeAudioClip([
                        audio_clip,
                        transition_audio.with_start(0)
                    ])
                    card_clip = card_clip.with_audio(combined_audio)
                    print(f"  ✓ 已添加卡片（{news.duration:.1f}秒）+ 过渡音效")
                except Exception as e:
                    print(f"  ⚠️ 过渡音效添加失败: {e}，使用原始音频")
                    card_clip = card_clip.with_audio(audio_clip)
            else:
                # 第一个片段只使用原始音频
                card_clip = card_clip.with_audio(audio_clip)
                print(f"  ✓ 已添加卡片（{news.duration:.1f}秒）")

            clips.append(card_clip)

        except Exception as e:
            print(f"处理新闻 {i+1} 失败: {e}")
            raise

    # 拼接所有片段
    print("正在拼接视频片段...")
    if progress_callback:
        progress_callback(len(news_list), len(news_list) * 2, "正在拼接视频片段...")

    final_clip = concatenate_videoclips(clips, method="compose")

    # 导出视频
    print(f"正在导出视频到: {output_path}")

    # 导出前更新进度
    if progress_callback:
        progress_callback(len(news_list) + 1, len(news_list) * 2, "正在导出视频... (这可能需要几分钟)")

    # 创建一个标志来控制进度更新线程
    export_complete = threading.Event()

    def simulate_export_progress():
        """模拟导出进度（因为 MoviePy 不提供实时进度）"""
        if not progress_callback:
            return

        # 预估导出时间（基于视频总时长）
        total_duration = sum(news.duration for news in news_list)
        estimated_time = total_duration * 2  # 粗略估计导出时间是视频时长的2倍

        start_step = len(news_list) + 1
        end_step = len(news_list) * 2
        steps = end_step - start_step

        elapsed = 0
        update_interval = 1  # 每秒更新一次

        while not export_complete.is_set() and elapsed < estimated_time * 1.5:
            # 计算当前进度（使用对数曲线，前期快后期慢）
            progress_ratio = min(0.95, elapsed / estimated_time)  # 最多到95%
            current_step = start_step + int(progress_ratio * steps)

            percent = int(progress_ratio * 100)
            progress_callback(current_step, len(news_list) * 2, f"正在导出视频... {percent}%")

            if export_complete.wait(update_interval):
                break
            elapsed += update_interval

    # 启动进度模拟线程
    if progress_callback:
        progress_thread = threading.Thread(target=simulate_export_progress, daemon=True)
        progress_thread.start()

    # 使用 verbose=False 禁用控制台输出
    try:
        final_clip.write_videofile(
            output_path,
            fps=config.VIDEO_FPS,
            codec=config.VIDEO_CODEC,
            audio_codec=config.VIDEO_AUDIO_CODEC,
            bitrate=config.VIDEO_BITRATE,
            preset='medium',  # 编码速度（ultrafast/fast/medium/slow）
            threads=4,
            verbose=False,  # 禁用默认进度条
            logger=None,  # 禁用日志
        )
    except TypeError:
        # 如果 MoviePy 版本不支持 verbose 参数，使用简化版本
        final_clip.write_videofile(
            output_path,
            fps=config.VIDEO_FPS,
            codec=config.VIDEO_CODEC,
            audio_codec=config.VIDEO_AUDIO_CODEC,
            bitrate=config.VIDEO_BITRATE,
            preset='medium',
            threads=4,
            logger=None,
        )
    finally:
        # 停止进度模拟线程
        export_complete.set()

    # 完成后更新进度到 100%
    if progress_callback:
        progress_callback(len(news_list) * 2, len(news_list) * 2, "视频导出完成！")

    # 清理资源
    for clip in clips:
        clip.close()
    final_clip.close()

    print(f"\n✓ 视频生成成功: {output_path}")
    print(f"  总时长: {sum(news.duration for news in news_list):.1f} 秒")

    return output_path


def get_video_info(news_list: List[NewsItem]) -> dict:
    """
    获取视频信息（不实际生成）

    Args:
        news_list: 新闻列表

    Returns:
        视频信息字典
    """
    total_duration = sum(news.duration for news in news_list)

    return {
        "news_count": len(news_list),
        "total_duration": total_duration,
        "duration_formatted": f"{int(total_duration // 60)}:{int(total_duration % 60):02d}",
        "resolution": f"{config.LAYOUT_CONFIG['canvas_width']}x{config.LAYOUT_CONFIG['canvas_height']}",
        "fps": config.VIDEO_FPS,
    }
