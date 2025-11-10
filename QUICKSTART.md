# 快速开始指南

## 1. 安装依赖

```bash
# 同步依赖
uv sync
```

## 2. 配置 API Key（可选）

如果要使用 AI 文案生成功能，需要配置 API Key：

```bash
# 使用 Kimi API（默认，推荐）
export KIMI_API_KEY="sk-your-kimi-api-key"

# 或使用通用环境变量
export AI_API_KEY="your-api-key"
export AI_BASE_URL="https://api.moonshot.cn/v1"
export AI_MODEL="moonshot-v1-8k"
```

或直接编辑 `config.py` 文件。

**获取 Kimi API Key**：
1. 访问 [Moonshot AI 开放平台](https://platform.moonshot.cn/)
2. 注册并创建 API Key
3. 复制 Key 到配置中

**其他 AI 服务**：
- 通义千问: `https://dashscope.aliyuncs.com/compatible-mode/v1`
- OpenAI: `https://api.openai.com/v1`
- 其他 OpenAI 兼容服务

如果不配置，系统会使用简单的文本处理（不调用 AI）。

## 3. 准备字体（推荐）

为了正确显示中文，建议下载字体：

1. 下载 [Noto Sans SC](https://fonts.google.com/noto/specimen/Noto+Sans+SC)
2. 将以下文件放到 `assets/fonts/` 目录：
   - `NotoSansSC-Regular.ttf`
   - `NotoSansSC-Bold.ttf`

如果不添加字体，系统会使用默认字体（可能无法显示中文）。

## 4. 运行应用

```bash
uv run main.py
```

## 5. 使用流程

### 第一步：获取新闻

1. 选择 RSS 源分类（科技新闻/财经新闻/国际新闻）
2. 点击"获取新闻"按钮
3. 等待新闻列表加载

### 第二步：选择新闻

1. 勾选要制作成视频的新闻（建议 3-5 条）
2. 可以使用"全选"或"清空"按钮

### 第三步：视频设置

1. 选择卡片风格（蓝色/粉色/绿色/紫色）
2. 选择语音类型（中文女声/男声等）

### 第四步：生成视频

1. 点击"开始生成视频"
2. 等待进度条完成（可能需要几分钟）
3. 视频会保存到 `output/videos/news_collection.mp4`

## 6. 输出文件

生成过程中会产生以下文件：

```
output/
├── images/
│   ├── news_card_000.png  # 第1条新闻的卡片
│   ├── news_card_001.png  # 第2条新闻的卡片
│   └── ...
├── audio/
│   ├── news_000.mp3       # 第1条新闻的语音
│   ├── news_001.mp3       # 第2条新闻的语音
│   └── ...
└── videos/
    └── news_collection.mp4  # 最终视频
```

## 常见问题

### Q: 提示 "获取新闻失败"

A: 检查网络连接，或者 RSS 源可能暂时不可用。可以在 `config.py` 中更换其他 RSS 源。

### Q: 提示 "AI 生成失败"

A: 检查 QWEN_API_KEY 是否正确配置。如果未配置，系统会使用备用方案。

### Q: 图片上文字显示为方块

A: 需要安装中文字体到 `assets/fonts/` 目录。

### Q: 视频合成失败

A: MoviePy 首次运行可能需要下载 ffmpeg。如果失败，手动安装 ffmpeg：

```bash
# macOS
brew install ffmpeg

# Ubuntu
sudo apt install ffmpeg

# Windows
# 从 https://ffmpeg.org/download.html 下载
```

### Q: 视频时长太短/太长

A: 时长由语音自动决定。可以在 AI 生成文案后手动调整每条新闻的要点数量。

## 进阶配置

### 添加自定义 RSS 源

编辑 `config.py`：

```python
RSS_PRESETS = {
    "我的分类": [
        {"name": "源名称", "url": "RSS地址", "default_count": 5},
    ],
}
```

### 调整卡片样式

修改 `config.py` 中的参数：

```python
LAYOUT_CONFIG = {
    "title_font_size": 70,    # 标题字号
    "point_font_size": 45,    # 要点字号
    # ...
}
```

### 更换 TTS 语音

查看 [Edge TTS 语音列表](https://speech.microsoft.com/portal/voicegallery)，添加到 `config.py`:

```python
TTS_VOICES = {
    "新语音": "zh-CN-XiaoxiaoNeural",
}
```

## 技术支持

如有问题，请查看：
- `README.md` - 项目说明
- `CLAUDE.md` - 架构文档
- GitHub Issues（如果项目已开源）
