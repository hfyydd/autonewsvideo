import json
import os
from typing import Dict, List, Any


class ConfigManager:
    """配置管理器，负责保存和加载用户配置"""

    def __init__(self, config_file: str = "user_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载配置文件失败: {e}")
                return self._get_default_config()
        else:
            return self._get_default_config()

    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "llm": {
                "api_key": "",
                "base_url": "https://api.moonshot.cn/v1",
                "model": "kimi-k2-turbo-preview",
            },
            "tts": {
                "engine": "edge",  # edge 或 minimax
                "edge_voice": "中文女声",  # Edge TTS 音色
                "minimax_api_key": "",
                "minimax_model": "speech-2.6-hd",
                "minimax_voice_id": "male-qn-qingse",
            },
            "rss_sources": {
                "科技新闻": [
                    {"name": "36氪", "url": "https://36kr.com/feed", "default_count": 5},
                    {"name": "IT之家", "url": "https://www.ithome.com/rss/", "default_count": 3},
                    {"name": "少数派", "url": "https://sspai.com/feed", "default_count": 3},
                    {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss", "default_count": 3},
                ],
                "财经新闻": [
                    {"name": "华尔街见闻", "url": "https://wallstreetcn.com/feed", "default_count": 5},
                    {"name": "财联社", "url": "https://www.cls.cn/rss", "default_count": 3},
                ],
                "国际新闻": [
                    {"name": "BBC中文", "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml", "default_count": 5},
                ],
            }
        }

    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False

    # ===== LLM 配置 =====
    def get_llm_config(self) -> Dict[str, str]:
        """获取 LLM 配置"""
        return self.config.get("llm", self._get_default_config()["llm"])

    def set_llm_config(self, api_key: str, base_url: str, model: str):
        """设置 LLM 配置"""
        self.config["llm"] = {
            "api_key": api_key,
            "base_url": base_url,
            "model": model,
        }

    # ===== RSS 源配置 =====
    def get_rss_categories(self) -> List[str]:
        """获取所有 RSS 分类"""
        return list(self.config.get("rss_sources", {}).keys())

    def get_rss_sources(self, category: str) -> List[Dict[str, Any]]:
        """获取指定分类的 RSS 源"""
        return self.config.get("rss_sources", {}).get(category, [])

    def add_rss_category(self, category: str):
        """添加新的 RSS 分类"""
        if "rss_sources" not in self.config:
            self.config["rss_sources"] = {}
        if category not in self.config["rss_sources"]:
            self.config["rss_sources"][category] = []

    def remove_rss_category(self, category: str):
        """删除 RSS 分类"""
        if "rss_sources" in self.config and category in self.config["rss_sources"]:
            del self.config["rss_sources"][category]

    def add_rss_source(self, category: str, name: str, url: str, default_count: int = 5):
        """添加 RSS 源到指定分类"""
        if "rss_sources" not in self.config:
            self.config["rss_sources"] = {}
        if category not in self.config["rss_sources"]:
            self.config["rss_sources"][category] = []

        self.config["rss_sources"][category].append({
            "name": name,
            "url": url,
            "default_count": default_count
        })

    def remove_rss_source(self, category: str, index: int):
        """从指定分类删除 RSS 源"""
        if "rss_sources" in self.config and category in self.config["rss_sources"]:
            sources = self.config["rss_sources"][category]
            if 0 <= index < len(sources):
                sources.pop(index)

    def update_rss_source(self, category: str, index: int, name: str, url: str, default_count: int):
        """更新 RSS 源"""
        if "rss_sources" in self.config and category in self.config["rss_sources"]:
            sources = self.config["rss_sources"][category]
            if 0 <= index < len(sources):
                sources[index] = {
                    "name": name,
                    "url": url,
                    "default_count": default_count
                }

    def get_all_rss_sources(self) -> Dict[str, List[Dict[str, Any]]]:
        """获取所有 RSS 源"""
        return self.config.get("rss_sources", {})

    # ===== TTS 配置 =====
    def get_tts_config(self) -> Dict[str, str]:
        """获取 TTS 配置"""
        return self.config.get("tts", self._get_default_config()["tts"])

    def set_tts_config(self, engine: str, edge_voice: str = "", minimax_api_key: str = "", minimax_model: str = "", minimax_voice_id: str = ""):
        """设置 TTS 配置"""
        self.config["tts"] = {
            "engine": engine,
            "edge_voice": edge_voice or "中文女声",
            "minimax_api_key": minimax_api_key,
            "minimax_model": minimax_model or "speech-2.6-hd",
            "minimax_voice_id": minimax_voice_id or "male-qn-qingse",
        }
