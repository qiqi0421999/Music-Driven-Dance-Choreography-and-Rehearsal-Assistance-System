@echo off
chcp 65001 > nul
cls

echo ========================================
echo   音乐舞蹈系统启动器
echo   开发者：Qi Yuqing
echo ========================================
echo.

echo 注意：由于网络限制，无法自动安装依赖
echo.
echo 请确保已安装以下Python包：
echo 1. Flask
echo 2. numpy
echo 3. librosa
echo.
echo 如果未安装，请在有网络的电脑运行：
echo pip install Flask numpy librosa
echo.
echo 按任意键尝试启动系统...
pause > nul

echo.
echo 正在启动音乐舞蹈系统...
echo 访问：http://localhost:5000
echo.
python run.py
pause