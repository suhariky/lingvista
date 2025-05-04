# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # Путь к корню проекта
    $SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName

    # Запуск активации
    & "$SERVICE_ROOT_DIR\scripts\windows\ps\activate.ps1"

    # Запуск сервера
    Write-Host "[run.ps1] Run Django server..."
    python "$SERVICE_ROOT_DIR\lingvista\manage.py" runserver
}
catch {
    Write-Error "[run.ps1] Error: $_"
    exit 1
}