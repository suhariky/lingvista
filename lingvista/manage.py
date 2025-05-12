#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv


def get_env_vars_from_example(file_path='.env.example'):
    """
    Извлекает имена переменных из .env.example файла

    :param file_path: Путь к файлу .env.example
    :return: Список имен переменных окружения
    """
    env_vars = []
    env_file = Path(file_path)

    if not env_file.exists():
        return env_vars

    # Регулярное выражение для поиска имен переменных
    pattern = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=')

    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):  # Игнорируем пустые строки и комментарии
                match = pattern.match(line)
                if match:
                    env_vars.append(match.group(1))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lingvista.settings')
    load_dotenv()
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    required_vars = get_env_vars_from_example((Path(__file__).parent / '.env.example').as_posix())
    for var in required_vars:
        if not os.getenv(var):
            raise ValueError(f'Set {var} in environment variables')
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
