# 自动新闻视频生成器

一款从 RSS 新闻源自动生成视频的桌面应用，支持 AI 文案改写、语音合成、卡片式图片生成和视频合成。

## ✨ 功能特性

- 📰 **多源新闻获取**: 预设科技/财经/国际新闻 RSS 源，一键批量获取
- ⚙️ **图形化配置**: 可视化配置 LLM 和 RSS 源，无需编辑配置文件
- 🤖 **AI 文案生成**: 使用国内大模型（Kimi/通义千问）将新闻改写为视频文案
- 🎙️ **语音合成**: 基于 Edge TTS，支持多种中文语音
- 🎨 **自适应卡片**: 根据文案内容自动调整卡片大小，支持多种配色
- 🎬 **自动视频合成**: 图片+语音自动拼接成完整视频
- 📝 **文案预览编辑**: 生成前可预览和编辑 AI 生成的文案

## 🚀 快速开始

### 环境要求

- Python 3.13+
- uv (推荐) 或 pip

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync


```

### 配置 API Key

有两种配置方式：

#### 方式一：使用图形界面配置（推荐）

1. 启动应用：`uv run main.py`
2. 点击界面右上角的 **⚙️ 设置** 按钮
3. 在 "LLM 配置" 区域填写：
   - **API Key**: 你的 AI 服务 API 密钥
   - **Base URL**: API 端点（如 `https://api.moonshot.cn/v1`）
   - **模型名称**: 模型名称（如 `kimi-k2-turbo-preview`）
4. 点击 "保存" 按钮



**获取 Kimi API Key**：
1. 访问 [Moonshot AI 开放平台](https://platform.moonshot.cn/)
2. 注册并创建 API Key
3. 复制 Key 到环境变量

如果不配置 API Key，系统会使用备用方案（简单文本处理）。

### 运行应用

```bash
uv run main.py
```

### 打包应用
```bash
uv run flet build macos --verbose
```

## 📖 使用流程

1. **配置 LLM** → 点击右上角设置按钮，配置 API Key（首次使用）
2. **（可选）自定义 RSS 源** → 在设置中添加/删除 RSS 源
3. **选择 RSS 分类** → 点击"获取新闻"
4. **勾选要制作的新闻** → 支持多选
5. **生成文案预览** → 点击"生成文案预览"，可编辑 TTS 文案和卡片内容
6. **配置视频设置** → 选择卡片风格和语音类型
7. **点击"开始生成"** → 等待完成
8. **视频输出到** `output/videos/news_collection.mp4`

## 🏗️ 项目结构

```
autonewsvideo/
├── main.py                     # Flet GUI 主程序
├── config.py                   # 配置文件
├── CONFIG_GUIDE.md             # 配置指南
├── user_config.json.example    # 配置文件示例
├── models/
│   └── news.py                 # 数据模型
├── services/
│   ├── config_manager.py       # 配置管理
│   ├── rss_fetcher.py          # RSS 获取
│   ├── ai_writer.py            # AI 文案生成
│   ├── tts_service.py          # 语音合成
│   ├── image_generator.py      # 图片生成
│   └── video_composer.py       # 视频合成
├── output/
│   ├── images/                 # 生成的图片
│   ├── audio/                  # 生成的音频
│   └── videos/                 # 最终视频
└── assets/
    └── fonts/                  # 字体文件（需自行下载）
```

## 🎨 自定义配置

### 添加 RSS 源

编辑 `config.py` 中的 `RSS_PRESETS`:

```python
RSS_PRESETS = {
    "科技新闻": [
        {"name": "36氪", "url": "https://36kr.com/feed", "default_count": 5},
        # 添加更多源...
    ],
}
```

### 调整卡片样式

修改 `config.py` 中的 `LAYOUT_CONFIG` 和 `CARD_STYLES`。

### 更换语音

在 `config.py` 的 `TTS_VOICES` 中添加更多 Edge TTS 支持的语音。

### 切换 AI 服务

在 `config.py` 中修改：

```python
# 使用 Kimi（默认）
AI_BASE_URL = "https://api.moonshot.cn/v1"
AI_MODEL = "moonshot-v1-8k"

# 或使用通义千问
AI_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
AI_MODEL = "qwen-plus"

# 或使用 OpenAI
AI_BASE_URL = "https://api.openai.com/v1"
AI_MODEL = "gpt-4"
```

## 📝 字体配置

应用需要中文字体才能正确显示。推荐下载：

- [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)

下载后将字体文件放到 `assets/fonts/` 目录：
- `NotoSansSC-Regular.ttf`
- `NotoSansSC-Bold.ttf`

如果没有字体文件，系统会使用默认字体（可能无法显示中文）。

## 🔧 技术栈

- **GUI**: Flet
- **RSS 解析**: feedparser
- **AI**: OpenAI SDK (兼容 Kimi/通义千问等)
- **TTS**: Edge TTS
- **图片生成**: Pillow
- **视频合成**: MoviePy

## 📋 待办事项

- [ ] 添加更多模板样式
- [ ] 支持自定义背景图
- [ ] 添加片头片尾
- [ ] 支持竖屏视频 (9:16)
- [ ] 批量导出功能
- [ ] 视频预览功能

## ⚠️ 注意事项

1. 首次生成视频可能需要下载 MoviePy 的依赖（ffmpeg）
2. AI 文案生成需要稳定的网络连接
3. 视频合成较耗时，建议一次选择 3-5 条新闻

## 📄 License

MIT
