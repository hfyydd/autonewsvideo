"""
MiniMax TTS 服务
提供基于 MiniMax API 的文本转语音功能
"""
import os
import requests
from typing import Tuple, Optional
from mutagen.mp3 import MP3


class MinimaxTTSService:
    """MiniMax TTS 服务类"""

    def __init__(self, api_key: str, model: str = "speech-2.6-hd", voice_id: str = "male-qn-qingse"):
        """
        初始化 MiniMax TTS 服务

        Args:
            api_key: MiniMax API 密钥
            model: 模型版本 (speech-2.6-hd, speech-02-turbo 等)
            voice_id: 音色编号
        """
        self.api_key = api_key
        self.model = model
        self.voice_id = voice_id
        self.base_url = "https://api.minimaxi.com/v1/t2a_v2"

    def generate_audio(self, text: str, output_path: str,
                      speed: float = 1.0,
                      volume: float = 1.0,
                      emotion: str = "neutral") -> Tuple[str, float]:
        """
        生成语音音频

        Args:
            text: 要转换的文本
            output_path: 输出音频文件路径
            speed: 语速 (0.5-2.0)
            volume: 音量 (0.1-2.0)
            emotion: 情绪 (neutral, happy, sad, angry, fearful, etc.)

        Returns:
            (audio_path, duration) 元组

        Raises:
            Exception: API 调用失败时抛出异常
        """
        if not self.api_key:
            raise ValueError("MiniMax API Key 未配置")

        if len(text) > 10000:
            raise ValueError("文本长度不能超过 10000 字符")

        # 构造请求
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": self.model,
            "text": text,
            "stream": False,  # 非流式
            "voice_setting": {
                "voice_id": self.voice_id,
                "speed": speed,
                "vol": volume,
                "emotion": emotion
            },
            "audio_setting": {
                "sample_rate": 32000,
                "format": "mp3",
                "channel": 1  # 单声道
            }
        }

        try:
            # 调用 API
            response = requests.post(
                self.base_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            result = response.json()

            # 检查响应状态
            if result.get("base_resp", {}).get("status_code") != 0:
                error_msg = result.get("base_resp", {}).get("status_msg", "未知错误")
                raise Exception(f"MiniMax API 错误: {error_msg}")

            # 获取音频数据 (hex 编码)
            audio_hex = result.get("data", {}).get("audio")
            if not audio_hex:
                raise Exception("API 返回的音频数据为空")

            # 解码 hex 数据并保存
            audio_bytes = bytes.fromhex(audio_hex)

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with open(output_path, 'wb') as f:
                f.write(audio_bytes)

            # 获取音频时长
            duration = self._get_audio_duration(output_path)

            print(f"✓ MiniMax TTS 生成成功: {output_path} (时长: {duration:.2f}秒)")
            return output_path, duration

        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"MiniMax TTS 生成失败: {str(e)}")

    def _get_audio_duration(self, audio_path: str) -> float:
        """
        获取音频文件时长

        Args:
            audio_path: 音频文件路径

        Returns:
            时长(秒)
        """
        try:
            audio = MP3(audio_path)
            return audio.info.length
        except Exception as e:
            print(f"警告: 无法获取音频时长: {e}")
            # 返回一个默认值，基于文本长度估算
            return 0.0

    @staticmethod
    def get_available_voices() -> dict:
        """
        获取可用的音色列表

        Returns:
            音色字典 {display_name: voice_id}
        """
        return {
            "青涩青年音色": "male-qn-qingse",
            "精英青年音色": "male-qn-jingying",
            "霸道青年音色": "male-qn-badao",
            "青年大学生音色": "male-qn-daxuesheng",
            "少女音色": "female-shaonv",
            "御姐音色": "female-yujie",
            "成熟女性音色": "female-chengshu",
            "甜美女性音色": "female-tianmei",
            "男性主持人": "presenter_male",
            "女性主持人": "presenter_female",
            "男性有声书1": "audiobook_male_1",
            "男性有声书2": "audiobook_male_2",
            "女性有声书1": "audiobook_female_1",
            "女性有声书2": "audiobook_female_2",
        }
