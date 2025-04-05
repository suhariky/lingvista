from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_photo', 'streak', 'completed_levels', 'language_level', 'achievements']

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)
        self.fields['achievements'].widget.attrs.update({'placeholder': 'Введите достижения'})
        self.fields['language_level'].widget.attrs.update({'placeholder': 'Введите уровень языка'})


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

