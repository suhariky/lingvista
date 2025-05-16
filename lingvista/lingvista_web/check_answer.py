import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


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
        try:
            logger.debug(
                f"Checking multiple choice answer - Task ID: {task.id}, "
                f"User answer: '{user_answer}', Options: {task.option1}/{task.option2}/{task.option3}, "
                f"Correct index: {task.correct_answer}"
            )

            correct_option = [task.option1, task.option2, task.option3][int(task.correct_answer) - 1]
            result = user_answer == correct_option

            logger.debug(
                f"Multiple choice result - Task ID: {task.id}, " f"Correct option: '{correct_option}', Result: {result}"
            )

            return result
        except IndexError:
            logger.error(
                f"IndexError in MultipleChoiceCheckStrategy - Task ID: {task.id}, "
                f"Correct_answer: {task.correct_answer}, "
                f"Options count: {sum(1 for x in [task.option1, task.option2, task.option3] if x)}"
            )
            raise
        except Exception as e:
            logger.error(f"Error in MultipleChoiceCheckStrategy for Task ID: {task.id}: {str(e)}", exc_info=True)
            raise


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
        try:
            logger.debug(
                f"Checking audio answer - Task ID: {task.id}, "
                f"User answer: '{user_answer}', Correct answer: '{task.correct_answer}'"
            )

            normalized_user = ' '.join(user_answer.split()).lower()
            normalized_correct = ' '.join(task.correct_answer.split()).lower()
            result = normalized_user == normalized_correct

            logger.debug(
                f"Audio answer normalized - Task ID: {task.id}, "
                f"User: '{normalized_user}', Correct: '{normalized_correct}', Result: {result}"
            )

            return result
        except AttributeError:
            logger.error(
                f"AttributeError in AudioAnswerCheckStrategy - Task ID: {task.id}, "
                f"User answer type: {type(user_answer)}, Correct answer type: {type(task.correct_answer)}"
            )
            raise
        except Exception as e:
            logger.error(f"Error in AudioAnswerCheckStrategy for Task ID: {task.id}: {str(e)}", exc_info=True)
            raise


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
    try:
        logger.debug(f"Determining strategy for Task ID: {task.id}")

        if task.option1 or task.option2 or task.option3:
            logger.debug(f"Task ID: {task.id} - using MultipleChoice strategy")
            return 'task', MultipleChoiceCheckStrategy()
        if task.audio:
            logger.debug(f"Task ID: {task.id} - using AudioAnswer strategy")
            return 'audio_answer', AudioAnswerCheckStrategy()

        error_msg = f"Unsupported task type for Task ID: {task.id}"
        logger.error(error_msg)
        raise ValueError(error_msg)
    except Exception as e:
        logger.error(
            f"Error in get_check_strategy for Task ID: {task.id if hasattr(task, 'id') else 'unknown'}: {str(e)}",
            exc_info=True,
        )
        raise
