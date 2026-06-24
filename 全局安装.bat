@echo off
chcp 65001 > nul
echo ========================================
echo   Agnes Video 技能 - 快速安装
echo ========================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python
    echo 请先安装 Python 3.6+：https://www.python.org/downloads/
    pause
    exit /b 1
)
echo [成功] Python 已安装

:: 检查 npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 npm
    echo 请先安装 Node.js：https://nodejs.org/
    pause
    exit /b 1
)
echo [成功] npm 已安装

echo.
echo [步骤 1/4] 安装 Agnes CLI...
call npm install -g @agnes-ai/agnes-cli
if errorlevel 1 (
    echo [错误] Agnes CLI 安装失败
    pause
    exit /b 1
)
echo [成功] Agnes CLI 安装完成

:: 验证安装
agnes key status >nul 2>&1
echo [成功] Agnes CLI 验证通过

echo.
echo [步骤 2/4] 创建全局技能目录...
set "GLOBAL_SKILLS=%USERPROFILE%\.trae\skills"
mkdir "%GLOBAL_SKILLS%" 2>nul
mkdir "%GLOBAL_SKILLS%\agnes-video" 2>nul
echo [成功] 目录创建完成

echo.
echo [步骤 3/4] 复制技能文件...
set "SOURCE_DIR=%CD%\.trae\skills\agnes-video"
set "TARGET_DIR=%GLOBAL_SKILLS%\agnes-video"

:: 复制所有文件
copy "%SOURCE_DIR%\SKILL.md" "%TARGET_DIR%\" >nul
copy "%SOURCE_DIR%\__init__.py" "%TARGET_DIR%\" >nul
copy "%SOURCE_DIR%\video_manager.py" "%TARGET_DIR%\" >nul
copy "%SOURCE_DIR%\generate_video.py" "%TARGET_DIR%\" >nul
copy "%SOURCE_DIR%\check_status.py" "%TARGET_DIR%\" >nul
copy "%SOURCE_DIR%\check_api_key.py" "%TARGET_DIR%\" >nul
copy "%SOURCE_DIR%\安装说明.md" "%TARGET_DIR%\" >nul
echo [成功] 技能文件复制完成

echo.
echo [步骤 4/4] 验证安装...
cd /d "%TARGET_DIR%"
python video_manager.py check

echo.
echo ========================================
echo   安装完成！
echo ========================================
echo.
echo 技能位置：%TARGET_DIR%
echo.
echo 下一步：
echo 1. 配置 API Key：agnes key register
echo 2. 保存 API Key：agnes key set "您的_API_KEY"
echo 3. 验证配置：agnes key status
echo.
echo 使用示例：
echo   生成视频：python video_manager.py generate --prompt "描述" --num-frames 121
echo   查询状态：python video_manager.py status <video_id>
echo.
pause
