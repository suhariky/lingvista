from abc import ABC, abstractmethod


class AnswerCheckStrategy(ABC):
    """
    Абстрактный базовый класс для стратегий проверки ответов.
    Определяет интерфейс для всех конкретных стратегий проверки.
    """

    @abstractmethod
    def check_answer(self, task, user_answer) -> bool:
        """
        Абстрактный метод для проверки ответа пользователя.

        Args:
            task: Объект задания, содержащий правильный ответ
            user_answer: Ответ, предоставленный пользователем

        Returns:
            bool: Результат проверки (True - ответ верный, False - неверный)
        """
        pass


class MultipleChoiceCheckStrategy(AnswerCheckStrategy):
    """
    Конкретная стратегия для проверки заданий с множественным выбором.
    Сравнивает ответ пользователя с выбранным правильным вариантом.
    """

    def check_answer(self, task, user_answer) -> bool:
        """
        Проверяет ответ пользователя для задания с множественным выбором.

        Args:
            task: Объект задания, должен содержать option1, option2, option3 и correct_answer
            user_answer: Выбранный пользователем вариант

        Returns:
            bool: True если ответ совпадает с правильным вариантом, иначе False
        """
        correct_option = [task.option1, task.option2, task.option3][int(task.correct_answer) - 1]
        return user_answer == correct_option


class AudioAnswerCheckStrategy(AnswerCheckStrategy):
    """
    Конкретная стратегия для проверки аудио-заданий.
    Нормализует текст перед сравнением (удаляет лишние пробелы, приводит к нижнему регистру).
    """

    def check_answer(self, task, user_answer) -> bool:
        """
        Проверяет ответ пользователя для аудио-задания.
        Нормализует оба текста перед сравнением.

        Args:
            task: Объект задания, должен содержать correct_answer
            user_answer: Текст, введенный пользователем

        Returns:
            bool: True если нормализованные тексты совпадают, иначе False
        """
        normalized_user = ' '.join(user_answer.split()).lower()
        normalized_correct = ' '.join(task.correct_answer.split()).lower()
        print("normalized_user", normalized_user, "normalized_correct", normalized_correct)
        return normalized_user == normalized_correct


def get_check_strategy(task) -> tuple[str, AnswerCheckStrategy]:
    """
    Фабричный метод для получения подходящей стратегии проверки ответа.

    Args:
        task: Объект задания для анализа

    Returns:
        tuple: Кортеж из (тип задания, стратегия проверки)

    Raises:
        ValueError: Если тип задания не поддерживается
    """
    if task.option1 or task.option2 or task.option3:
        return 'task', MultipleChoiceCheckStrategy()
    if task.audio:
        return 'audio_answer', AudioAnswerCheckStrategy()
    raise ValueError("Unsupported task type")
