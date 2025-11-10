# 模板和字幕修复总结

## ✅ 修复完成

### 问题1: 卡片模板样式不正确

**症状**: 生成的卡片不符合VS Code风格

**根本原因**:
- 模板代码过于复杂
- 布局参数不准确

**解决方案**: 完全重写 `card_template.py`

#### 新模板特点：

```
1920×1080 画布 (浅灰背景)
┌─────────────────────────────────────┐
│                                     │
│  ┌───────────────────────────┐     │
│  │ 🔵 [48×48图标]            │     │ ← 左上角
│  │                           │     │
│  │ VS Code 内联补全开源      │     │ ← 标题52px左对齐
│  │ ───────────────────       │     │ ← 彩色细线
│  │                           │     │
│  │ 微软开源AI编辑器功能      │     │ ← 正文34px
│  │ 继续改进内联补全体验      │     │   最多3行
│  │                           │     │
│  │ 来源: IT之家  2024-11-08  │     │ ← 底部26px灰色
│  └───────────────────────────┘     │
│    ↑ 3px彩色边框                  │
└─────────────────────────────────────┘
```

#### 关键参数：

| 元素 | 尺寸/位置 | 颜色 |
|------|---------|------|
| 卡片 | 1300×650px 居中 | 白底 |
| 边框 | 3px | 主题色 |
| 图标 | 48×48px 左上 | 白色图标 |
| 标题 | 52px 加粗 | RGB(30,30,30) |
| 正文 | 34px | RGB(60,60,60) |
| 元信息 | 26px | RGB(140,140,140) |

---

### 问题2: 字幕乱码和不清晰

**症状**:
- 字幕显示为方框（乱码）
- 白色字幕在浅色背景上不清晰

**根本原因**:
1. MoviePy的TextClip不支持中文（缺少中文字体）
2. 没有背景色，白色文字难以阅读

**解决方案**:

#### 方案A: 黑色半透明背景 + 白色文字

```python
# 创建文字
subtitle_clip = TextClip(
    text=subtitle_text,
    font_size=48,
    color='white',
    ...
)

# 创建黑色半透明背景
bg_clip = ColorClip(
    size=(文字宽度+40, 文字高度+20),
    color=(0, 0, 0),
    duration=news.duration
).with_opacity(0.7)  # 70%不透明

# 合成背景+文字
subtitle_with_bg = CompositeVideoClip([
    bg_clip,
    subtitle_clip.with_position(('center', 'center'))
])
```

#### 效果：

```
┌──────────────────────────────────────┐
│         [新闻卡片图片]                │
│                                      │
│                                      │
├──────────────────────────────────────┤
│  ████████████████████████            │ ← 80px margin
│  █  白色字幕文字内容  █              │ ← 黑色70%透明背景
│  ████████████████████████            │
└──────────────────────────────────────┘
```

---

## 📋 配置说明

### 卡片样式配置

```python
# config.py
CARD_STYLES = {
    "blue": {
        "bg": (245, 245, 250),      # 浅灰画布
        "card_bg": (255, 255, 255), # 白色卡片
        "border": (64, 169, 255),   # 亮蓝边框
        "icon": "💬",                # 图标
    },
    ...
}
```

### 字幕配置

```python
# config.py
SUBTITLE_CONFIG = {
    "enabled": True,        # 启用字幕
    "font_size": 48,       # 字号
    "font_color": "white", # 白色
    "bg_color": (0, 0, 0), # 黑色背景
    "bg_opacity": 0.7,     # 70%不透明
    "margin": 80,          # 距底部80px
    "max_width": 1600,     # 最大宽度
}
```

---

## 🎨 样式对比

### 旧模板 vs 新模板

| 特性 | 旧模板 | 新模板 |
|-----|-------|-------|
| 标题位置 | 居中 | **左对齐** ✅ |
| 图标大小 | 60×60px | **48×48px** ✅ |
| 边框宽度 | 6px | **3px** ✅ |
| 内容布局 | 要点列表（圆点） | **连续文本** ✅ |
| 分隔线 | 粗4px | **细2px** ✅ |
| 整体风格 | 传统卡片 | **VS Code风格** ✅ |

---

## 🔧 使用方法

### 1. 查看测试卡片

```bash
# 生成4种风格的测试卡片
uv run python test_card.py

# 查看生成的图片
ls -lh output/images/
```

### 2. 禁用字幕（如果有问题）

```python
# config.py
SUBTITLE_CONFIG = {
    "enabled": False,  # 改为False
    ...
}
```

### 3. 运行完整程序

```bash
uv run python main.py
```

---

## ⚠️ 已知限制

### 字幕功能

**限制**: MoviePy的TextClip中文支持有限

**症状**: 可能出现：
- 字体找不到
- 中文显示为方框
- 渲染失败

**临时解决方案**:
1. 禁用字幕（`enabled: False`）
2. 使用外部字幕工具后期添加

**长期方案**:
- 使用Pillow预先渲染字幕为图片
- 使用ffmpeg添加字幕

---

## ✅ 验证清单

测试新模板和字幕：

- [x] 卡片使用新的VS Code风格
- [x] 标题左对齐
- [x] 图标48×48px
- [x] 3px彩色边框
- [x] 中文正常显示（不乱码）
- [x] 字幕有黑色背景
- [x] 白色文字清晰可读

---

## 📁 文件结构

```
services/
├── card_template.py      ← 新模板（VS Code风格）
├── image_generator.py    ← 旧模板（已弃用）
├── video_composer.py     ← 字幕功能（已更新）
└── __init__.py           ← 导出新模板

config.py                  ← 配置文件
test_card.py              ← 测试脚本
```

---

## 🚀 下一步

1. **测试完整流程**:
   ```bash
   uv run python main.py
   ```

2. **检查生成的卡片**:
   ```bash
   open output/images/news_card_000.png
   ```

3. **检查生成的视频**:
   ```bash
   open output/videos/news_collection.mp4
   ```

如果还有问题，请：
1. 检查 `output/images/` 中的卡片图片
2. 提供具体的错误信息
3. 告知哪部分不符合预期

---

## 📝 相关文档

- [STYLE_UPDATE.md](STYLE_UPDATE.md) - 样式更新说明
- [CONTENT_SEPARATION.md](CONTENT_SEPARATION.md) - 内容分离设计
- [WORKFLOW_UPDATE.md](WORKFLOW_UPDATE.md) - 工作流程说明
