@echo off
echo ========================================
echo   ????????????
echo   ???????
echo   ???1.0.0
echo ========================================
echo.

echo 1. ??Python...
python --version
if errorlevel 1 (
    echo ???Python????
    pause
    exit
)

echo.
echo 2. ????...
pip install -r requirements.txt

echo.
echo 3. ???????...
if not exist "data\music" mkdir data\music
if not exist "data\outputs" mkdir data\outputs

echo.
echo 4. ????...
echo ????????http://localhost:5000
echo ? Ctrl+C ??
echo ========================================
echo.

python run.py
pause
