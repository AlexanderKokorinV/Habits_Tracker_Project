from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """Разрешает (Create/PUT/PATCH/DELETE) только владельцу.
    Остальные могут только читать (GET), если привычка публичная.
    """
    def has_object_permission(self, request, view, obj):
        # Если метод безопасный (GET, HEAD, OPTIONS) и привычка публичная
        if request.method in permissions.SAFE_METHODS and obj.is_public:
            return True

        # Во всех остальных случаях пользователем должен быть создатель
        return obj.user == request.user