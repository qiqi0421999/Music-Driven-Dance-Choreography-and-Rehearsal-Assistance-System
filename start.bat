@echo off
chcp 65001 > nul
cls

echo ========================================
echo   音乐舞蹈系统 - 无代理版本
echo   （已关闭代理）
echo ========================================
echo.

echo [1/4] 清除代理设置...
set HTTP_PROXY=
set HTTPS_PROXY=
set http_proxy=
set https_proxy=
echo ✅ 代理环境变量已清除

echo.
echo [2/4] 检查Python环境...
python --version 2>nul
if errorlevel 1 (
    echo ❌ Python未安装！
    echo 请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python检查通过

echo.
echo [3/4] 安装依赖（使用国内镜像源）...
echo 正在安装，请稍等...
pip install Flask==2.3.3 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
pip install numpy==1.24.3 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
pip install librosa==0.10.1 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
pip install soundfile==0.12.1 -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn
echo ✅ 核心依赖安装完成

echo.
echo [4/4] 创建目录并启动...
mkdir data 2>nul
mkdir data\music 2>nul
mkdir data\outputs 2>nul

echo.
echo ========================================
echo 🎉 系统启动成功！
echo 📍 请访问：http://localhost:5000
echo 🛑 按 Ctrl+C 停止程序
echo ========================================
echo.

python run.py
pause