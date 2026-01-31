# 创建新的start.bat（用英文避免乱码）
@'
@echo off
echo ========================================
echo   Music Dance System
echo   Developer: Qi Yuqing
echo   Version: 1.0.0
echo ========================================
echo.

echo 1. Check Python...
python --version
if errorlevel 1 (
    echo Error: Python not installed!
    pause
    exit
)

echo.
echo 2. Install dependencies...
if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo Warning: requirements.txt not found!
    echo Installing basic dependencies...
    pip install Flask==2.3.3 Flask-CORS==4.0.0 librosa==0.10.1
)

echo.
echo 3. Create necessary folders...
if not exist "data\music" mkdir data\music
if not exist "data\outputs" mkdir data\outputs

echo.
echo 4. Start system...
echo Please visit: http://localhost:5000
echo Press Ctrl+C to stop
echo ========================================
echo.

python run.py
pause
'@ | Out-File -FilePath "start.bat" -Encoding ASCII