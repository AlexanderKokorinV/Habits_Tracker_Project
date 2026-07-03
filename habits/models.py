from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import ForeignKey


# Create your models here.

class Habit(models.Model):
    """Модель привычки"""
    user = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="habits",
        verbose_name="Создатель привычки"
    )
    place = models.CharField(
        max_length=255,
        verbose_name="Место выполнения",
        help_text="Добавьте место, в котором необходимо выполнять привычку"
    )
    time = models.TimeField(
        verbose_name="Время выполнения",
        help_text="Время, когда необходимо выполнять привычку"
    )
    action = models.CharField(
        max_length=500,
        verbose_name="Действие",
        help_text="Действие, которое представляет собой привычка"
    )
    is_pleasant = models.BooleanField(
        default=False,
        verbose_name="Признак приятной привычки",
        help_text="Привычка, которую можно привязать к выполнению полезной привычки"
    )
    related_habit = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="related_to",
        verbose_name="Связанная привычка",
        help_text="Привычка, которая связана с другой привычкой"
    )

    periodicity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Периодичность",
        help_text="Периодичность выполнения привычки для напоминания в днях"
    )
    reward = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Вознаграждение",
        help_text="Чем себя вознаградить после выполнения"
    )
    duration = models.PositiveIntegerField(
        verbose_name="Время на выполнение",
        help_text="Не должно превышать 120 секунд (правило 2 минут)",
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name="Признак публичности",
        help_text="Привычки можно публиковать в общий доступ"
    )

    class Meta:
        verbose_name = "Привычка"
        verbose_name_plural = "Привычки"
        ordering = ["id"]

    def __str__(self):
        return f"Я буду {self.action} в {self.time} в {self.place}"

class HabitLog(models.Model):
    """Модель лога выполнения привычки для трекинга и статистики"""

    habit = ForeignKey(
        Habit,
        on_delete=models.CASCADE,
        related_name="logs",
        verbose_name="Привычка"
    )
    # Дата и время нажатия на кнопку
    checked_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата и время выполнения"
    )

    class Meta:
        verbose_name = "Лог выполнения"
        verbose_name_plural = "Логи выполнения"
        ordering = ["-checked_at"]

    def __str__(self):
        return f"Привычка '{self.habit.action}' выполнена в {self.checked_at.strftime('%d.%m.%Y %H:%M')}"

