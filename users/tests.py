from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

# Create your tests here.

User = get_user_model()

class UserAuthTestCase(APITestCase):
    """Тесты для аутентификации, профилей и кастомного менеджера пользователей"""

    def setUp(self):
        """Подготовка базовых данных для тестирования"""
        self.register_url = reverse("users:user_register")
        self.token_url = reverse("users:token_obtain_pair")
        self.profile_url = reverse("users:user_profile")

        # Создание тестового пользователя для проверки логина и профиля
        self.user_email = "test_owner@test.com"
        self.user_password = "1234!1234"
        self.user = User.objects.create_user(
            email=self.user_email,
            password=self.user_password,
        )

    def test_user_registration_success(self):
        """Тест успешной регистрации нового пользователя с мгновенной выдачей JWT"""
        data = {
            "email": "new_test_user@test.com",
            "password": "1234!1234",
        }
        response = self.client.post(self.register_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        # Создалась ровно одна запись
        self.assertEqual(User.objects.filter(email="new_test_user@test.com").count(), 1)

    def test_user_login_and_jwt_obtain(self):
        """Тест получения токенов через эндпоинт Simple-JWT"""
        data = {
            "email": self.user_email,
            "password": self.user_password
        }
        response = self.client.post(self.token_url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_get_and_update_user_profile(self):
        """Тест просмотра и изменения личного профиля авторизованным пользователем"""

        self.client.force_authenticate(user=self.user)

        # Проверка чтения профиля (GET)
        response_get = self.client.get(self.profile_url)
        self.assertEqual(response_get.status_code, status.HTTP_200_OK)
        self.assertEqual(response_get.data["email"], self.user.email)

        # Проверка частичного обновления (PATCH) привязки Telegram Chat ID
        data_patch = {"telegram_chat_id": "123456789"}
        response_patch = self.client.patch(self.profile_url, data=data_patch, format="json")
        self.assertEqual(response_patch.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.get(id=self.user.id).telegram_chat_id, "123456789")

    def test_custom_user_manager_create_superuser(self):
        """Тест кастомного менеджера: проверка создания суперпользователя (createsuperuser)"""
        superuser = User.objects.create_superuser(email="admin@test.com", password="1234!1234")
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_superuser)


        # Проверка генерации валидационных ошибок менеджера
        with self.assertRaises(ValueError):
            User.objects.create_user(email="") # Вызов ошибки ValueError

