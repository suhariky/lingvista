@echo off
echo Searching for the scripts directory and requirements.txt...

:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"

:: Move one level up (where requirements.txt is located)
cd /d "%SCRIPT_DIR%.."

:: Check if requirements.txt exists
if not exist requirements.txt (
    echo File requirements.txt not found!
    pause
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo Dependencies installed successfully!
) else (
    echo An error occurred while installing dependencies.
)

pause