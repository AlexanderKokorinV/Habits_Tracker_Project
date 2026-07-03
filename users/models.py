from django.contrib.auth.models import AbstractUser
from django.db import models

from users.managers import CustomUserManager

# Create your models here.


class User(AbstractUser):
    """Модель пользователя с email и без использования username"""

    username = None
    email = models.EmailField(max_length=255, unique=True, verbose_name="Email", help_text="Укажите ваш email")
    phone_number = models.CharField(
        max_length=35, null=True, blank=True, verbose_name="Телефон", help_text="Укажите ваш номер телефона"
    )
    city = models.CharField(max_length=100, null=True, blank=True, verbose_name="Город", help_text="Укажите ваш город")
    avatar = models.ImageField(
        upload_to="users/avatars/", null=True, blank=True, verbose_name="Аватар", help_text="Подгрузите ваш аватар"
    )

    # Поле для интеграции с Telegram-ботом
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Telegram Chat ID",
        help_text="ID чата в Telegram для отправки уведомлений",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
