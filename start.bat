@echo off
chcp 65001 > nul
echo ========================================
echo   音乐驱动舞蹈辅助排演系统
echo   Music-Driven Dance Rehearsal System
echo ========================================
echo.
echo 正在检查环境...
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Python！
    echo 请安装Python 3.8或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python检查通过
echo.

REM 检查并安装依赖
echo 正在检查依赖包...
if exist requirements.txt (
    echo 安装依赖包...
    pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
) else (
    echo 错误：找不到requirements.txt
    pause
    exit /b 1
)

echo.
echo 正在创建必要目录...
if not exist "data\music" mkdir data\music
if not exist "data\outputs" mkdir data\outputs

echo.
echo ========================================
echo 启动成功！
echo 请打开浏览器访问：http://localhost:5000
echo 按 Ctrl+C 停止程序
echo ========================================
echo.
python run.py
pause