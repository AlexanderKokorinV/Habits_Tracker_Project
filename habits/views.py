from django.db.models import Q
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from habits.models import Habit, HabitLog
from habits.pagination import HabitPagination
from habits.permissions import IsOwnerOrReadOnly
from habits.serializers import HabitSerializer

# Create your views here.


class HabitViewSet(viewsets.ModelViewSet):
    """Эндпоинты для работы с привычками (CRUD, Public)"""

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        """
        Текущий пользователь видит:
        - все собственные привычки (полезные и приятные)
        - чужие привычки, если они отмечены как публичные
        """
        user = self.request.user
        return Habit.objects.filter(Q(user=user) | Q(is_public=True)).order_by("id")

    def perform_create(self, serializer):
        """Автоматически привязываем создаваемую привычку к текущему пользователю"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def public(self, request):
        """Список только публичных привычек других пользователей (/habits/public/)"""
        public_habits = Habit.objects.filter(is_public=True).exclude(user=request.user).order_by("id")

        page = self.paginate_queryset(public_habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)

    # Эндпоинт отметки выполнения для SPA (вызывает создание HabitLog)
    @swagger_auto_schema(
        method="post", responses={200: openapi.Response(description="Привычка успешно отмечена выполненной")}
    )
    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def check(self, request, pk=None):
        """Отметка о выполнении привычки пользователем в SPA (/habits/{id}/check/)"""
        habit = self.get_object()

        # Нельзя отметить чужую привычку
        if habit.user != request.user:
            return Response({"error": "Это не ваша привычка"}, status=status.HTTP_403_FORBIDDEN)

        # Создание лога выполнения в базе данных PostgreSQL
        log = HabitLog.objects.create(habit=habit)
        return Response(
            {"status": "Привычка успешно отмечена выполненной!", "log_id": log.id}, status=status.HTTP_200_OK
        )
