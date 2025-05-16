# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # Путь к корню проекта
    $SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName

    cd $SERVICE_ROOT_DIR

    # Запуск активации
    & "$SERVICE_ROOT_DIR\scripts\windows\ps\activate.ps1"

    # Запуск сервера
    Write-Host "[pylint.ps1] Check Pylint..."
    pylint lingvista --disable=C0114,R0903,E1101,W1203 --max-line-length=120 --fail-under=8 --ignore=migrations
}
catch {
    Write-Error "[pylint.ps1] Error: $_"
    exit 1
}
