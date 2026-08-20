@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo   🐺 Fenrir - Autonomous Dark Web OSINT Setup
echo ===================================================
echo.
echo Installing Fenrir dependencies on Windows...

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python launcher not found. Install Python 3.10+ first.
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo.
echo ---------------------------------------------------
echo  [IMPORTANT] Tor Network Configuration
echo ---------------------------------------------------
echo  Download the Tor Expert Bundle or Tor Browser:
echo  https://www.torproject.org/download/tor/
echo  Ensure tor.exe is running on port 9050 before crawling.
echo ---------------------------------------------------
echo.

echo Creating fenrir.bat CLI launcher...
(
echo @echo off
echo python "%%~dp0main.py" %%*
) > "%~dp0fenrir.bat"
(
echo @echo off
echo python "%%~dp0main.py" %%*
) > "%~dp0deeprecon.bat"

echo.
echo [SUCCESS] Fenrir setup complete!
echo Launch options:
echo   1. Interactive CLI: fenrir --cli   (or python main.py)
echo   2. Web Dashboard:   fenrir --web   (or python main.py --web)
echo.
pause
