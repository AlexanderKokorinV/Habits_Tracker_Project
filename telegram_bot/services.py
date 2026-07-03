import json
import requests
from django.conf import settings
from habits.models import Habit


class TelegramBotAPIService:
    """Сервис для интеграции с Telegram Bot API"""

    @staticmethod
    def _get_api_url() -> str:

        # Чтение токен бота из настроек
        if not hasattr(settings, "TELEGRAM_BOT_TOKEN") or not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("В конфигурации settings.py отсутствует или пуст TELEGRAM_BOT_TOKEN")

        if not hasattr(settings, "TELEGRAM_URL") or not settings.TELEGRAM_URL:
            raise ValueError("В конфигурации settings.py отсутствует или пуст TELEGRAM_URL")

        return f"{settings.TELEGRAM_URL.rstrip('/')}{settings.TELEGRAM_BOT_TOKEN}/sendMessage"


    @classmethod
    def build_habit_reminder_text(cls, habit: Habit) -> str:
        """Формирует текст напоминания по канонам книги 'Атомные привычки"""
        message = (
            f"**Время атомной привычки!**\n\n"
            f"Я буду **{habit.action}** в **{habit.time.strftime('%H:%M')}** в **{habit.place}**."
        )

        if habit.related_habit:
            message += f"\n\n_Сразу после этого сделайте приятное действие:_{habit.related_habit.action}"
        elif habit.reward:
            message += f"\n\n_Ваша награда за выполнение:_{habit.reward}"

        return message

    @classmethod
    def send_message(cls, chat_id: str, text: str, reply_markup: dict = None) -> bool:
        """Отправляет текстовое сообщение с кнопкой в Telegram"""
        try:
            url = cls._get_api_url()
            payload = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "Markdown"
            }

            # Если кнопки переданы - добавляем их в запрос
            if reply_markup:
                payload["reply_markup"] = json.dumps(reply_markup)

            response = requests.post(url, json=payload, timeout=5)
            response.raise_for_status()
            return True

        except (requests.RequestException, ValueError) as e:
            print(f"Ошибка Telegram Service при отправке в чат {chat_id}: {e}")
            return False

    @classmethod
    def send_habit_reminder_with_button(cls, chat_id: str, text: str, habit_id: int) -> bool:
        """Отправляет напоминание с кнопкой 'Выполнено'"""
        reply_markup = {
            "inline_keyboard": [[
                {
                    "text": "✅ Выполнено!",
                    "callback_data": f"check_habit:{habit_id}"
                }
            ]]
        }
        return cls.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup)


