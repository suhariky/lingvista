# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # Путь к корню проекта
    $SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName

    # Запуск активации
    & "$SERVICE_ROOT_DIR\scripts\windows\ps\activate.ps1"

    # Установка необходимых модулей
    Write-Host "[install.ps1] Install modules..."
    uv sync --active

    # Обновление pip
    Write-Host "[install.ps1] Upgrade pip..."
    pip install --upgrade pip
}
catch {
    Write-Error "[install.ps1] Error: $_"
    exit 1
}
