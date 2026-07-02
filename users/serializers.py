from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from users.managers import CustomUserManager

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

        assert isinstance(User.objects, CustomUserManager)  # Техническая строка для линтера

        try:
            user = User.objects.create(
                email=validated_data.get("email"),
                password=validated_data.get("password"),
                phone_number=validated_data.get("phone_number", None),
                city=validated_data.get("city", None),
                avatar=validated_data.get("avatar", None),
            )
            return user
        except IntegrityError as e:
            raise ValidationError({"error": f"Не удалось завершить регистрацию из-за системной ошибки: {str(e)}"})
