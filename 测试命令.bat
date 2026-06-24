@echo off
chcp 65001 > nul
echo ========================================
echo   Agnes Video 技能测试
echo ========================================
echo.

:: 检查配置
echo [1/3] 检查系统配置...
python video_manager.py check
echo.

:: 提示用户配置 API Key
echo [2/3] API Key 配置说明...
echo.
echo 如果尚未配置 API Key，请：
echo 1. 访问 https://agnes-ai.com 注册并获取 API Key
echo 2. 运行: agnes key set "您的_API_KEY"
echo 3. 验证: agnes key status
echo.

:: 示例命令
echo [3/3] 示例命令：
echo.
echo 生成 5 秒视频：
echo   python video_manager.py generate --prompt "一只猫在海滩上散步" --num-frames 121 --frame-rate 24
echo.
echo 查询状态：
echo   python video_manager.py status <video_id>
echo.
echo 持续查询直到完成：
echo   python video_manager.py status <video_id> --poll --interval 5
echo.

pause
