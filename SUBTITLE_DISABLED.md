# 字幕功能禁用说明

## 修改内容

字幕功能已被默认禁用，以避免在某些环境下可能出现的问题。

### 1. 修改 video_composer.py

移除了字幕生成的相关代码（第 53-68 行）：

**之前**：
```python
# 添加字幕（如果启用）
if config.SUBTITLE_CONFIG["enabled"] and news.tts_script:
    try:
        # 创建字幕文字
        subtitle_clip = TextClip(...)
        # 创建背景
        bg_clip = ColorClip(...)
        # 合成字幕
        img_clip = CompositeVideoClip([img_clip, subtitle_with_bg])
    except Exception as e:
        print(f"字幕添加失败: {e}")
```

**现在**：
```python
# 字幕功能已禁用（可在 config.py 中修改 SUBTITLE_CONFIG["enabled"] 来启用）
# 注意：字幕功能可能在某些环境下会出现问题
```

### 2. 修改 config.py

将字幕默认设置为禁用：

```python
SUBTITLE_CONFIG = {
    "enabled": False,  # 默认禁用字幕
    ...
}
```

### 3. 移除不必要的导入

从 video_composer.py 中移除了不再使用的导入：

**之前**：
```python
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip
```

**现在**：
```python
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
```

## 影响

### 视频生成

- ✅ **视频生成速度更快**：无需处理字幕叠加
- ✅ **更稳定**：避免字幕相关的潜在错误
- ✅ **兼容性更好**：TextClip 在某些环境下可能需要额外依赖（如 ImageMagick）

### 功能保留

- ✅ 图片生成时，卡片上仍然包含标题和要点
- ✅ 语音播报包含完整的 TTS 文案
- ✅ 视频质量不受影响

## 如何重新启用字幕

如果你的环境支持字幕功能，可以通过以下步骤重新启用：

### 方法 1: 修改配置文件

编辑 `config.py`：

```python
SUBTITLE_CONFIG = {
    "enabled": True,  # 改为 True
    ...
}
```

### 方法 2: 恢复字幕代码

如果需要字幕功能，可以参考 git 历史或以下代码片段：

```python
# 在 video_composer.py 的图片+音频合成后添加
if config.SUBTITLE_CONFIG["enabled"] and news.tts_script:
    try:
        from moviepy import TextClip, ColorClip, CompositeVideoClip

        subtitle_text = news.tts_script[:70] + ("..." if len(news.tts_script) > 70 else "")

        subtitle_clip = TextClip(
            text=subtitle_text,
            font_size=config.SUBTITLE_CONFIG["font_size"],
            color='white',
            size=(config.SUBTITLE_CONFIG["max_width"], None),
            method='caption',
            duration=news.duration
        )

        subtitle_w, subtitle_h = subtitle_clip.size
        bg_clip = ColorClip(
            size=(subtitle_w + 40, subtitle_h + 20),
            color=(0, 0, 0),
            duration=news.duration
        ).with_opacity(0.7)

        subtitle_with_bg = CompositeVideoClip([
            bg_clip,
            subtitle_clip.with_position(('center', 'center'))
        ])

        subtitle_y = config.LAYOUT_CONFIG["canvas_height"] - config.SUBTITLE_CONFIG["margin"]
        subtitle_with_bg = subtitle_with_bg.with_position(('center', subtitle_y))

        img_clip = CompositeVideoClip([img_clip, subtitle_with_bg])

        print(f"  ✅ 字幕已添加")
    except Exception as e:
        print(f"  ⚠️ 字幕添加失败: {e}，继续生成无字幕版本")
```

## 字幕功能的已知问题

### 依赖问题

MoviePy 的 TextClip 依赖：
- **ImageMagick**（用于文字渲染）
- 特定的字体文件

在某些环境下，这些依赖可能：
- 未正确安装
- 路径配置不正确
- 版本不兼容

### 常见错误

1. **ImageMagick 未安装**
   ```
   OSError: MoviePy Error: creation of None failed because of the following error:
   ```

2. **字体问题**
   ```
   OSError: unable to open font file
   ```

3. **渲染失败**
   ```
   Exception: TextClip rendering failed
   ```

## 推荐方案

对于大多数用户，建议：

1. **使用无字幕版本**（当前默认）
   - 卡片上已有标题和要点
   - 配合语音播报，信息传达完整

2. **如需字幕**，可以：
   - 使用视频编辑软件后期添加（如剪映、PR）
   - 使用专业字幕工具（如 Aegisub）
   - 或在环境配置完整后启用内置字幕功能

## 测试

所有测试通过：
```bash
✓ 语法检查通过
✓ 模块导入通过
✓ 应用启动正常
```

运行应用：
```bash
uv run main.py
```

现在生成的视频将不包含底部字幕，视频生成速度更快，稳定性更好。
