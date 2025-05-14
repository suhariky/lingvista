#!/bin/bash -e

# параметры скрипта
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"
VENV_PATH="${SERVICE_ROOT_DIR}/venv"

# путь до виртуального окружения
if [ -d "${VENV_PATH}" ] && [ -f "${VENV_PATH}/bin/activate" ]; then
    source "${VENV_PATH}/bin/activate"
else
    echo "Виртуальное окружение не установлено"
    exit 1
fi
