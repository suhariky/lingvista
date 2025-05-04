#!/bin/bash -e

# Функция для определения дистрибутива
detect_distro() {
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        DISTRO=$ID
    elif [ -f /etc/redhat-release ]; then
        DISTRO="rhel"
    elif [ -f /etc/debian_version ]; then
        DISTRO="debian"
    else
        echo "Не удалось определить дистрибутив."
        exit 1
    fi
}

# Функция для установки curl и др
install_dependencies() {
    case $DISTRO in
        ubuntu|debian|pop|linuxmint|kali)
            echo "Установка зависимостей для Debian-based дистрибутивов..."
            sudo apt update
            sudo apt install -y curl
            ;;
        fedora|rhel|centos|almalinux|rocky)
            echo "Установка зависимостей для RHEL-based дистрибутивов..."
            if command -v dnf &> /dev/null; then
                sudo dnf install -y curl libnsl libxcrypt-compat
            elif command -v yum &> /dev/null; then
                sudo yum install -y curl libnsl libxcrypt-compat
            else
                echo "Не найден менеджер пакетов (dnf или yum)."
                exit 1
            fi
            ;;
        arch|manjaro)
            echo "Установка зависимостей для Arch-based дистрибутивов..."
            sudo pacman -Sy --noconfirm curl libxcrypt-compat
            ;;
        opensuse|sles)
            echo "Установка зависимостей для openSUSE..."
            sudo zypper install -y curl tar gzip
            ;;
        *)
            echo "Дистрибутив не поддерживается: $DISTRO"
            exit 1
            ;;
    esac
}

echo "Установка зависимостей для проекта..."
detect_distro
install_dependencies

# Попытка установки uv
if ! command -v uv &> /dev/null; then
    # Проверка успешности установки curl
    if command -v curl &> /dev/null; then
        echo "curl успешно найден"
    else
        echo "Ошибка: curl не установлен."
        exit 1
    fi

    echo "Установка uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh

    # Путь, который нужно добавить
    NEW_PATH="$HOME/.local/bin"

    # Проверка, содержится ли путь в PATH
    if [[ ":$PATH:" != *":$NEW_PATH:"* ]]; then
        echo "Добавляем $NEW_PATH в PATH..."
        export PATH="$NEW_PATH:$PATH"
        echo "Новый PATH: $PATH"
    else
        echo "$NEW_PATH уже содержится в PATH."
    fi
else
    echo "Все зависимости установлены!!"
fi