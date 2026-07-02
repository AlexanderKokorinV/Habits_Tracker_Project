from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.response import Response

from habits.models import Habit
from habits.pagination import HabitPagination
from habits.permissions import IsOwnerOrReadOnly
from habits.serializers import HabitSerializer


# Create your views here.

class HabitViewSet(viewsets.ModelViewSet):
    """Эндпоинты для работы с привычками (CRUD + Public)"""

    serializer_class = HabitSerializer
    pagination_class = HabitPagination
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)

    def get_queryset(self):
        """
        Текущий пользователь видит:
        - все собственные привычки (полезные и приятные)
        - чужие привычки, если они отмечены как публичные
        """
        user = self.request.user
        return Habit.objects.filter(Q(user=user) | Q(is_public=True).order_by("id"))

    def perform_create(self, serializer):
        """Автоматически привязываем создаваемую привычку к текущему пользователю"""
        serializer.save(user=self.request.user)


    def public(self, request):
        """Список только публичных привычек других пользователей (/habits/public/)"""
        public_habits = Habit.objects.filter(is_public=True).exclude(user=request.user).order_by("id")

        page = self.paginate_queryset(public_habits)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(public_habits, many=True)
        return Response(serializer.data)