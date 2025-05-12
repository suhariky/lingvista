# strategies.py
from abc import ABC, abstractmethod


class AnswerCheckStrategy(ABC):
    @abstractmethod
    def check_answer(self, task, user_answer) -> bool:
        pass


class MultipleChoiceCheckStrategy(AnswerCheckStrategy):
    def check_answer(self, task, user_answer) -> bool:
        correct_option = [task.option1, task.option2, task.option3][int(task.correct_answer) - 1]
        return user_answer == correct_option


class AudioAnswerCheckStrategy(AnswerCheckStrategy):
    def check_answer(self, task, user_answer) -> bool:
        normalized_user = ' '.join(user_answer.split()).lower()
        normalized_correct = ' '.join(task.correct_answer.split()).lower()
        print("normalized_user", normalized_user, "normalized_correct", normalized_correct)
        return normalized_user == normalized_correct


def get_check_strategy(task) -> tuple[str, AnswerCheckStrategy]:
    if task.option1 or task.option2 or task.option3:
        return 'task', MultipleChoiceCheckStrategy()
    elif task.audio:
        return 'audio_answer', AudioAnswerCheckStrategy()
    raise ValueError("Unsupported task type")
