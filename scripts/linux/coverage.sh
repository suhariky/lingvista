#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"

# Переходим в виртуальное окружение
. "${SERVICE_ROOT_DIR}/scripts/linux/activate.sh"

# Запускаем сервер
coverage run --omit="migrations" "${SERVICE_ROOT_DIR}/lingvista/manage.py" test lingvista_web
coverage report --fail-under=70
