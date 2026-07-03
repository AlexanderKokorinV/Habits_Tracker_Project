from django.contrib.auth import get_user_model
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import generics, permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import UserProfileSerializer, UserRegisterSerializer

# Create your views here.

User = get_user_model()


class UserCreateAPIView(CreateAPIView):
    """Эндпоинт для регистрации нового пользователя с выдачей JWT-токенов"""

    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()

    # Ручное описание ответа для Swagger
    @swagger_auto_schema(
        responses={
            201: openapi.Response(
                description="Пользователь успешно создан. Возвращены JWT-токены.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "user": openapi.Schema(type=openapi.TYPE_OBJECT, description="Данные профиля"),
                        "refresh": openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh Token"),
                        "access": openapi.Schema(type=openapi.TYPE_STRING, description="JWT Access Token"),
                    },
                ),
            )
        }
    )
    def create(self, request, *args, **kwargs):
        """Переопределяет метод create для выдачи JWT-токенов"""

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Генерируем JWT-токены для нового пользователя
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "user": UserProfileSerializer(user).data,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Эндпоинт для просмотра и редактирования профиля текущего пользователя.
    URL: /api/users/profile/
    """

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Возвращает объект пользователя, который сделал запрос (из токена)"""
        return self.request.user
