from django.forms import ClearableFileInput, FileInput


class CustomFileInput(FileInput):
    """
    Кастомный виджет для загрузки файлов.
    Наследуется от стандартного FileInput и добавляет пользовательский текст.

    Attributes:
        template_name (str): Путь к пользовательскому шаблону виджета.
    """

    template_name = 'widgets/custom_file_input.html'

    def get_context(self, name, value, attrs):
        """
        Добавляет пользовательский текст в контекст шаблона.

        Args:
            name (str): Имя поля формы.
            value: Текущее значение поля.
            attrs (dict): HTML-атрибуты виджета.

        Returns:
            dict: Контекст для рендеринга шаблона виджета.
        """
        context = super().get_context(name, value, attrs)
        context['widget']['custom_text'] = 'Select file'
        return context


class CustomClearableFileInput(ClearableFileInput):
    """
    Кастомный виджет для загрузки файлов с возможностью очистки.
    Наследуется от стандартного ClearableFileInput с измененными текстами.

    Attributes:
        template_name (str): Путь к пользовательскому шаблону виджета.
        initial_text (str): Текст для отображения текущего файла.
        input_text (str): Текст кнопки выбора нового файла.
        clear_checkbox_label (str): Текст метки чекбокса удаления файла.
    """

    template_name = 'widgets/clearable_file_input_simple.html'
    initial_text = 'Current file'
    input_text = 'Select file'
    clear_checkbox_label = 'Remove'
