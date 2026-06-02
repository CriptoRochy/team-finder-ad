from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator

from .models import User
from .utils import validate_phone


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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Электронная почта"
        self.fields["username"].widget = forms.EmailInput(
            attrs={"placeholder": "Email"}
        )
        self.fields["password"].label = "Пароль"
        self.fields["password"].widget = forms.PasswordInput(
            attrs={"placeholder": "Пароль"}
        )


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
            "avatar": forms.FileInput(attrs={"class": "avatar-input"}),
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

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        return validate_phone(phone, self.instance)
