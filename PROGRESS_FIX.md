# 视频合成进度条修复说明

## 问题描述

在视频合成阶段，界面上看不到进度更新。

## 原因分析

MoviePy 的 `write_videofile()` 方法在执行过程中不提供实时进度回调接口（或者接口在不同版本中不一致）。这导致虽然我们定义了进度回调函数，但在视频导出阶段无法实时更新进度条。

## 解决方案

### 1. 进度模拟器

由于无法获取真实的导出进度，我们使用一个后台线程模拟进度更新：

```python
def simulate_export_progress():
    """模拟导出进度"""
    # 基于视频总时长预估导出时间
    total_duration = sum(news.duration for news in news_list)
    estimated_time = total_duration * 2  # 导出时间约为视频时长的2倍

    # 每秒更新一次进度，使用对数曲线（前期快后期慢）
    while not export_complete.is_set():
        progress_ratio = min(0.95, elapsed / estimated_time)  # 最多到95%
        progress_callback(current_step, total, f"正在导出视频... {percent}%")
        time.sleep(1)
```

### 2. 线程同步

使用 `threading.Event` 来同步主线程和进度模拟线程：

```python
export_complete = threading.Event()

# 启动进度线程
progress_thread = threading.Thread(target=simulate_export_progress, daemon=True)
progress_thread.start()

# 执行导出
try:
    final_clip.write_videofile(...)
finally:
    export_complete.set()  # 通知进度线程停止
```

### 3. 完整的进度流程

现在视频生成的进度显示包括：

1. **语音生成**: 每条新闻完成后更新进度
2. **图片生成**: 每张图片完成后更新进度
3. **视频拼接**: 显示 "正在拼接视频片段..."
4. **视频导出**:
   - 显示 "正在导出视频... X%"
   - 进度从 0% 逐渐增加到 95%
   - 每秒更新一次
5. **完成**: 显示 "视频导出完成！"，进度到 100%

## 技术细节

### 进度估算

导出时间估算公式：
```python
estimated_time = total_video_duration * 2
```

这个系数（2）是经验值，可能因以下因素变化：
- CPU 性能
- 视频编码器设置（preset: ultrafast/fast/medium/slow）
- 视频分辨率和比特率
- 系统负载

### 进度曲线

使用线性进度但限制在 95%，因为：
- 视频编码可能有不可预测的耗时波动
- 保留最后 5% 给收尾工作
- 避免进度条"卡"在 99% 的不良体验

## 修改文件

- `services/video_composer.py` (第 1-192 行)
  - 添加 `threading` 和 `time` 导入
  - 实现 `simulate_export_progress()` 函数
  - 使用 `threading.Event` 控制进度线程

## 测试

运行完整的视频生成流程，观察进度条：

1. 选择新闻并生成文案
2. 点击"开始生成"
3. 观察进度条在各个阶段的更新：
   - 语音生成阶段：实时更新
   - 图片生成阶段：实时更新
   - 视频导出阶段：每秒更新，显示百分比

## 优化建议

未来可以考虑的改进：

1. **更精确的时间估算**：
   - 记录历史导出时间，使用机器学习预测
   - 考虑视频长度、分辨率等因素

2. **真实进度追踪**：
   - 监控输出文件大小变化
   - 使用 ffmpeg 的进度输出（如果 MoviePy 暴露了接口）

3. **用户反馈**：
   - 添加"取消导出"按钮
   - 显示预估剩余时间
