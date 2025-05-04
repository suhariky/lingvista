#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )/../../" && pwd )"

# Создаем виртуальное окружение
. "${SERVICE_ROOT_DIR}/scripts/linux/create_virtual_environment.sh"

# Устанавливаем зависимости
. "${SERVICE_ROOT_DIR}/scripts/linux/install.sh"
