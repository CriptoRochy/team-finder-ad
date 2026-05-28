# users/forms.py
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

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(attrs={"placeholder": "Пароль"}))

    def clean(self):
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        if email and password:
            self.user = authenticate(email=email, password=password)
            if self.user is None:
                raise forms.ValidationError("Неверный email или пароль")
        return self.cleaned_data

    def get_user(self):
        return self.user


class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'avatar-input'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if phone:
            phone = re.sub(r"\D", "", phone)
            if phone.startswith("8") and len(phone) == 11:
                phone = "+7" + phone[1:]
            elif phone.startswith("7") and len(phone) == 11:
                phone = "+" + phone
            elif phone.startswith("+7") and len(phone) == 12:
                pass
            else:
                raise ValidationError("Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX")
            if User.objects.exclude(pk=self.instance.pk).filter(phone=phone).exists():
                raise ValidationError("Пользователь с таким номером телефона уже существует")
            return phone
        return phone

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