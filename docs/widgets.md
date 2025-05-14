# Кастомные виджеты (widgets.py)

В этом разделе описаны пользовательские виджеты для форм Django.

---

## `CustomFileInput`
- **Назначение**: Кастомный виджет для загрузки файлов
- **Родительский класс**: `FileInput`
- **Особенности**:
  - Использует шаблон `widgets/custom_file_input.html`
  - Добавляет кастомный текст "Select file" в контекст виджета
- **Использование**:
  ```python
  class MyForm(forms.Form):
      file = forms.FileField(widget=CustomFileInput())
  ```

## CustomClearableFileInput

### Назначение
Улучшенный виджет для загрузки файлов с возможностью очистки

### Родительский класс
`ClearableFileInput`

### Настройки
- **template_name**: `widgets/clearable_file_input_simple.html`
- **initial_text**: "Current file" (текст о текущем файле)
- **input_text**: "Select file" (текст кнопки выбора)
- **clear_checkbox_label**: "Remove" (текст чекбокса удаления)

### Пример использования
```python
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']
        widgets = {
            'avatar': CustomClearableFileInput()
        }
```
## Особенности реализации

### Общие для всех виджетов
- Позволяют кастомизировать внешний вид через HTML-шаблоны
- Поддерживают стандартное поведение Django-виджетов

### Особенности CustomClearableFileInput
- Предоставляет возможность удаления уже загруженного файла
- Имеет настраиваемые текстовые labels

## Расположение шаблонов
Шаблоны виджетов должны располагаться по следующим путям:
- `templates/widgets/custom_file_input.html`
- `templates/widgets/clearable_file_input_simple.html`

## Рекомендации по использованию

1. **Выбор виджета**:
   - Для простой загрузки файлов используйте `CustomFileInput`
   - Для полей с возможностью удаления используйте `CustomClearableFileInput`

2. **Кастомизация текстов**:
```python
CustomClearableFileInput(
    input_text="Выберите файл",
    clear_checkbox_label="Удалить"
)
```
