from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import UserManager
from .utils import generate_avatar


NAME_MAX_LENGTH = 124
PHONE_MAX_LENGTH = 12
ABOUT_MAX_LENGTH = 256


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(
        unique=True, verbose_name="Электронная почта")
    name = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name="Имя")
    surname = models.CharField(
        max_length=NAME_MAX_LENGTH, verbose_name="Фамилия")
    avatar = models.ImageField(
        upload_to="avatars/", blank=True, verbose_name="Аватар")
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH, blank=True, verbose_name="Телефон")
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    about = models.TextField(
        max_length=ABOUT_MAX_LENGTH, blank=True, verbose_name="О себе")
    is_active = models.BooleanField(
        default=True, verbose_name="Активен")
    is_staff = models.BooleanField(
        default=False, verbose_name="Персонал")
    date_joined = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата регистрации")

    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
        verbose_name="Избранные проекты",
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"

    def save(self, *args, **kwargs):
        if not self.avatar:
            generate_avatar(self)
        super().save(*args, **kwargs)
