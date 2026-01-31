@echo off
echo ========================================
echo   音乐驱动舞蹈辅助排演系统
echo   开发者：齐雨晴
echo   版本：1.0.0
echo ========================================
echo.

echo 1. 检查Python...
python --version
if errorlevel 1 (
    echo 错误：Python未安装！
    pause
    exit
)

echo.
echo 2. 安装依赖...
pip install -r requirements.txt

echo.
echo 3. 创建必要文件夹...
if not exist "data\music" mkdir data\music
if not exist "data\outputs" mkdir data\outputs

echo.
echo 4. 启动系统...
echo 请在浏览器访问：http://localhost:5000
echo 按 Ctrl+C 停止
echo ========================================
echo.

python run.py
pause