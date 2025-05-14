#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"
cd "${SERVICE_ROOT_DIR}"

# Переходим в виртуальное окружение
. "${SERVICE_ROOT_DIR}/scripts/linux/activate.sh"

# Запускаем генерацию документации в папку target
mkdocs build --site-dir "${SERVICE_ROOT_DIR}/target"
