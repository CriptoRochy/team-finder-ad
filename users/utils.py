import random
from io import BytesIO
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


AVATAR_SIZE = 200
AVATAR_FONT_SIZE = 140
AVATAR_BG_COLOR_MIN = 100
AVATAR_BG_COLOR_MAX = 200


def generate_avatar(user_instance):
    bg_color = (
        random.randint(AVATAR_BG_COLOR_MIN, AVATAR_BG_COLOR_MAX),
        random.randint(AVATAR_BG_COLOR_MIN, AVATAR_BG_COLOR_MAX),
        random.randint(AVATAR_BG_COLOR_MIN, AVATAR_BG_COLOR_MAX),
    )
    image = Image.new("RGB", (AVATAR_SIZE, AVATAR_SIZE), bg_color)
    draw = ImageDraw.Draw(image)
    first_letter = user_instance.name[0].upper()

    font_path = Path(settings.BASE_DIR) / "fonts" / "vestisans-medium.ttf"
    if font_path.exists():
        font = ImageFont.truetype(str(font_path), AVATAR_FONT_SIZE)
    else:
        font = ImageFont.load_default()

    draw.text(
        (AVATAR_SIZE // 2, AVATAR_SIZE // 2),
        first_letter,
        fill="white",
        font=font,
        anchor="mm",
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    filename = f"avatar_{user_instance.email}.png"
    user_instance.avatar.save(
        filename, ContentFile(buffer.getvalue()), save=False)
    buffer.close()


def validate_phone(phone, instance=None):
    if not phone:
        return phone

    from .models import User

    phone = re.sub(r"[^\d+]", "", phone)

    if phone.startswith("8") and len(phone) == 11:
        phone = "+7" + phone[1:]
    elif phone.startswith("7") and len(phone) == 11:
        phone = "+" + phone
    elif phone.startswith("+7") and len(phone) == 12:
        pass
    else:
        raise ValidationError(
            "Номер телефона должен быть в формате 8XXXXXXXXXX или +7XXXXXXXXXX"
        )

    if (User.objects.filter(phone=phone)
            .exclude(pk=getattr(instance, 'pk', None))
            .exists()):
        raise ValidationError(
            "Пользователь с таким номером телефона уже существует"
        )

    return phone
