<#
.SYNOPSIS
Скрипт для проверки стиля кода с использованием black, isort и ruff
#>

param (
    [switch]$Fix,
    [switch]$FixBlack,
    [switch]$FixIsort,
    [switch]$FixRuff,
    [switch]$Verbose,
    [switch]$Help
)

# Настройка кодировки
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

function Show-Help {
    @"
Usage: check.ps1 [options]

Options:
  -Fix          Automatically fix all found problems
  -FixBlack     Automatically fix found problems black
  -FixIsort     Automatically fix found problems isort
  -FixRuff      Automatically fix the found problems ruff
  -Verbose      Detailed output
  -Help         Show this message and exit

Examples:
  # Verification with detailed
  check output.bat -Verbose

  # Auto-fix all problems
  check.bat -Fix

  # Automatic Black correction with detailed
  check output.bat -FixBlack -Verbose
"@
}

# Показать помощь и выйти если запрошено
if ($Help) {
    Show-Help
    exit 0
}

# Корень репозитория
$SERVICE_ROOT_DIR = (Get-Item $PSScriptRoot).Parent.Parent.Parent.FullName
$PROJECT_ROOT = if ($env:PROJECT_ROOT) { $env:PROJECT_ROOT } else { $SERVICE_ROOT_DIR }

# Функция для вывода verbose сообщений
function Log {
    param([string]$Message)
    if ($Verbose) {
        Write-Host "[check.ps1] $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $Message"
    }
}

# Глобальные переменные для хранения ошибок
$script:Errors = @()
$script:HasErrors = $false

# Активация виртуального окружения
Log "Activating the virtual environment..."
try {
    & "$SERVICE_ROOT_DIR\scripts\windows\ps\activate.ps1"
    if (-not $?) {
        Write-Error "[check.ps1] Error: The virtual environment could not be activated."
        exit 1
    }
}
catch {
    Write-Error "[check.ps1] Virtual environment activation error: $_"
    exit 1
}

# Проверка black
function Run-Black {
    $config = "$SERVICE_ROOT_DIR\pyproject.toml"

    Write-Host "=== Check black ==="

    if ($Fix -or $FixBlack) {
        Log "Auto-correction..."
        & black "--config" "$config" "$PROJECT_ROOT"
    }
    else {
        try {
            & black "--config" "$config" "--check" "$PROJECT_ROOT"
            if (-not $?) {
                $script:Errors += "black: Style inconsistencies found (run with -FixBlack to fix)"
                $script:HasErrors = $true
            }
            else {
                Write-Host "[check.ps1] black: verification passed"
            }
        }
        catch {
            $script:Errors += "black: Style inconsistencies found (run with -FixBlack to fix)"
            $script:HasErrors = $true
        }
    }
}

# Проверка isort
function Run-Isort {
    $config = "$SERVICE_ROOT_DIR\pyproject.toml"

    Write-Host "=== Check isort ==="

    if ($Fix -or $FixIsort) {
        Log "Auto-correction..."
        & isort "--settings-path" "$config" "$PROJECT_ROOT"
    }
    else {
        try {
            & isort "--settings-path" "$config" "--check-only" "$PROJECT_ROOT"
            if (-not $?) {
                $script:Errors += "isort: Unsorted imports found (run with -FixIsort to fix)"
                $script:HasErrors = $true
            }
            else {
                Write-Host "[check.ps1] isort: verification passed"
            }
        }
        catch {
            $script:Errors += "isort: Unsorted imports found (run with -FixIsort to fix)"
            $script:HasErrors = $true
        }
    }
}

# Проверка ruff
function Run-Ruff {
    $config = "$SERVICE_ROOT_DIR\pyproject.toml"

    Write-Host "=== Check ruff ==="

    if ($Fix -or $FixRuff) {
        Log "Auto-correction..."
            & ruff "--config" "$config" "check" "--fix" "$PROJECT_ROOT"
        if (-not $?) {
            $script:Errors += "ruff: Problems have been found that require manual correction"
            $script:HasErrors = $true
        }
    }
    else {
        try {
            & ruff "--config" "$config" "check" "$PROJECT_ROOT"
            if (-not $?) {
                $script:Errors += "ruff: Problems have been found that require manual correction"
                $script:HasErrors = $true
            }
            else {
                Write-Host "[check.ps1] ruff: verification passed."
            }
        }
        catch {
            $script:Errors += "ruff: Problems found in the code (run with -FixRuff to fix automatically)"
            $script:HasErrors = $true
        }
    }
}

# Основной поток
Log "The beginning of code verification..."
Run-Black
Run-Isort
Run-Ruff

# Вывод итогов
if ($script:HasErrors) {
    Write-Host "`n=== Total ==="
    foreach ($error in $script:Errors) {
        Write-Host "- $error"
    }
    Write-Host "`nTo fix most of the problems, run the script with the -Fix flag."
    exit 1
}
else {
    Write-Host "`n=== Total ==="
    Write-Host "All checks have been completed successfully!"
    exit 0
}
