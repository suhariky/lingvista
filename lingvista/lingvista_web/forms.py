from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile
from .widgets import CustomClearableFileInput


class ProfileEditForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.
    Позволяет изменить фотографию профиля.
    """

    class Meta:
        model = Profile
        fields = ['profile_photo']
        widgets = {
            'profile_photo': CustomClearableFileInput(attrs={'class': 'input-custom'}),
        }


class EmailChangeForm(forms.Form):
    """
    Форма для изменения email пользователя.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input-custom'}),
        label="New Email",
        help_text="Введите новый email адрес",
    )


class CustomPasswordChangeForm(PasswordChangeForm):
    """
    Кастомная форма изменения пароля с добавлением CSS-классов к полям.
    Наследуется от стандартной PasswordChangeForm.
    """

    def __init__(self, *args, **kwargs):
        """
        Инициализация формы. Добавляет CSS-класс 'input-custom' ко всем полям.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'input-custom'})


class UserLogInForm(AuthenticationForm):
    """
    Форма для входа пользователя в систему.
    Наследуется от стандартной AuthenticationForm.
    """

    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):
    """
    Форма регистрации нового пользователя.
    Наследуется от стандартной UserCreationForm с добавлением поля email.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Your Email'}),
        help_text="Обязательное поле. Введите действующий email.",
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
        help_text="Требуется. Не более 150 символов. Только буквы, цифры и @/./+/-/_.",
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}),
        help_text="Пароль должен содержать как минимум 8 символов.",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password confirmation'}),
        help_text="Для подтверждения введите, пожалуйста, пароль ещё раз.",
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """
        Проверка, что email уникален в системе.
        """
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже используется.")
        return email
