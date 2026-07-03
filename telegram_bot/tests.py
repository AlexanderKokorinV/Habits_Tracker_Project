import datetime
from unittest.mock import patch, MagicMock

import requests
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.conf import settings

from habits.models import Habit
from telegram_bot.services import TelegramBotAPIService

# Create your tests here.


User = get_user_model()

class TelegramServiceTestCase(TestCase):
    """Тест сервисной функциональности"""

    def setUp(self):
        """Создание тестовых данных для проверки сервиса"""
        self.user = User.objects.create_user(
            email="bot_tester@test.com",
            password="1234!1234",
            telegram_chat_id="123456789"
        )
        # Полезная привычка с текстовой наградой
        self.habit_with_reward = Habit.objects.create(
            user=self.user,
            action="умываться",
            time=datetime.time(7, 0, 0),
            place="ванной",
            is_pleasant=False,
            duration=60,
            reward="съесть яблоко"
        )

    def test_build_habit_reminder_text_with_reward(self):
        """Проверка правильности сборки Markdown-текста по книге"""
        text = TelegramBotAPIService.build_habit_reminder_text(self.habit_with_reward)

        # Проверка, что текст формируется корректно
        self.assertIn("\u23F0 *Время атомной привычки!*", text)
        self.assertIn("Я буду **умываться** в **07:00** в **ванной**.", text)
        self.assertIn("\U0001F381 _Ваша награда за выполнение:_ съесть яблоко", text)

        # Подмена requests.post на виртуальный объект mock_post с помощью patch
        @patch("telegram_bot.services.requests.post")
        def test_send_message_success(self, mock_post):
            """Проверка успешной отправки сообщения (имитация статуса 200)"""

            # Mock-ответ от Telegram
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_post.return_value = mock_response

            # Вызов реального сервисного метода
            result = TelegramBotAPIService.send_message(chat_id="123456789", text="Тестовое сообщение")

            # Проверки
            self.assertTrue(result)
            mock_post.assert_called_once() # requests.post вызывается ровно один раз

            # Проверка, что сервис попытался отправить запрос на правильный URL
            expected_url = f"{settings.TELEGRAM_URL.rstrip('/')}/{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
            self.assertEqual(expected_url, mock_post.call_args[0][0])

        @patch("telegram_bot.services.requests.post")
        def test_send_message_network_error(self, mock_post):
            """Проверка устойчивости сервиса к падению сети (имитация ошибки 500)"""

            # Имитация сбоя сетевой библиотеки requests
            mock_post.side_effect = requests.RequestException("Сетевой сбой")

            # Вызов реального сервисного метода
            result = TelegramBotAPIService.send_message(chat_id="123456789", text="Тестовое сообщение")

            # Код возвращает False без аварийного завершения (try/except)
            self.assertFalse(result)