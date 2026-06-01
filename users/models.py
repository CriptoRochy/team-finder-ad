import random
from io import BytesIO
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from pathlib import Path

class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        return self.create_user(email, name, surname, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, verbose_name="Электронная почта")
    name = models.CharField(max_length=124, verbose_name="Имя")
    surname = models.CharField(max_length=124, verbose_name="Фамилия")
    avatar = models.ImageField(upload_to="avatars/", blank=True, verbose_name="Аватар")
    phone = models.CharField(max_length=12, blank=True, verbose_name="Телефон")
    github_url = models.URLField(blank=True, verbose_name="GitHub")
    about = models.TextField(max_length=256, blank=True, verbose_name="О себе")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    is_staff = models.BooleanField(default=False, verbose_name="Персонал")

    favorites = models.ManyToManyField(
        "projects.Project",
        blank=True,
        related_name="interested_users",
        verbose_name="Избранные проекты"
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.name} {self.surname}"

    def generate_avatar(self):
        bg_color = (random.randint(100, 200), random.randint(100, 200), random.randint(100, 200))
        size = 200
        image = Image.new("RGB", (size, size), bg_color)
        draw = ImageDraw.Draw(image)
        first_letter = self.name[0].upper()

        font_path = Path(settings.BASE_DIR) / "fonts" / "vestisans-medium.ttf"
        if font_path.exists():
            font = ImageFont.truetype(str(font_path), 140)
        else:
            font = ImageFont.load_default()

        draw.text((size//2, size//2), first_letter, fill="white", font=font, anchor="mm")

        buffer = BytesIO()
        image.save(buffer, format="PNG")
        filename = f"avatar_{self.email}.png"
        self.avatar.save(filename, ContentFile(buffer.getvalue()), save=False)
        buffer.close()

    def save(self, *args, **kwargs):
        if not self.avatar:
            self.generate_avatar()
        super().save(*args, **kwargs)