#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"

# Переходим в виртуальное окружение
. "${SERVICE_ROOT_DIR}/scripts/linux/activate.sh"

# Запускаем миграцию бд
python "${SERVICE_ROOT_DIR}/lingvista/manage.py" makemigrations
python "${SERVICE_ROOT_DIR}/lingvista/manage.py" migrate
