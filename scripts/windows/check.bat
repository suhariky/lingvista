@echo off
SETLOCAL EnableDelayedExpansion

:: Получаем директорию, где находится скрипт
set "SCRIPT_DIR=%~dp0"

:: Формируем полный путь к PS-скрипту
set "PS_SCRIPT=%SCRIPT_DIR%ps\check.ps1"

:: Проверяем, существует ли файл
if not exist "%PS_SCRIPT%" (
    echo Error: PowerShell script not found: %PS_SCRIPT%
    pause
    exit /b 1
)

:: По умолчанию все флаги выключены
set Fix=false
set FixBlack=false
set FixIsort=false
set FixRuff=false
set Verbose=false
set Help=false

:: Преобразуем числовые флаги в строковые значения "true"/"false"
for %%A in (%*) do (
    if "%%A"=="--Fix" set Fix=true
    if "%%A"=="-Fix" set Fix=true
    if "%%A"=="--FixBlack" set FixBlack=true
    if "%%A"=="-FixBlack" set FixBlack=true
    if "%%A"=="--FixIsort" set FixIsort=true
    if "%%A"=="-FixIsort" set FixIsort=true
    if "%%A"=="--FixRuff" set FixRuff=true
    if "%%A"=="-FixRuff" set FixRuff=true
    if "%%A"=="--Verbose" set Verbose=true
    if "%%A"=="-Verbose" set Verbose=true
    if "%%A"=="--Help" set Help=true
    if "%%A"=="-Help" set Help=true
)

:: Собираем активные флаги в одну переменную
set "args="

if "!Fix!"=="true" set "args=!args! -Fix"
if "!FixBlack!"=="true" set "args=!args! -FixBlack"
if "!FixIsort!"=="true" set "args=!args! -FixIsort"
if "!FixRuff!"=="true" set "args=!args! -FixRuff"
if "!Verbose!"=="true" set "args=!args! -Verbose"
if "!Help!"=="true" set "args=!args! -Help"

:: Удаляем возможный пробел в начале строки
if defined args set "args=!args:~1!"

:: Запускаем PowerShell-скрипт
if defined args (
    powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "& { . '%PS_SCRIPT%'  !args! }"
) else (
    powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "& { . '%PS_SCRIPT%' }"
)

:: Возвращаем код завершения
exit /b %ERRORLEVEL%
