#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"
cd "${SERVICE_ROOT_DIR}"

# Переходим в виртуальное окружение
. "${SERVICE_ROOT_DIR}/scripts/linux/activate.sh"

# Установка необходимых модулей
echo "Установка модулей..."
uv sync --active

# Обновление pip
echo "Обновление pip..."
pip install --upgrade pip
