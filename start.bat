@echo off
chcp 65001 > nul
title 音乐舞蹈系统启动器
color 0A

echo ========================================
echo   音乐驱动舞蹈辅助排演系统
echo   Music-Driven Dance Rehearsal System
echo   开发者：Qi Yuqing
echo ========================================
echo.

echo [1/4] 检查Python环境...
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python！
    echo.
    echo 解决方案：
    echo 1. 请从 https://www.python.org/downloads/ 下载Python
    echo 2. 安装时务必勾选"Add Python to PATH"
    echo.
    pause
    exit /b 1
)

python --version
echo ✅ Python检查通过
echo.

echo [2/4] 检查依赖文件...
if not exist "requirements.txt" (
    echo ⚠️ 未找到requirements.txt，正在创建...
    (
echo Flask==2.3.3
echo Flask-CORS==4.0.0
echo numpy==1.24.3
echo pandas==2.0.3
echo librosa==0.10.1
echo soundfile==0.12.1
echo moviepy==1.0.3
echo matplotlib==3.7.2
echo opencv-python==4.8.0.76
echo Pillow==10.0.0
echo scipy==1.11.1
echo scikit-learn==1.3.0
echo pydub==0.25.1
    ) > requirements.txt
    echo ✅ 已创建requirements.txt
)

echo [3/4] 安装依赖包...
echo 正在安装，这可能需要几分钟...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --user
if errorlevel 1 (
    echo ⚠️ 依赖安装遇到问题，尝试简化安装...
    echo.
    echo 正在安装核心依赖...
    pip install Flask numpy librosa soundfile matplotlib opencv-python -i https://pypi.tuna.tsinghua.edu.cn/simple --user
)

echo ✅ 依赖安装完成
echo.

echo [4/4] 创建项目目录...
if not exist "data" mkdir data
if not exist "data\music" mkdir data\music
if not exist "data\outputs" mkdir data\outputs
if not exist "static" mkdir static
if not exist "static\css" mkdir static\css
if not exist "static\js" mkdir static\js
if not exist "templates" mkdir templates
if not exist "models" mkdir models
if not exist "utils" mkdir utils
echo ✅ 目录结构创建完成
echo.

echo ========================================
echo 🎉 环境准备完成！
echo.
echo 📍 重要文件检查：
if exist "run.py" (
    echo ✅ run.py  - 存在
) else (
    echo ❌ run.py  - 缺失
)
if exist "app.py" (
    echo ✅ app.py  - 存在
) else (
    echo ❌ app.py  - 缺失
)
if exist "config.py" (
    echo ✅ config.py  - 存在
) else (
    echo ❌ config.py  - 缺失
)
if exist "models\music_processor.py" (
    echo ✅ music_processor.py - 存在
) else (
    echo ⚠️  music_processor.py - 缺失（部分功能可能受限）
)
echo.
echo 🚀 正在启动系统...
echo 📍 请打开浏览器访问：http://localhost:5000
echo 🛑 按 Ctrl+C 停止程序
echo ========================================
echo.

timeout /t 3 /nobreak > nul

REM 检查并启动系统
if exist "run.py" (
    python run.py
) else if exist "app.py" (
    python app.py
) else (
    echo ❌ 错误：找不到启动文件！
    echo 请确保run.py或app.py存在
    pause
)

pause