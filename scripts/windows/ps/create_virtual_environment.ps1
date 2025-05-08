# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

try {
    # Переходим в корневую директорию
    $SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName
    Set-Location $SERVICE_ROOT_DIR

    # Параметры скрипта
    $PROJECT = "lingvista"
    $VENV_PATH = Join-Path $SERVICE_ROOT_DIR "venv"
    $PYTHON_VERSION = "3.11.4"

    # Проверка, установлена ли uv
    if (-not (Get-Command "uv" -ErrorAction SilentlyContinue)) {
        Write-Host "[create_virtual_environment.ps1] Environment installation is not possible, install uv first: .\scripts\windows\install-third-party.bat"
        exit 1
    }

    # Проверка существования каталога виртуального окружения
    if (Test-Path "$VENV_PATH\Scripts\Activate.ps1") {
        Write-Host "[create_virtual_environment.ps1] The virtual environment was found on the way: $VENV_PATH"

        # Активируем окружение и получаем версию Python
        $activateScript = "$VENV_PATH\Scripts\Activate.ps1"
        $pythonVersion = & {
            & $activateScript *>&1 | Out-Null
            $versionOutput = python --version 2>&1
            if ($versionOutput -match "Python (\d+\.\d+\.\d+)") {
                $matches[1]
            }
            deactivate *>&1 | Out-Null
        }

        # Проверка версии Python
        if ($pythonVersion -eq $PYTHON_VERSION) {
            Write-Host "[create_virtual_environment.ps1] A virtual environment with Python ${pythonVersion} has been found and is suitable for operation."
        }
        else {
            Write-Host "[create_virtual_environment.ps1] Virtual environment found, but created using Python: $pythonVersion`nexpected Python: $PYTHON_VERSION`nDelete the created virtual environment: $VENV_PATH"
            exit 1
        }
    }
    else {
        # Создание виртуального окружения
        Write-Host "[create_virtual_environment.ps1] Creating a new virtual environment ${PROJECT} with Python ${PYTHON_VERSION}..."
        uv venv --seed --prompt "${PROJECT}" -p "${PYTHON_VERSION}" "${VENV_PATH}"

        if (-not $?) {
            Write-Host "[create_virtual_environment.ps1] Couldn't create a virtual environment."
            exit 1
        }
    }
}
catch {
    Write-Host "[create_virtual_environment.ps1] Error: $_"
    exit 1
}
