from django.forms import ClearableFileInput, FileInput


class CustomFileInput(FileInput):
    template_name = 'widgets/custom_file_input.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['custom_text'] = 'Select file'
        return context


class CustomClearableFileInput(ClearableFileInput):
    template_name = 'widgets/clearable_file_input_simple.html'
    initial_text = 'Current file'  # Текст о текущем файле
    input_text = 'Select file'  # Текст кнопки выбора (английский)
    clear_checkbox_label = 'Remove'  # Текст чекбокса
