@echo off
setlocal enabledelayedexpansion

echo ========================================
echo  Daily Logbook - EXE Builder
echo ========================================
echo.

REM Check if PyInstaller is installed
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    pip install pyinstaller
    echo.
)

echo Building Daily Logbook.exe...
echo This may take a minute...
echo.

pyinstaller --onefile --windowed --name "Daily Logbook" --hidden-import=tkcalendar main.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build Successful!
echo ========================================
echo.
echo Your executable is located at:
echo %cd%\dist\Daily Logbook.exe
echo.
echo You can now:
echo - Run it directly
echo - Share it with others
echo - Create shortcuts to it
echo.
pause
