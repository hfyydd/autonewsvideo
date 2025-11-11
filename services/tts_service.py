import edge_tts
import asyncio
import os
from models.news import NewsItem
import config
from services.config_manager import ConfigManager
from services.minimax_tts import MinimaxTTSService


async def generate_news_audio(news: NewsItem, index: int, voice: str = None, tts_engine: str = None) -> tuple[str, float]:
    """
    为整条新闻生成语音

    Args:
        news: 新闻对象（需包含 tts_script）
        index: 新闻索引
        voice: 语音类型（默认使用配置中的默认值）
        tts_engine: TTS引擎 ("edge" 或 "minimax", 默认从配置读取)

    Returns:
        (audio_path, duration) 音频路径和时长
    """

    if voice is None:
        voice = config.TTS_DEFAULT_VOICE

    # 使用 TTS 文案
    full_text = news.tts_script

    if not full_text:
        raise ValueError(f"新闻 {index} 的 TTS 文案为空")

    # 确保输出目录存在
    os.makedirs(config.AUDIO_DIR, exist_ok=True)

    # 输出路径
    output_path = os.path.join(config.AUDIO_DIR, f"news_{index:03d}.mp3")

    # 获取 TTS 引擎配置
    if tts_engine is None:
        config_manager = ConfigManager()
        tts_config = config_manager.get_tts_config()
        tts_engine = tts_config.get("engine", "edge")

    try:
        if tts_engine == "minimax":
            # 使用 MiniMax TTS
            return await _generate_with_minimax(full_text, output_path)
        else:
            # 使用 Edge TTS (默认)
            return await _generate_with_edge(full_text, output_path, voice)

    except Exception as e:
        print(f"生成语音失败: {e}")
        # 返回一个默认时长（用于测试）
        return "", 10.0


async def _generate_with_edge(text: str, output_path: str, voice: str) -> tuple[str, float]:
    """使用 Edge TTS 生成语音"""
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=config.TTS_RATE,
        pitch=config.TTS_PITCH
    )

    await communicate.save(output_path)
    duration = await get_audio_duration(output_path)
    return output_path, duration


async def _generate_with_minimax(text: str, output_path: str) -> tuple[str, float]:
    """使用 MiniMax TTS 生成语音"""
    config_manager = ConfigManager()
    tts_config = config_manager.get_tts_config()

    api_key = tts_config.get("minimax_api_key", "")
    model = tts_config.get("minimax_model", "speech-2.6-hd")
    voice_id = tts_config.get("minimax_voice_id", "male-qn-qingse")

    if not api_key:
        raise ValueError("MiniMax API Key 未配置，请在设置中配置")

    # MiniMax API 是同步的,在事件循环中运行
    loop = asyncio.get_event_loop()
    service = MinimaxTTSService(api_key=api_key, model=model, voice_id=voice_id)

    # 在线程池中运行同步函数
    return await loop.run_in_executor(
        None,
        service.generate_audio,
        text,
        output_path
    )


async def get_audio_duration(audio_path: str) -> float:
    """
    获取音频文件时长

    Args:
        audio_path: 音频文件路径

    Returns:
        时长（秒）
    """
    try:
        # 使用 mutagen 获取时长
        from mutagen.mp3 import MP3
        audio = MP3(audio_path)
        return audio.info.length
    except:
        try:
            # 备用方案：使用 moviepy
            from moviepy import AudioFileClip
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_clip.close()
            return duration
        except:
            # 如果都失败，估算时长（中文约 5 字/秒）
            print(f"警告: 无法获取音频时长，使用估算值")
            return 10.0


async def batch_generate_audio(news_list: list[NewsItem], voice: str = None) -> list[NewsItem]:
    """
    批量生成多条新闻的语音

    Args:
        news_list: 新闻列表
        voice: 语音类型

    Returns:
        更新后的新闻列表
    """
    for i, news in enumerate(news_list):
        print(f"正在生成第 {i+1}/{len(news_list)} 条新闻语音...")

        audio_path, duration = await generate_news_audio(news, i, voice)
        news.audio_path = audio_path
        news.duration = duration

        print(f"  完成 - 时长: {duration:.1f}秒")

    return news_list


async def generate_opening_audio(script: str, voice: str = None, tts_engine: str = None) -> tuple[str, float]:
    """
    为片头生成语音

    Args:
        script: 片头文案
        voice: 语音类型（默认使用配置中的默认值）
        tts_engine: TTS引擎 ("edge" 或 "minimax", 默认从配置读取)

    Returns:
        (audio_path, duration) 音频路径和时长
    """

    if voice is None:
        voice = config.TTS_DEFAULT_VOICE

    if not script:
        raise ValueError("片头文案为空")

    # 确保输出目录存在
    os.makedirs(config.AUDIO_DIR, exist_ok=True)

    # 输出路径
    output_path = os.path.join(config.AUDIO_DIR, "opening.mp3")

    # 获取 TTS 引擎配置
    if tts_engine is None:
        config_manager = ConfigManager()
        tts_config = config_manager.get_tts_config()
        tts_engine = tts_config.get("engine", "edge")

    try:
        if tts_engine == "minimax":
            # 使用 MiniMax TTS
            return await _generate_with_minimax(script, output_path)
        else:
            # 使用 Edge TTS (默认)
            return await _generate_with_edge(script, output_path, voice)

    except Exception as e:
        print(f"生成片头语音失败: {e}")
        # 返回一个默认时长（用于测试）
        return "", 5.0


def generate_audio_sync(news: NewsItem, index: int, voice: str = None) -> tuple[str, float]:
    """
    同步版本的语音生成（用于非异步环境）

    Args:
        news: 新闻对象
        index: 新闻索引
        voice: 语音类型

    Returns:
        (audio_path, duration)
    """
    return asyncio.run(generate_news_audio(news, index, voice))
