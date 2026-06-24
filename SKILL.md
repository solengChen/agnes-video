---
name: "agnes-video"
description: "使用 Agnes AI 视频生成服务生成 AI 视频。通过 Agnes CLI 工具调用 Agnes Video V2.0 模型，支持文本生成视频、关键帧动画等。首次使用时会引导用户配置 API Key。生成视频后会返回包含 task_id 和 video_id 的完整响应信息，并提供视频链接查看。"
---

# Agnes Video 技能

使用 Agnes AI 的 Video V2.0 模型生成高质量 AI 视频。

## 核心功能

- **文本生成视频**：通过文本描述生成视频内容
- **关键帧动画**：支持多张图片作为关键帧生成视频
- **异步任务管理**：创建任务后自动查询生成状态
- **API Key 管理**：首次使用时引导配置 API Key

## 工具脚本

| 脚本 | 功能 |
|------|------|
| `check_api_key.py` | 检查 API Key 配置状态 |
| `generate_video.py` | 创建视频生成任务 |
| `check_status.py` | 查询视频生成状态 |
| `video_manager.py` | 统一管理工具（推荐使用） |

## API Key 配置

### 首次使用

首次调用时，技能会检查 API Key 配置。如果未配置，会引导您：

1. 打开 Agnes 平台申请 API Key：https://agnes-ai.com
2. 或者运行命令：`agnes key register`
3. 保存 API Key：`agnes key set "您的_API_KEY"`
4. 验证配置：`agnes key status`

### API Key 来源优先级

1. 命令行 `--api-key` 参数
2. 环境变量 `AGNES_API_KEY`
3. 本地保存的 Key（`agnes key set`）

## 使用方法

### 方式一：使用 video_manager（推荐）

```bash
python .trae/skills/agnes-video/video_manager.py generate \
  --prompt "视频描述文本" \
  --num-frames 121 \
  --frame-rate 24
```

### 方式二：分步操作

```bash
# 1. 创建视频任务
python .trae/skills/agnes-video/generate_video.py \
  --prompt "视频描述" \
  --num-frames 121 \
  --frame-rate 24

# 2. 查询任务状态（使用返回的 video_id）
python .trae/skills/agnes-video/check_status.py <video_id>
```

### 方式三：使用 Agnes CLI

```bash
# 生成视频
agnes video generate \
  --prompt "A cat walking on the beach at sunset" \
  --num-frames 121 \
  --frame-rate 24

# 查询状态
agnes video status <video_id_or_task_id>
```

## 参数说明

### 必需参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--prompt` | 视频内容描述 | "一个女孩在海边跳舞" |

### 可选参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--num-frames` | 121 | 视频帧数（必须是 16 的倍数 + 1） |
| `--frame-rate` | 24 | 帧率（fps） |
| `--mode` | normal | 生成模式：`normal` 或 `keyframes` |
| `--image` | - | 关键帧图片路径（keyframes 模式） |
| `--duration` | - | 视频时长（秒），自动计算帧数 |

### 帧数约束（重要！）

```
num_frames 必须是 16 的倍数 + 1
有效值：1, 17, 33, 49, 65, 81, 97, 113, 121, ...
```

### 视频时长计算

```
视频时长 = num_frames / frame_rate
示例：121帧 / 24fps ≈ 5秒
```

## 工作流程

### 标准流程

```
1. 技能启动 → 检查 API Key 配置
2. 接收用户需求 → 解析视频生成参数
3. 创建视频任务 → 获取 task_id 和 video_id
4. 查询生成状态 → 等待视频生成完成
5. 返回完整结果 → 提供视频链接和详细信息
```

### 异步任务说明

Agnes Video 采用异步生成模式：
1. 提交生成请求 → 立即返回 task_id 和 video_id
2. 后台生成视频 → 需要轮询查询状态
3. 生成完成 → 提供视频链接

## 关键帧模式

使用多张图片作为关键帧生成过渡视频：

```bash
agnes video generate \
  --prompt "Smooth transition between keyframes" \
  --image ./start.png \
  --image ./end.png \
  --mode keyframes
```

## 输出格式

### 成功响应

```json
{
  "success": true,
  "video_id": "vid_xxx",
  "task_id": "task_xxx",
  "status": "pending|processing|completed|failed",
  "video_url": "https://example.com/video.mp4",
  "metadata": {
    "num_frames": 121,
    "frame_rate": 24,
    "duration": 5.04,
    "created_at": "2026-06-25T10:30:00Z"
  }
}
```

### 任务状态

| 状态 | 说明 |
|------|------|
| `pending` | 任务已提交，等待处理 |
| `processing` | 正在生成视频 |
| `completed` | 视频生成完成 |
| `failed` | 生成失败 |

## 视频链接说明

视频生成完成后，您可以通过返回的 `video_url` 直接在线查看视频。**本技能不会自动下载视频文件**，仅提供视频链接供您查看或手动下载。

## 示例

### 生成 5 秒视频

```bash
python .trae/skills/agnes-video/video_manager.py generate \
  --prompt "A beautiful woman dancing on a sandy beach at sunset" \
  --num-frames 121 \
  --frame-rate 24
```

### 生成 10 秒视频

```bash
python .trae/skills/agnes-video/video_manager.py generate \
  --prompt "A group of friends playing volleyball on the beach" \
  --num-frames 241 \
  --frame-rate 24
```

### 关键帧动画

```bash
python .trae/skills/agnes-video/video_manager.py generate \
  --prompt "Transition from day to night" \
  --image ./day_scene.png \
  --image ./night_scene.png \
  --mode keyframes
```

## 错误处理

### API Key 未配置

```
错误：未检测到 API Key 配置
解决：请先配置 API Key
1. 访问 https://agnes-ai.com 注册账号
2. 申请 API Key
3. 保存：agnes key set "您的_API_KEY"
```

### 帧数不符合要求

```
错误：num_frames 必须是 16 的倍数 + 1
示例有效值：121, 241, 361, ...
当前值：120（无效）
建议：使用 121 或 241
```

### 网络请求失败

```
错误：无法连接到 Agnes AI 服务
检查：
1. 网络连接是否正常
2. API Key 是否有效
3. 服务是否可用
```

## 资源链接

- **Agnes 平台**：https://agnes-ai.com
- **API 文档**：https://agnes-ai.com/doc/agnes-video-v20
- **CLI 工具**：@agnes-ai/agnes-cli
- **问题反馈**：https://github.com/Constantine1916/agnes-cli

## 最佳实践

1. **视频描述**：使用具体、详细的描述有助于生成更好的视频
2. **帧数选择**：5-10 秒视频通常 121-241 帧足够
3. **轮询频率**：建议间隔 5-10 秒查询一次状态
4. **并发任务**：可以同时提交多个生成任务
5. **API Key 安全**：不要在代码中硬编码 API Key，使用环境变量或 `agnes key set`
