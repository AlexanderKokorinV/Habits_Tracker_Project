"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


# Настройка метаданных API-документации
schema_view = get_schema_view(
   openapi.Info(
      title="Атомные привычки API",
      default_version='v1',
      description="Бэкенд-часть SPA веб-приложения для трекинга атомных привычек по Джеймсу Клиру",
      contact=openapi.Contact(email="admin@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path("admin/", admin.site.urls),

    path("users/", include("users.urls", namespace="users")),
    path("habits/", include("habits.urls", namespace="habits")),

    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema_swagger_ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema_redoc"),
]
