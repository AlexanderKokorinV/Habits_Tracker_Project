from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User

# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Убираем username из отображения и фильтров
    list_display = ("id", "email", "phone_number", "city", "telegram_chat_id", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")

    # Указываем, по каким полям искать (поиск по email вместо username)
    search_fields = ("email", "phone_number", "city")
    ordering = ("email",)

    # Поля, которые будут видны при создании пользователя через админку
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password", "phone_number", "city", "telegram_chat_id", "avatar"),
            },
        ),
    )

    # Поля, которые видны при редактировании существующего пользователя
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Личные данные", {"fields": ("phone_number", "city", "avatar", "telegram_chat_id")}),
        ("Права доступа", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
