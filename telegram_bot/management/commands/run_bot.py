from django.core.management import BaseCommand
from django.conf import settings
import requests
import time

from habits.models import Habit, HabitLog


class Command(BaseCommand):
    """Кастомная команда - обработчик нажатия на кнопку в Telegram"""

    help = "Запуск фонового обработчика инлайн-кнопок Telegram"

    def handle(self, *args, **options):
        bot_token = settings.TELEGRAM_BOT_TOKEN
        base_url = f"{settings.TELEGRAM_URL.rstrip('/')}/{bot_token}"

        self.stdout.write(self.style.SUCCESS("Бот-обработчик успешно запущен..."))
        offset = 0

        while True:
            # Получаем обновления из Telegram
            try:
                response = requests.get(f"{base_url}/getUpdates", params={"offset": offset, "timeout": 20}, timeout=25)
                if response.status_code != 200:
                    continue

                updates = response.json().get("result", [])
                for update in updates:
                    offset = update["update_id"] + 1

                    # Проверка, является ли обновление нажатием на кнопку
                    if "callback_query" in update:
                        callback = update["callback_query"]
                        callback_id = callback["id"]
                        data = callback["data"]
                        message = callback["message"]
                        chat_id = message["chat"]["id"]
                        message_id = message["message_id"]

                        # Проверка технического ключа
                        if data.startswith("check_habit:"):
                            habit_id = int(data.split(":")[1])

                            try:
                                habit = Habit.objects.get(id=habit_id)
                                # Создаетя лог выполнения привычки в базе данных PostgreSQL
                                HabitLog.objects.create(habit=habit)

                                # Отправка уведомления в Telegram, что кнопка сработала
                                requests.post(f"{base_url}/answerCallbackQuery",
                                              json={"callback_query_id": callback_id, "text": "Привычка отмечена!"})

                                # Обновление текста сообщения
                                new_text = message["text"] + "\n\n**Выполнено! Отличная работа по системе атомных привычек!**"
                                requests.post(f"{base_url}/editMessageText", json={
                                    "chat_id": chat_id,
                                    "message_id": message_id,
                                    "text": new_text,
                                    "parse_mode": "Markdown"
                                })

                            except Habit.DoesNotExist:
                                requests.post(f"{base_url}/answerCallbackQuery", json={
                                    "callback_query_id": callback_id,
                                    "text": "Ошибка: Привычка не найдена."
                                })

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Ошибка в цикле бота: {e}"))
                time.sleep(5)

