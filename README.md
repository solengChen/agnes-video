# Agnes Video 技能 - 安装包

这是一个完整的 Agnes Video 技能安装包，包含所有必要的文件和脚本。

## 📦 包内容

```
agnes-video-skill/
├── SKILL.md                 # 技能定义文件
├── __init__.py             # Python 包初始化
├── video_manager.py         # 统一管理工具（推荐使用）
├── generate_video.py        # 视频生成脚本
├── check_status.py          # 状态查询脚本
├── check_api_key.py         # API Key 检查脚本
├── 安装说明.md              # 中文安装指南
├── README.md               # English installation guide
└── 全局安装.bat            # Windows 一键安装脚本
```

## 🚀 快速安装

### Windows

1. **双击运行 `全局安装.bat`**
   - 自动安装 Agnes CLI
   - 复制所有文件到全局目录
   - 验证安装

2. **或手动安装**
   ```powershell
   # 安装 Agnes CLI
   npm install -g @agnes-ai/agnes-cli
   
   # 复制技能文件到全局目录
   Copy-Item -Path ".trae\skills\agnes-video" -Destination "$env:USERPROFILE\.trae\skills\agnes-video" -Recurse -Force
   ```

### Linux / macOS

```bash
# 安装 Agnes CLI
npm install -g @agnes-ai/agnes-cli

# 复制技能文件到全局目录
mkdir -p ~/.trae/skills/agnes-video
cp -r .trae/skills/agnes-video/* ~/.trae/skills/agnes-video/
```

## 🔑 配置 API Key

### 方法一：使用 Agnes CLI

```bash
# 打开注册页面
agnes key register

# 保存 API Key
agnes key set "您的_API_KEY"

# 验证配置
agnes key status
```

### 方法二：使用环境变量

```bash
# Linux / macOS
export AGNES_API_KEY="您的_API_KEY"

# Windows PowerShell
$env:AGNES_API_KEY = "您的_API_KEY"

# Windows CMD
set AGNES_API_KEY=您的_API_KEY
```

## 🎬 使用方法

### 检查系统状态

```bash
cd ~/.trae/skills/agnes-video
python video_manager.py check
```

### 生成视频

```bash
# 生成 5 秒视频
python video_manager.py generate --prompt "一只猫在海滩上散步" --num-frames 121 --frame-rate 24

# 生成 10 秒视频
python video_manager.py generate --prompt "日落时分的海边风景" --num-frames 241 --frame-rate 24
```

### 查询视频状态

```bash
# 单次查询
python video_manager.py status <video_id>

# 持续查询直到完成
python video_manager.py status <video_id> --poll --interval 5
```

## 📋 帧数约束

⚠️ **重要**：帧数必须是 **16 的倍数 + 1**

有效值：
- 121 帧 ≈ 5 秒
- 241 帧 ≈ 10 秒
- 361 帧 ≈ 15 秒

## 📝 返回信息

视频生成成功后，会返回完整的 JSON 信息：

```json
{
  "success": true,
  "video_id": "vid_xxx",
  "task_id": "task_xxx",
  "status": "completed",
  "video_url": "https://example.com/video.mp4",
  "parameters": {
    "num_frames": 121,
    "frame_rate": 24,
    "duration": 5.04
  }
}
```

## 🔗 获取 API Key

1. 访问 https://agnes-ai.com
2. 注册账号并登录
3. 在个人中心申请 API Key

## 📚 更多信息

- **Agnes 平台**：https://agnes-ai.com
- **API 文档**：https://agnes-ai.com/doc/agnes-video-v20
- **CLI 工具**：https://www.npmjs.com/package/@agnes-ai/agnes-cli

## ❓ 常见问题

### Q: 为什么需要 API Key？

A: Agnes AI 的视频生成服务需要身份验证，API Key 用于标识您的账号和使用配额。

### Q: 视频生成需要多长时间？

A: 通常需要 1-5 分钟，取决于视频复杂度和服务器负载。

### Q: 如何加快生成速度？

A: 使用较少的帧数（121 vs 241），避免高峰期，简化描述词。

---

**版本**: 1.0.0  
**更新日期**: 2026-06-25  
**作者**: AI Assistant
