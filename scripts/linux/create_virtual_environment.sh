#!/bin/bash -e

# Переходим в корневую директорию
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"
cd "${SERVICE_ROOT_DIR}"

# Параметры скрипта
PROJECT="lingvista"
VENV_PATH="${SERVICE_ROOT_DIR}/venv"  # путь до виртуального окружения
PYTHON_VERSION="3.11.4"

# Проверка, установлена ли uv
if ! command -v uv &> /dev/null; then
    echo "Установка окружения на базе uv невозможна, установите uv: . ./scripts/linux/install-third-party.sh"
    exit 1
fi

# Проверка существования каталога виртуального окружения
if [ -d "$VENV_PATH" ] && [ -f "$VENV_PATH/bin/activate" ]; then
    echo "Виртуальное окружение найдено по пути: $VENV_PATH"

    # Активируем тихо, чтобы не выводить приглашение venv в терминал
    . "$VENV_PATH/bin/activate" > /dev/null 2>&1

    # Получение версии Python внутри виртуального окружения
    ACTUAL_PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}' | cut -d'.' -f1-3)

    # Деактивация виртуального окружения
    deactivate > /dev/null 2>&1

    # Проверка версии Python
    if [ "$ACTUAL_PYTHON_VERSION" == "$PYTHON_VERSION" ]; then
        echo "Найдено виртуальное окружение с Python ${ACTUAL_PYTHON_VERSION} и подходит для работы."
    else
        echo "Виртуальное окружение найдено, но создано с использованием Python: $ACTUAL_PYTHON_VERSION"
        echo "Ожидалась версия Python: $PYTHON_VERSION"
        echo "Удалите созданное виртуальное окружение: $VENV_PATH"
        exit 1
    fi
else
    # Создание виртуального окружения
    echo "Создание нового окружения ${PROJECT} с Python ${PYTHON_VERSION}..."
    uv venv --seed --prompt "${PROJECT}" -p "${PYTHON_VERSION}" "${VENV_PATH}"
fi
