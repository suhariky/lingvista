#!/bin/bash -e

# Корень репозитория
SERVICE_ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../" && pwd)"
PROJECT_ROOT="${PROJECT_ROOT:-$SERVICE_ROOT_DIR}"

# Параметры
AUTO_FIX=false
AUTO_FIX_BLACK=false
AUTO_FIX_ISORT=false
AUTO_FIX_RUFF=false
VERBOSE=false
SHOW_HELP=false

# Текст помощи
show_help() {
    cat <<EOF
Использование: $(basename "$0") [опции]

Опции:
  -f,  --fix           Автоматически исправить все найденные проблемы
  -fb, --fix-black     Автоматически исправить найденные проблемы black
  -fi, --fix-isort     Автоматически исправить найденные проблемы isort
  -fr, --fix-ruff      Автоматически исправить найденные проблемы ruff
  -v,  --verbose       Подробный вывод
  -h,  --help          Показать это сообщение и выйти

Примеры:
  # Проверка с подробным выводом
  $0 --verbose

  # Автоисправление всех проблем
  $0 --fix

  # Автоисправление black с подробным выводом
  $0 --fix-black --verbose
EOF
}

# Разбор аргументов
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--fix)
            AUTO_FIX=true
            shift
            ;;
        -fb|--fix-black)
            AUTO_FIX_BLACK=true
            shift
            ;;
        -fi|--fix-isort)
            AUTO_FIX_ISORT=true
            shift
            ;;
        -fr|--fix-ruff)
            AUTO_FIX_RUFF=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            SHOW_HELP=true
            shift
            ;;
        *)
            echo "Ошибка: Неизвестный аргумент: $1"
            show_help
            exit 1
            ;;
    esac
done


# Показать помощь и выйти если запрошено
if [ "$SHOW_HELP" = true ]; then
    show_help
    exit 0
fi

# Функция для вывода verbose сообщений
log() {
    if [ "$VERBOSE" = true ]; then
        echo "$(date +'%Y-%m-%d %H:%M:%S') $1"
    fi
}

# Глобальные переменные для хранения ошибок
ERRORS=()
HAS_ERRORS=false

# Активация виртуального окружения
log "Активация виртуального окружения..."
. "${SERVICE_ROOT_DIR}/scripts/linux/activate.sh" || {
    echo "Ошибка: Не удалось активировать виртуальное окружение"
    exit 1
}

# Проверка black
run_black() {
    local config="${SERVICE_ROOT_DIR}/pyproject.toml"
    local check_cmd=("black" "--config" "$config" "--check" "$PROJECT_ROOT")
    local fix_cmd=("black" "--config" "$config" "$PROJECT_ROOT")

    echo -e "\n=== Проверка black ==="

    if [ "$AUTO_FIX" = "true" ] || [ "$AUTO_FIX_BLACK" = "true" ]; then
        log "Автоформатирование..."
        "${fix_cmd[@]}"
    else
        if ! "${check_cmd[@]}"; then
            ERRORS+=("black: Найдены несоответствия стилю (запустите с --fix для исправления)")
            HAS_ERRORS=true
        else
            echo "✓ black: проверка пройдена"
        fi
    fi
}

# Проверка isort
run_isort() {
    local config="${SERVICE_ROOT_DIR}/pyproject.toml"
    local check_cmd=("isort" "--settings-path" "$config" "--check-only" "$PROJECT_ROOT")
    local fix_cmd=("isort" "--settings-path" "$config" "$PROJECT_ROOT")

    echo -e "\n=== Проверка isort ==="

    if [ "$AUTO_FIX" = "true" ] || [ "$AUTO_FIX_ISORT" = "true" ]; then
        log "Автоформатирование..."
        "${fix_cmd[@]}"
    else
        if ! "${check_cmd[@]}"; then
            ERRORS+=("isort: Найдены неотсортированные импорты (запустите с --fix для исправления)")
            HAS_ERRORS=true
        else
            echo "✓ isort: проверка пройдена"
        fi
    fi
}

# Проверка ruff
run_ruff() {
    local config="${SERVICE_ROOT_DIR}/pyproject.toml"
    local check_cmd=("ruff" "--config" "$config" "check" "$PROJECT_ROOT")
    local fix_cmd=("ruff" "--config" "$config" "check" "--fix" "$PROJECT_ROOT")

    echo -e "\n=== Проверка ruff ==="

    if [ "$AUTO_FIX" = "true" ] || [ "$AUTO_FIX_RUFF" = "true" ]; then
        log "Автоисправление..."
        if ! "${fix_cmd[@]}"; then
            ERRORS+=("ruff: Найдены проблемы, требующие ручного исправления")
            HAS_ERRORS=true
        fi
    else
        if ! "${check_cmd[@]}"; then
            ERRORS+=("ruff: Найдены проблемы в коде (запустите с --fix для автоматического исправления)")
            HAS_ERRORS=true
        else
            echo "✓ ruff: проверка пройдена"
        fi
    fi
}

# Основной поток
log "Начало проверки кода..."
run_black
run_isort
run_ruff

# Вывод итогов
if [ "$HAS_ERRORS" = true ]; then
    echo -e "\n\n=== Итог ==="
    for error in "${ERRORS[@]}"; do
        echo "• $error"
    done
    echo -e "\nДля исправления большинства проблем запустите скрипт с флагом --fix"
    exit 1
else
    echo -e "\n\n=== Итог ==="
    echo "✓ Все проверки пройдены успешно!"
    exit 0
fi
