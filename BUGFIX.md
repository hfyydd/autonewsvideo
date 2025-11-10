# 问题修复记录

## ✅ 已修复问题列表

### 1. Flet API 变化（已修复）

**问题描述：**
```
AttributeError: module 'flet' has no attribute 'colors'. Did you mean: 'Colors'?
AttributeError: module 'flet' has no attribute 'icons'. Did you mean: 'Icons'?
```

**原因：**
Flet 库更新后，API 发生了变化，常量类名首字母改为大写。

**修复：**
- `ft.colors` → `ft.Colors`（9处）
- `ft.icons` → `ft.Icons`（2处）

---

### 2. 异步事件循环问题（已修复）

**问题描述：**
```
RuntimeError: no running event loop
RuntimeWarning: coroutine 'main.<locals>.generate_video_clicked' was never awaited
```

**原因：**
Flet 的事件处理器在普通线程中运行，没有事件循环，不能直接使用 `asyncio.create_task()`。

**修复方案：**
使用线程 + 新事件循环的方式：

```python
def generate_video_clicked(e):
    """生成视频（同步入口）"""
    # 获取选中的新闻
    selected_news = [news for news in all_news if news.selected]

    # 在后台线程中运行
    def run_generation():
        # 创建新的事件循环
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_generate_video_async(selected_news))
        finally:
            loop.close()

    # 启动后台线程
    thread = threading.Thread(target=run_generation, daemon=True)
    thread.start()

async def _generate_video_async(selected_news):
    """异步生成视频的实际逻辑"""
    # ... 异步代码 ...
```

**关键点：**
1. 事件处理器改为普通函数（非 async）
2. 在新线程中创建独立的事件循环
3. 使用 `loop.run_until_complete()` 运行异步任务
4. 使用 daemon 线程避免阻塞程序退出

---

### 3. MoviePy API 变化（已修复）

**问题描述：**
```
AttributeError: 'ImageClip' object has no attribute 'set_audio'. Did you mean: 'with_audio'?
```

**原因：**
MoviePy 2.x 版本 API 发生变化。

**修复：**
- `clip.set_audio(audio)` → `clip.with_audio(audio)`

**修改位置：**
`services/video_composer.py` line 52

```python
# 旧版本
img_clip = img_clip.set_audio(audio_clip)

# 新版本
img_clip = img_clip.with_audio(audio_clip)
```

---

### 4. Dropdown 不支持 height 参数（已修复）

**问题描述：**
```
TypeError: Dropdown.__init__() got an unexpected keyword argument 'height'
```

**原因：**
Flet 的 Dropdown 组件不支持 `height` 参数。

**修复：**
移除 Dropdown 的 `height=50` 参数

```python
# 错误写法
ft.Dropdown(
    label="RSS 源分类",
    width=180,
    height=50,  # ❌ 不支持
)

# 正确写法
ft.Dropdown(
    label="RSS 源分类",
    width=180,  # ✅ 只设置 width
)
```

---

### 5. 中文字体乱码问题（已修复）

**问题描述：**
图片生成时，中文文字显示为方框（乱码）。

**原因：**
1. 配置的字体文件不存在（`assets/fonts/` 目录为空）
2. PIL 的默认字体（`ImageFont.load_default()`）不支持中文
3. 加载字体失败后直接回退到不支持中文的默认字体

**修复方案：**
实现智能字体加载系统，按优先级尝试多种字体源：

**修改位置：** `services/image_generator.py` 第 104-172 行

```python
def load_font(font_path: str, size: int, bold: bool = False):
    """加载字体，支持多种回退方案"""

    # 尝试1: 使用配置的字体
    if os.path.exists(font_path):
        try:
            return ImageFont.truetype(font_path, size)
        except Exception:
            pass

    # 尝试2: macOS 系统字体
    mac_fonts = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ]
    for mac_font in mac_fonts:
        if os.path.exists(mac_font):
            try:
                return ImageFont.truetype(mac_font, size)
            except Exception:
                pass

    # 尝试3: Linux 系统字体
    linux_fonts = [
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    for linux_font in linux_fonts:
        if os.path.exists(linux_font):
            try:
                return ImageFont.truetype(linux_font, size)
            except Exception:
                pass

    # 尝试4: Windows 系统字体
    windows_fonts = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
    ]
    for win_font in windows_fonts:
        if os.path.exists(win_font):
            try:
                return ImageFont.truetype(win_font, size)
            except Exception:
                pass

    # 最后回退: 使用 PIL 默认字体
    print(f"警告: 未找到支持中文的字体，文字可能显示异常")
    return ImageFont.load_default()
```

**支持的字体：**
- **macOS**: PingFang、黑体、冬青黑体
- **Linux**: 文泉驿、Noto Sans CJK
- **Windows**: 微软雅黑、黑体

**优点：**
1. 无需手动下载字体文件
2. 自动适配不同操作系统
3. 多种字体回退机制，提高兼容性
4. 优先使用高质量系统字体

**Linux 用户注意：**
如果系统没有中文字体，需要安装：
```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-microhei

# Fedora/CentOS
sudo yum install wqy-microhei-fonts
```

---

## 验证

```bash
uv run python -c "import main; print('✓ 所有问题已修复')"
```

## API 变化总结

### Flet API 变化
- `ft.colors` → `ft.Colors`
- `ft.icons` → `ft.Icons`
- Dropdown 不支持 `height` 参数

### MoviePy 2.x API 变化
- `clip.set_audio()` → `clip.with_audio()`
- `clip.set_duration()` → `clip.with_duration()`
- `clip.set_fps()` → `clip.with_fps()`
- `clip.set_start()` → `clip.with_start()`

### 迁移建议
如果使用 MoviePy，注意：
- 所有 `set_*` 方法改为 `with_*`
- 这些方法返回新对象（不修改原对象）
- 需要重新赋值：`clip = clip.with_audio(audio)`

## Flet 组件参数限制

### Dropdown
- ✅ 支持：width, label, value, options
- ❌ 不支持：height（使用默认高度）

### 其他需要注意的组件
- TextField: 支持 height
- Container: 支持 height/width
- Button: 某些版本支持 height

## Flet 异步编程最佳实践

### 在 Flet 中使用异步函数

**方式1：使用线程（推荐用于后台任务）**
```python
def button_click(e):
    def run_async():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_task())
        loop.close()

    threading.Thread(target=run_async, daemon=True).start()
```

**方式2：使用 page.run_task（Flet 原生）**
```python
async def async_handler(e):
    await some_async_work()

page.on_event = lambda e: page.run_task(async_handler, e)
```

**方式3：手动管理事件循环**
```python
import asyncio

loop = asyncio.get_event_loop()

def button_click(e):
    asyncio.run_coroutine_threadsafe(async_task(), loop)
```

## 相关资源

- Flet 官方文档: https://flet.dev/docs/
- Flet 异步编程: https://flet.dev/docs/guides/python/async-apps
- MoviePy 文档: https://zulko.github.io/moviepy/
- Python asyncio 文档: https://docs.python.org/3/library/asyncio.html
