# 问题修复：AssertionError: Container Control must be added to the page first

## 问题描述

在运行应用时遇到错误：
```
AssertionError: Container Control must be added to the page first
```

## 根本原因

在 Flet 中，控件必须先添加到页面后才能调用 `.update()` 方法。原代码在 `refresh_rss_list()` 函数中调用了 `settings_dialog.content.update()`，但此时对话框还没有被添加到页面的 overlay 中。

### 问题代码位置

```python
def refresh_rss_list():
    # ... 构建 RSS 列表 ...
    settings_dialog.content.update()  # ❌ 错误：对话框还未添加到页面
```

## 解决方案

### 1. 提前声明对话框对象

在函数定义前先创建空的对话框对象：

```python
# 配置对话框（先定义，后面才能在 refresh_rss_list 中检查状态）
settings_dialog = ft.AlertDialog(
    open=False,  # 初始为关闭状态
)
```

### 2. 修改刷新逻辑

只在对话框已经打开时才更新页面：

```python
def refresh_rss_list():
    """刷新 RSS 列表显示"""
    rss_list_view.controls.clear()

    # ... 构建 RSS 列表 ...

    # 只在对话框已经添加到页面时才更新
    if settings_dialog.open:
        page.update()
```

### 3. 后续配置对话框内容

在定义完所有辅助函数后，更新对话框的内容和属性：

```python
# 更新对话框内容
settings_dialog.title = ft.Text("设置", ...)
settings_dialog.content = ft.Container(...)
settings_dialog.actions = [...]
```

## 修改文件

- `main.py` (第 392-557 行)

## 测试

运行启动测试验证修复：

```bash
uv run python test_startup.py
```

预期输出：
```
✓ 所有测试通过！应用可以正常启动。
```

## 相关知识

### Flet 控件更新机制

1. **控件必须在页面树中**：只有已添加到 `page` 或其子控件的控件才能调用 `update()`
2. **对话框的特殊性**：对话框通过 `page.overlay.append()` 添加到页面
3. **更新时机**：在对话框 `open=True` 之后才会真正添加到页面

### 最佳实践

1. **延迟更新**：使用条件判断确保控件已添加
2. **统一更新**：优先使用 `page.update()` 而不是单个控件的 `update()`
3. **对话框模式**：先创建空对话框对象，再配置内容

## 验证步骤

1. 运行语法检查：`uv run python -m py_compile main.py` ✓
2. 运行模块导入测试：`uv run python test_startup.py` ✓
3. 启动应用：`uv run main.py`
4. 点击设置按钮，验证对话框正常显示
5. 添加/删除 RSS 源，验证列表刷新正常
