#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"

cd "${SERVICE_ROOT_DIR}"

# Переходим в виртуальное окружение
. "${SERVICE_ROOT_DIR}/scripts/linux/activate.sh"

# Запускаем pylint с падением при score < 8.0
pylint lingvista --disable=C0114,R0903,E1101 --max-line-length=120 --fail-under=8 --ignore=migrations
