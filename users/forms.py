from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import re
from .models import User
from django.contrib.auth import authenticate

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")

    class Meta:
        model = User
        fields = ("name", "surname", "email", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Электронная почта",
        }


class UserLoginForm(AuthenticationForm):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'placeholder': 'Email'}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={'placeholder': 'Пароль'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].label = "Электронная почта"
        self.fields["password"].label = "Пароль"
        self.error_messages = {
            "invalid_login": "Неверный email или пароль",
        }

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")
        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise ValidationError(self.error_messages["invalid_login"])
            else:
                self.confirm_login_allowed(self.user_cache)
        return self.cleaned_data

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'avatar-input'}),
        }

    def clean_github_url(self):
        url = self.cleaned_data.get("github_url")
        if url:
            validator = URLValidator()
            try:
                validator(url)
            except ValidationError:
                raise ValidationError("Введите корректный URL")
            if "github.com" not in url:
                raise ValidationError("Ссылка должна вести на GitHub")
        return url