# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # Путь к корню проекта
    $SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName

    # Запуск активации
    & "$SERVICE_ROOT_DIR\scripts\windows\ps\activate.ps1"

    # Запуск сервера
    Write-Host "[coverage.ps1] Run tests coverage..."
    coverage run --omit="*/migrations/*,*/__init__.py" "$SERVICE_ROOT_DIR\lingvista\manage.py" test lingvista_web
    coverage report --fail-under=70
}
catch {
    Write-Error "[coverage.ps1] Error: $_"
    exit 1
}
