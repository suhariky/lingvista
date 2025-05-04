# Устанавливаем UTF-8 для корректного вывода
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

# Путь к корню проекта (теперь считаем от расположения activate.ps1)
$SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName
$VENV_PATH = Join-Path $SERVICE_ROOT_DIR "venv"

# Проверка существования venv
if (-not (Test-Path "$VENV_PATH\Scripts\Activate.ps1")) {
    Write-Error "[activate.ps1] Virtual environment not found in $VENV_PATH"
    exit 1
}

# Активация venv с проверкой успешности
& "$VENV_PATH\Scripts\Activate.ps1"
if (-not $env:VIRTUAL_ENV) {
    Write-Error "[activate.ps1] Failed to activate the environment"
    exit 1
}

Write-Host "[activate.ps1] The environment is activated: $env:VIRTUAL_ENV"