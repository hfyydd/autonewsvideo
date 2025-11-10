# 切换到 Kimi API - 完成说明

## ✅ 已完成的更改

### 1. 更新了配置文件 (`config.py`)

- 默认 API 切换为 **Kimi (Moonshot AI)**
- Base URL: `https://api.moonshot.cn/v1`
- 默认模型: `moonshot-v1-8k`
- 支持多种环境变量配置方式

### 2. 环境变量优先级

```bash
# 方式1：直接使用 Kimi 专用变量（推荐）
export KIMI_API_KEY="sk-xxx"

# 方式2：使用通用变量
export AI_API_KEY="sk-xxx"
export AI_BASE_URL="https://api.moonshot.cn/v1"
export AI_MODEL="moonshot-v1-8k"
```

### 3. 向后兼容

保留了旧的 `QWEN_API_KEY` 变量作为别名，不会破坏现有配置。

## 🚀 如何使用

### 获取 Kimi API Key

1. 访问 [Moonshot AI 开放平台](https://platform.moonshot.cn/)
2. 注册账号（支持微信/手机号）
3. 进入控制台 → API Keys
4. 创建新的 API Key
5. 复制 Key（格式：`sk-xxxxx`）

### 配置 API Key

**方式1：使用环境变量**（推荐）

```bash
export KIMI_API_KEY="sk-your-key-here"
uv run main.py
```

**方式2：使用 .env 文件**

```bash
# 复制示例文件
cp .env.example .env

# 编辑 .env 文件，填入你的 API Key
# KIMI_API_KEY=sk-your-key-here

# 运行应用
uv run main.py
```

**方式3：直接修改 config.py**（不推荐）

在 `config.py` 文件中修改：

```python
AI_API_KEY = "sk-your-key-here"
```

## 🔄 切换到其他 AI 服务

### 切换到通义千问

```bash
export AI_API_KEY="your-qwen-key"
export AI_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export AI_MODEL="qwen-plus"
```

### 切换到 OpenAI

```bash
export AI_API_KEY="sk-your-openai-key"
export AI_BASE_URL="https://api.openai.com/v1"
export AI_MODEL="gpt-4"
```

### 切换到 DeepSeek

```bash
export AI_API_KEY="your-deepseek-key"
export AI_BASE_URL="https://api.deepseek.com/v1"
export AI_MODEL="deepseek-chat"
```

## 📝 Kimi API 特点

- ✅ **长文本支持**: moonshot-v1-8k 支持 8K tokens
- ✅ **中文优化**: 针对中文场景优化
- ✅ **价格实惠**: 相比 OpenAI 更便宜
- ✅ **国内访问**: 无需科学上网
- ✅ **OpenAI 兼容**: 使用标准 OpenAI SDK

## 🎯 推荐配置

对于新闻视频生成，推荐以下配置：

```python
# config.py
AI_BASE_URL = "https://api.moonshot.cn/v1"
AI_MODEL = "moonshot-v1-8k"  # 适合新闻文案生成
```

如果需要处理更长的新闻，可以选择：
- `moonshot-v1-32k` - 支持 32K tokens
- `moonshot-v1-128k` - 支持 128K tokens

## ⚠️ 注意事项

1. **API Key 安全**: 不要将 API Key 提交到 Git
2. **费用控制**: 建议在 Kimi 控制台设置用量限制
3. **备用方案**: 即使不配置 API Key，程序也能运行（使用简单文本处理）

## ✨ 测试配置

运行测试确认配置正确：

```bash
# 测试 API 配置
uv run python -c "import config; print(f'Base URL: {config.AI_BASE_URL}'); print(f'Model: {config.AI_MODEL}')"

# 测试完整功能
uv run python test_basic.py
```

## 📚 相关文档

- Kimi API 文档: https://platform.moonshot.cn/docs
- OpenAI API 兼容性: https://platform.moonshot.cn/docs/api-reference
- 定价信息: https://platform.moonshot.cn/pricing
