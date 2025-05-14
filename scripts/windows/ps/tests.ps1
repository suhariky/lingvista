# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # Путь к корню проекта
    $SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName

    # Запуск активации
    & "$SERVICE_ROOT_DIR\scripts\windows\ps\activate.ps1"

    # Запуск сервера
    Write-Host "[tests.ps1] Run Django tests..."
    python "$SERVICE_ROOT_DIR\lingvista\manage.py" test lingvista_web
}
catch {
    Write-Error "[tests.ps1] Error: $_"
    exit 1
}
