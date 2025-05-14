@echo off
SETLOCAL

:: Получаем директорию, где находится скрипт
set "SCRIPT_DIR=%~dp0"

:: Формируем полный путь к PS-скрипту
set "PS_SCRIPT=%SCRIPT_DIR%ps\coverage.ps1"

:: Проверяем, существует ли файл
if not exist "%PS_SCRIPT%" (
    echo Error, file not found: %PS_SCRIPT%
    pause
    exit /b 1
)

:: Запускаем PowerShell-скрипт
powershell -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
