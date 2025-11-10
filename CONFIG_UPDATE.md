# 配置功能更新说明

## 新增功能

### 1. 图形化配置界面

在主界面右上角添加了 **⚙️ 设置** 按钮，点击后可打开配置对话框。

#### LLM 配置
- API Key（支持密码显示/隐藏）
- Base URL（API 端点地址）
- 模型名称

#### RSS 源配置
- 添加/删除 RSS 分类
- 添加/删除 RSS 源
- 实时预览已有配置

### 2. 配置管理模块

创建了 `services/config_manager.py` 模块，负责：
- 加载和保存用户配置
- 提供配置的增删改查接口
- 默认配置管理

### 3. 配置文件持久化

- 配置保存在 `user_config.json` 文件
- 支持 JSON 格式的用户配置
- 已添加到 `.gitignore`，不会被提交到版本控制

### 4. 配置优先级

系统按以下优先级读取配置：
1. 用户配置文件 (`user_config.json`) - 最高
2. 环境变量 (`.env` 或系统环境变量)
3. 默认值（内置）

## 文件变更

### 新增文件
- `services/config_manager.py` - 配置管理模块
- `CONFIG_GUIDE.md` - 详细配置指南
- `user_config.json.example` - 配置文件示例
- `test_config.py` - 配置功能测试

### 修改文件
- `main.py` - 添加配置对话框和设置按钮
- `config.py` - 支持从配置文件加载
- `README.md` - 更新使用说明
- `.gitignore` - 排除用户配置文件

## 使用方法

### 首次配置

1. 启动应用：`uv run main.py`
2. 点击右上角的 ⚙️ 设置按钮
3. 填写 LLM 配置（API Key、Base URL、Model）
4. （可选）添加自定义 RSS 源
5. 点击"保存"按钮

### 修改配置

随时点击设置按钮即可修改配置，保存后立即生效。

### 重置配置

删除 `user_config.json` 文件，重启应用即可恢复默认配置。

## 技术细节

### 配置文件格式

```json
{
  "llm": {
    "api_key": "your-api-key",
    "base_url": "https://api.moonshot.cn/v1",
    "model": "kimi-k2-turbo-preview"
  },
  "rss_sources": {
    "分类名": [
      {
        "name": "RSS源名称",
        "url": "RSS地址",
        "default_count": 5
      }
    ]
  }
}
```

### 配置加载流程

1. `ConfigManager` 初始化时读取 `user_config.json`
2. 如果文件不存在，使用默认配置
3. `config.py` 在模块加载时也会尝试读取配置文件
4. 保存时，配置会同时更新到内存和文件

### 配置更新机制

- 保存配置后，通过环境变量更新 `config` 模块的值
- 刷新主界面的 RSS 下拉框选项
- 下次启动时自动加载保存的配置

## 兼容性

- 完全向后兼容，仍支持通过环境变量配置
- 未设置配置文件时，使用默认值
- 配置文件优先级高于环境变量

## 测试

运行测试脚本验证配置功能：

```bash
uv run python test_config.py
```

## 下一步优化建议

1. 添加配置导入/导出功能
2. 支持多套配置方案切换
3. 添加配置验证（测试 API Key 是否有效）
4. 支持从 OPML 导入 RSS 源
5. 添加 RSS 源预设模板（更多分类）
