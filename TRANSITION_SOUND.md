# 键盘过渡音效功能

## 功能说明

在视频图片切换时添加键盘按键音效，使视频过渡更加生动自然。

## 实现细节

### 1. 音效生成模块 (`services/sound_effects.py`)

创建了专门的音效生成模块，使用 numpy 和 scipy 生成合成音效：

#### 键盘按键音效
- **频率组合**: 800Hz (基础频率) + 1600Hz (泛音) + 2400Hz (高频泛音)
- **包络**: 快速指数衰减，模拟按键的短促声音
- **时长**: 0.15秒
- **音量**: 30% (避免过大干扰语音)

```python
def generate_keyboard_click_sound(output_path: str = None, duration: float = 0.15) -> str:
    # 生成多频率正弦波叠加
    # 添加快速衰减包络
    # 保存为 WAV 文件
```

#### 过渡音效（备用）
- 更柔和的版本，频率较低 (600Hz + 900Hz)
- 带有渐进渐出包络
- 音量 20%

### 2. 视频合成集成 (`services/video_composer.py`)

在视频合成时自动添加过渡音效：

**关键改动**:

1. **导入音效模块** (第 8 行)
   ```python
   from services.sound_effects import ensure_sound_effects
   ```

2. **确保音效文件存在** (第 47-48 行)
   ```python
   sound_effects = ensure_sound_effects()
   transition_sound_path = sound_effects["keyboard_click"]
   ```

3. **叠加音效到片段** (第 66-82 行)
   ```python
   if i > 0:  # 第一个片段不需要过渡音
       transition_audio = AudioFileClip(transition_sound_path)
       combined_audio = CompositeAudioClip([
           audio_clip,
           transition_audio.with_start(0)  # 音效在开始时播放
       ])
       img_clip = img_clip.with_audio(combined_audio)
   ```

### 3. 音效文件管理

- **自动生成**: 首次运行时自动生成音效文件
- **存储位置**: `output/audio/keyboard_click.wav`
- **缓存机制**: 文件存在时不重复生成

## 使用效果

### 视频播放体验

1. **第一个新闻片段**: 直接播放，无过渡音
2. **后续片段**: 每个片段开始时播放键盘按键音
3. **音效叠加**: 过渡音与新闻语音同时播放，不影响内容理解

### 音效特点

- ✅ **自然**: 类似机械键盘的清脆声音
- ✅ **适度**: 音量适中，不会盖过语音
- ✅ **短促**: 0.15秒快速结束，不干扰内容
- ✅ **高品质**: 44100Hz 采样率，16-bit PCM

## 依赖包

新增依赖：
```toml
scipy = ">=1.16.0"  # 用于音频文件读写
numpy = ">=1.26.0"  # 用于音频信号处理
```

安装命令：
```bash
uv add scipy
```

## 配置选项

### 修改音效

如果想要调整音效，可以编辑 `services/sound_effects.py`：

1. **音效时长**:
   ```python
   generate_keyboard_click_sound(duration=0.2)  # 改为 0.2 秒
   ```

2. **音量**:
   ```python
   sound = (sound * 0.5 * 32767).astype(np.int16)  # 改为 50%
   ```

3. **频率**:
   ```python
   freq1 = 1000  # 改变基础频率
   ```

### 使用不同音效

如果想使用更柔和的过渡音效：

在 `video_composer.py` 第 48 行改为：
```python
transition_sound_path = sound_effects["transition"]  # 使用 transition 而不是 keyboard_click
```

### 禁用音效

如果不想要过渡音效，注释掉相关代码：

```python
# 第 66-79 行，将整个 if i > 0 块注释掉
# if i > 0:
#     ...
img_clip = img_clip.with_audio(audio_clip)  # 直接使用原始音频
```

## 文件结构

```
output/
├── audio/
│   ├── keyboard_click.wav    # 键盘按键音效
│   ├── transition.wav         # 柔和过渡音效
│   ├── news_000.mp3          # 新闻音频
│   └── ...
├── images/
└── videos/
```

## 技术细节

### 音频合成原理

使用 MoviePy 的 `CompositeAudioClip` 将多个音频层叠加：

```python
CompositeAudioClip([
    audio_clip,              # 底层：新闻语音
    transition_audio         # 顶层：过渡音效
])
```

两个音频同时播放，音量叠加（但由于过渡音很短且音量低，不会造成失真）。

### 音效生成算法

1. **正弦波合成**: 使用多个频率的正弦波叠加模拟真实按键声
2. **包络调制**: 应用指数衰减包络让声音自然结束
3. **归一化**: 防止音频削波和失真
4. **量化**: 转换为 16-bit PCM 格式

## 优化建议

未来可以考虑的改进：

1. **更多音效选项**:
   - 打字机音效
   - 翻页音效
   - 滑动音效

2. **音效随机化**:
   - 每次切换使用略微不同的音调
   - 增加真实感

3. **音效淡入淡出**:
   - 更平滑的音频过渡
   - 避免突兀感

4. **用户自定义**:
   - 允许用户上传自己的音效文件
   - 在配置界面选择音效类型

## 测试

所有测试通过：
```bash
✓ 音效文件生成成功
✓ 语法检查通过
✓ 模块导入正常
✓ 应用启动正常
```

## 示例

生成视频后，在每个新闻片段的切换处会听到清脆的"咔哒"声，类似按下键盘的声音，增强视频的节奏感和专业感。
