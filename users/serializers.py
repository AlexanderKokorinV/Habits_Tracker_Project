from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации новых пользователей"""

    password = serializers.CharField(write_only=True, min_length=8)  # пароль только для записи

    class Meta:
        model = User
        fields = ["id", "email", "password", "phone_number", "city", "avatar"]
        extra_kwargs = {
            "email": {"error_messages": {"unique": "Пользователь с таким Email уже зарегистрирован в системе."}}
        }

    def create(self, validated_data):
        """Метод создания с хешированием пароля перед сохранением в БД"""

        try:
            user = User.objects.create_user(**validated_data)
            return user
        except Exception as e:
            raise ValidationError({"error": f"Не удалось завершить регистрацию: {str(e)}"})


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для безопасного отображения и редактирования профиля текущего пользователя"""

    class Meta:
        model = User
        fields = ["id", "email", "telegram_chat_id", "phone_number", "city", "avatar"]
        read_only_fields = ["id", "email"]  # Запрещаем изменять id и email через этот эндпоинт в целях безопасности
