@echo off
echo Searching for the scripts directory and moving up...

:: Get the directory where the script is located
set "SCRIPT_DIR=%~dp0"

:: Move one level up (where requirements.txt is located)
cd /d "%SCRIPT_DIR%.."

:: Run server
lingvista\manage.py runserver