# 配置指南

## 配置页面使用说明

应用现在支持通过图形界面配置 LLM 和 RSS 源，无需手动编辑配置文件。

### 打开配置页面

1. 启动应用：`uv run main.py`
2. 点击界面右上角的 **⚙️ 设置** 按钮
3. 在弹出的设置对话框中进行配置

---

## LLM 配置

### 配置项说明

- **API Key**: 你的 AI 服务 API 密钥
- **Base URL**: API 端点地址
- **模型名称**: 要使用的模型

### 支持的 AI 服务

#### 1. Kimi (月之暗面)
```
API Key: 从 https://platform.moonshot.cn/ 获取
Base URL: https://api.moonshot.cn/v1
模型: kimi-k2-turbo-preview
```

#### 2. OpenAI
```
API Key: 从 https://platform.openai.com/ 获取
Base URL: https://api.openai.com/v1
模型: gpt-4o-mini 或 gpt-4o
```

#### 3. 其他兼容 OpenAI 的服务
只要 API 兼容 OpenAI 格式，都可以使用（如通义千问、Deepseek 等）。

---

## RSS 源配置

### 添加 RSS 源

1. 在设置页面的 "RSS 源配置" 区域
2. 填写以下信息：
   - **分类名称**: 如 "科技新闻"、"财经新闻"（可以是新分类或已有分类）
   - **RSS 源名称**: 如 "36氪"、"IT之家"
   - **RSS URL**: RSS 订阅地址
   - **默认数量**: 每次获取的新闻数量（默认 5）
3. 点击 "添加" 按钮

### 删除 RSS 源

- 在 "现有 RSS 源" 列表中，点击源旁边的 🗑️ 按钮即可删除
- 点击分类标题旁的删除按钮可以删除整个分类

### 管理分类

- 系统自动根据你添加的 RSS 源创建分类
- 删除分类会同时删除该分类下的所有 RSS 源

---

## 配置保存

- 点击 "保存" 按钮后，配置会保存到 `user_config.json` 文件
- 配置会立即生效，无需重启应用
- 下次启动应用时，会自动加载保存的配置

---

## 配置文件

如果需要手动编辑，配置保存在项目根目录的 `user_config.json` 文件中：

```json
{
  "llm": {
    "api_key": "your-api-key",
    "base_url": "https://api.moonshot.cn/v1",
    "model": "kimi-k2-turbo-preview"
  },
  "rss_sources": {
    "科技新闻": [
      {
        "name": "36氪",
        "url": "https://36kr.com/feed",
        "default_count": 5
      }
    ]
  }
}
```

---

## 配置优先级

系统按以下优先级读取配置：

1. **用户配置文件** (`user_config.json`) - 最高优先级
2. **环境变量** (`.env` 文件或系统环境变量)
3. **默认值** (内置默认配置)

---

## 常见问题

### Q: 配置保存后不生效？
A: 检查 `user_config.json` 文件是否正确生成，如果有错误可以删除该文件重新配置。

### Q: RSS 源添加后获取失败？
A: 请确认 RSS URL 是否正确，可以在浏览器中测试该 URL 是否可访问。

### Q: LLM 配置后仍然使用模拟数据？
A: 请确认 API Key 是否正确，Base URL 和模型名称是否匹配你的 AI 服务。

### Q: 如何重置为默认配置？
A: 删除项目根目录的 `user_config.json` 文件，重启应用即可恢复默认配置。

---

## 示例：添加自定义 RSS 源

假设你想添加 "虎嗅网" 作为科技新闻源：

1. 打开设置页面
2. 填写：
   - 分类名称: `科技新闻`
   - RSS 源名称: `虎嗅网`
   - RSS URL: `https://www.huxiu.com/rss/0.xml`
   - 默认数量: `5`
3. 点击 "添加"
4. 点击 "保存"

现在在主界面选择 "科技新闻" 分类时，就会包含虎嗅网的新闻了。
