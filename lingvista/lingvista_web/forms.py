from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_photo', 'streak', 'completed_levels', 'language_level', 'achievements']
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'input-custom'}),
            'streak': forms.NumberInput(attrs={'class': 'input-custom'}),
            'completed_levels': forms.NumberInput(attrs={'class': 'input-custom'}),
            'language_level': forms.TextInput(attrs={'class': 'input-custom'}),
            'achievements': forms.Textarea(attrs={'class': 'input-custom'}),
        }

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['achievements'].widget.attrs.update({'placeholder': 'Введите достижения'})
        self.fields['language_level'].widget.attrs.update({'placeholder': 'Введите уровень языка'})


class UserLogInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))

    class Meta:
        model = User
        fields = ('username', 'password')


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Your Email'})
    )
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}))
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password confirmation'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
