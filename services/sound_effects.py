"""
音效生成模块 - 生成键盘按键等音效
"""

import numpy as np
from scipy.io import wavfile
import os
import config


def generate_keyboard_click_sound(output_path: str = None, duration: float = 0.15) -> str:
    """
    生成键盘按键音效（类似机械键盘的咔哒声）

    Args:
        output_path: 输出路径，如果为 None 则使用默认路径
        duration: 音效时长（秒）

    Returns:
        音频文件路径
    """
    if output_path is None:
        output_path = os.path.join(config.AUDIO_DIR, "keyboard_click.wav")

    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # 采样率
    sample_rate = 44100
    samples = int(sample_rate * duration)

    # 生成多个频率的正弦波叠加（模拟按键的复合音色）
    t = np.linspace(0, duration, samples)

    # 基础频率（800Hz - 高频清脆的按键声）
    freq1 = 800
    sound1 = np.sin(2 * np.pi * freq1 * t)

    # 泛音（1600Hz）
    freq2 = 1600
    sound2 = 0.5 * np.sin(2 * np.pi * freq2 * t)

    # 泛音（2400Hz）
    freq3 = 2400
    sound3 = 0.3 * np.sin(2 * np.pi * freq3 * t)

    # 叠加音频
    sound = sound1 + sound2 + sound3

    # 添加包络（快速衰减，模拟按键的短促声音）
    envelope = np.exp(-8 * t)  # 指数衰减
    sound = sound * envelope

    # 归一化并转换为 16-bit PCM
    sound = sound / np.max(np.abs(sound))  # 归一化到 [-1, 1]
    sound = (sound * 0.3 * 32767).astype(np.int16)  # 降低音量到 30%，转换为 int16

    # 保存为 WAV 文件
    wavfile.write(output_path, sample_rate, sound)

    print(f"✓ 键盘音效已生成: {output_path}")
    return output_path


def generate_transition_sound(output_path: str = None, duration: float = 0.2) -> str:
    """
    生成更柔和的过渡音效

    Args:
        output_path: 输出路径
        duration: 音效时长（秒）

    Returns:
        音频文件路径
    """
    if output_path is None:
        output_path = os.path.join(config.AUDIO_DIR, "transition.wav")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    sample_rate = 44100
    samples = int(sample_rate * duration)
    t = np.linspace(0, duration, samples)

    # 使用较低频率，声音更柔和
    freq1 = 600
    sound1 = np.sin(2 * np.pi * freq1 * t)

    freq2 = 900
    sound2 = 0.4 * np.sin(2 * np.pi * freq2 * t)

    # 叠加
    sound = sound1 + sound2

    # 渐进渐出包络
    fade_in = np.linspace(0, 1, int(samples * 0.1))
    fade_out = np.linspace(1, 0, int(samples * 0.3))
    envelope = np.ones(samples)
    envelope[:len(fade_in)] = fade_in
    envelope[-len(fade_out):] = fade_out

    sound = sound * envelope

    # 归一化
    sound = sound / np.max(np.abs(sound))
    sound = (sound * 0.2 * 32767).astype(np.int16)  # 音量 20%

    wavfile.write(output_path, sample_rate, sound)

    print(f"✓ 过渡音效已生成: {output_path}")
    return output_path


def ensure_sound_effects() -> dict:
    """
    确保所有音效文件存在，如果不存在则生成

    Returns:
        音效文件路径字典
    """
    effects = {
        "keyboard_click": os.path.join(config.AUDIO_DIR, "keyboard_click.wav"),
        "transition": os.path.join(config.AUDIO_DIR, "transition.wav"),
    }

    # 检查并生成缺失的音效
    if not os.path.exists(effects["keyboard_click"]):
        generate_keyboard_click_sound(effects["keyboard_click"])

    if not os.path.exists(effects["transition"]):
        generate_transition_sound(effects["transition"])

    return effects


if __name__ == "__main__":
    # 测试生成音效
    print("生成音效文件...")
    effects = ensure_sound_effects()
    print("\n所有音效文件:")
    for name, path in effects.items():
        print(f"  {name}: {path}")
