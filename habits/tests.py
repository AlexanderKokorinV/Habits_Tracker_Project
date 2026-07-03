from django.contrib.admin import action
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from habits.models import Habit, HabitLog

# Create your tests here.


User = get_user_model()

class HabitTestCase(APITestCase):
    """Тесты для привычек"""

    def setUp(self):
        """Подготовка тестовых данных перед каждым тестом"""

        # Создание пользователей для проверки прав доступа
        self.user_owner = User.objects.create_user(email="owner@example.com", password="password123")
        self.user_other = User.objects.create_user(email="other@example.com", password="password123")

        # Авторизация владельца по умолчанию
        self.client.force_authenticate(user=self.user_owner)

        # Объявление базового URL-адреса для создания привычек
        self.list_create_url = reverse("habits:habits-list")

        # Создание одной базовой приватной привычки владельца для тестов чтения/обновления/удаления
        self.habit = Habit.objects.create(
            user=self.user_owner,
            action="читать 5 страниц книги",
            time="20:00:00",
            place="кресле",
            is_pleasant=False,
            duration=120,
            reward="еще 5 страниц книги"
        )
        self.detail_url = reverse("habits:habits-detail", kwargs={"pk": self.habit.id})

#-----------Тесты валидаторов сериализатора-----------

    def test_validation_exclude_reward_and_related_habit(self):
        """Тест валидации - запрет одновременного выбора награды и связанной привычки"""
        pleasant_habit = Habit.objects.create(
            user=self.user_owner,
            action="делать прогулку",
            time="21:00:00",
            place="сквере",
            is_pleasant=True,
            duration=120,
        )
        data = {
            "action": "составлять план на завтра",
            "time": "20:40:00",
            "place": "комнате",
            "is_pleasant": False,
            "duration": 120,
            "reward": "послушать музыку",
            "related_habit": pleasant_habit.id
        }
        response = self.client.post(self.list_create_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_duration_limit(self):
        """Тест валидации - время выполнения привычки не должно превышать 120 секунд"""
        data = {
            "action": "делать зарядку",
            "time": "07:30:00",
            "place": "квартире",
            "is_pleasant": False,
            "duration": 130, # Ошибка: > 120 секунд
        }
        response = self.client.post(self.list_create_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_related_habit_must_be_pleasant(self):
        """Тест валидации - связанная привычка обязательно должна иметь флаг иметь признак приятной"""
        useful_habit = Habit.objects.create(
            user=self.user_owner,
            action = "подготавливать вещи на утро",
            time="21:40:00",
            place="гостиной",
            is_pleasant=False,
            duration=60,
        )
        data = {
            "action": "прибирать стол",
            "time": "21:45:00",
            "place": "кухня",
            "is_pleasant": False,
            "duration": 60,
            "related_habit": useful_habit.id # Ошибка: привязка к полезной привычке
        }
        response = self.client.post(self.list_create_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_pleasant_habit_cannot_have_reward_or_related_one(self):
        """Тест валидации - у приятной привычки не может быть своего вознаграждения или связанной привычки"""
        data = {
            "action": "принимать душ",
            "time": "22:00:00",
            "place": "ванной",
            "is_pleasant": True,
            "duration": 60,
            "reward": "посмотреть кино" # Ошибка: у приятной привычки есть награда
        }
        response = self.client.post(self.list_create_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_validation_periodicity_limit(self):
        """Тест валидации - периодичность не может быть реже, чем 1 раз в 7 дней"""
        data = {
            "action": "обновлять список дел на неделю",
            "time": "12:00:00",
            "place": "телефоне",
            "is_pleasant": False,
            "duration": 60,
            "periodicity": 8, # Ошибка: > 7 дней
        }
        response = self.client.post(self.list_create_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#-----------CRUD тесты и пагинация-----------

    def test_get_habits_list_with_pagination(self):
        """CRUD — получение списка привычек текущего пользователя (с пагинацией)"""

        for i in range(7): # Создаем 7 привычек, чтобы активировать пагинацию
            Habit.objects.create(
                user=self.user_owner,
                action=f"действие {i}",
                time="6:30:00",
                place="дома",
                duration=30
            )
        response = self.client.get(self.list_create_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 5) # На странице ровно 5 элементов

    def test_get_habit_detail(self):
        """CRUD — получение деталей конкретной привычки её владельцем"""
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["action"], self.habit.action)

    def test_update_habit_patch(self):
        """CRUD — частичное обновление привычки (PATCH) владельцем"""
        data = {"action": "поливать растения"}
        response = self.client.patch(self.detail_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Habit.objects.get(id=self.habit.id).action, "поливать растения")

    def test_delete_habit(self):
        """CRUD — удаление привычки владельцем"""
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Habit.objects.filter(id=self.habit.id).count(), 0)

#-----------Тесты кастомных эндпоинтов и прав доступа-----------

    def test_get_public_habits_list(self):
        """Эндпоинт public - просмотр чужих публичных привычек"""

        # Авторизация стороннего пользователя
        self.client.force_authenticate(user=self.user_other)

        self.habit.is_public = True # Привычка владельца является публичной
        self.habit.save()

        public_url = reverse("habits:habits-public")
        response = self.client.get(public_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Сторонний пользователь видит публичную привычку владельца в результатах
        self.assertEqual(response.data["results"][0]["id"], self.habit.id)

    def test_check_habit_endpoint(self):
        """Эндпоинт check - успешное логирование выполнения привычки владельцем"""
        check_url = reverse("habits:habits-check", kwargs={"pk": self.habit.id})
        response = self.client.post(check_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(HabitLog.objects.filter(habit=self.habit).count(), 1) # Создалась ровно одна запись

    def test_permission_other_cannot_check_or_edit(self):
        """Права доступа - сторонний пользователь получает 404 при попытке доступа к чужой приватной привычке"""

        # Авторизация стороннего пользователя
        self.client.force_authenticate(user=self.user_other)

        # Попытка отредактировать чужую привычку
        response_patch = self.client.patch(self.detail_url, data={"action": "взлом"}, format="json")
        self.assertEqual(response_patch.status_code, status.HTTP_404_NOT_FOUND)

        check_url = reverse("habits:habits-check", kwargs={"pk": self.habit.id})
        response_check = self.client.post(check_url)
        self.assertEqual(response_check.status_code, status.HTTP_404_NOT_FOUND)

