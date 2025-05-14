#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"

cd "${SERVICE_ROOT_DIR}"

# Переходим в виртуальное окружение
. "${SERVICE_ROOT_DIR}/scripts/linux/activate.sh"

# Запускаем pycodestyle для проверки pep8
pycodestyle lingvista --max-line-length=120 --exclude=migrations --ignore=E701
