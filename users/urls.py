from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.views import UserCreateAPIView, UserProfileView

urlpatterns = [
    # Регистрация (POST) и профиль текущего пользователя (GET, PUT/PATCH)
    path("register/", UserCreateAPIView.as_view(), name="user_register"),
    path("profile/", UserProfileView.as_view(), name="user_profile"),

    # Авторизация через Simple-JWT и обновление access-токена по refresh-токену
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]