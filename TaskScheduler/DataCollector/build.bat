@echo off
REM =====================================================================
REM  DataCollector — Standalone Windows Executable Build Script (Batch)
REM =====================================================================

set SCRIPT_DIR=%~dp0
set SRC_DIR=%SCRIPT_DIR%src
set DIST_DIR=%SCRIPT_DIR%dist

echo.
echo =====================================================================
echo  AI TASK SCHEDULER: DATA COLLECTOR — WINDOWS BUILD
echo =====================================================================
echo.

echo [1/3] Installing/verifying build dependencies...
python -m pip install --upgrade pip
pip install pyinstaller customtkinter pystray pillow darkdetect

echo.
echo [2/3] Running automated unit test suite...
python -m unittest discover -s "%SCRIPT_DIR%tests" -p "test_*.py" -v
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Unit tests failed. Aborting build.
    exit /b %ERRORLEVEL%
)

echo.
echo [3/3] Compiling DataCollector.exe via PyInstaller...
pyinstaller ^
    --noconfirm ^
    --onefile ^
    --windowed ^
    --name DataCollector ^
    --distpath "%DIST_DIR%" ^
    --workpath "%SCRIPT_DIR%.build_work" ^
    --specpath "%SCRIPT_DIR%" ^
    --paths "%SRC_DIR%" ^
    --add-data "%SRC_DIR%/schema.json;." ^
    --add-data "%SRC_DIR%/db_schema.sql;." ^
    "%SRC_DIR%/main.py"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo  BUILD SUCCESSFUL!
    echo  Standalone Windows Executable: %DIST_DIR%\DataCollector.exe
    echo =====================================================================
) else (
    echo [ERROR] PyInstaller compilation failed.
    exit /b %ERRORLEVEL%
)
