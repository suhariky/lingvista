# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # Путь к корню проекта
    $SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName
    cd "$SERVICE_ROOT_DIR"

    # Запуск активации
    & "$SERVICE_ROOT_DIR\scripts\windows\ps\activate.ps1"

    # Запуск сервера
    Write-Host "[create_docs.ps1] Creating documentation into target..."
    # Запускаем генерацию документации в папку target
    mkdocs build --site-dir "$SERVICE_ROOT_DIR\target"
}
catch {
    Write-Error "[create_docs.ps1] Error: $_"
    exit 1
}
