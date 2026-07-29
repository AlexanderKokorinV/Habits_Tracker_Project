from datetime import datetime

from celery import shared_task

from habits.models import Habit
from telegram_bot.services import TelegramBotAPIService


@shared_task
def send_habit_reminders():
    """Периодическая задача Celery, проверяющая привычки каждую минуту
    и делегирующая отправку сервису TelegramBotAPIService"""

    now = datetime.now().time()

    # Извлечение нужных привычек из БД
    habits_to_remind = Habit.objects.filter(
        time__hour=now.hour,
        time__minute=now.minute,
        is_pleasant=False,  # Исключаем приятные привычки, так как они являются наградой, а не целью
        user__telegram_chat_id__isnull=False,  # У пользователя должен быть привязан Telegram
    ).select_related("user", "related_habit")

    # Если на эту минуту привычек нет, завершается выполнение
    if not habits_to_remind.exists():
        return f"Нет привычек для отправки на {now.strftime('%H:%M')}"

    sent_count = 0

    for habit in habits_to_remind:
        # Генерация текста сообщения через сервис
        message_text = TelegramBotAPIService.build_habit_reminder_text(habit)

        # Отправка сообщения через сервис
        success = TelegramBotAPIService.send_message(
            chat_id=habit.user.telegram_chat_id,
            text=message_text,
        )
        if success:
            sent_count += 1

    return f"Обработано привычек: {habits_to_remind.count()}, успешно отправлено: {sent_count}"
