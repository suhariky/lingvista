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
    Write-Host "[pycodestyle.ps1] Check pycodestyle..."
    pycodestyle lingvista --max-line-length=120 --exclude=migrations --ignore=E701
}
catch {
    Write-Error "[pycodestyle.ps1] Error: $_"
    exit 1
}
