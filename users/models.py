from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.

class User(AbstractUser):
    """Модель пользователя с email и без использования username"""

    email = models.EmailField(max_length=255, unique=True, verbose_name="Email", help_text="Укажите ваш email")

    # Поле для интеграции с Telegram-ботом
    telegram_chat_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Telegram Chat ID",
        help_text="ID чата в Telegram для отправки уведомлений"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email