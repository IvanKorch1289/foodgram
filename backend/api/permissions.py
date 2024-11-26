from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешение, позволяющее владельцу объекта редактировать его,
    а остальным пользователям только читать.
    Анонимные пользователи могут только читать.
    Используется для пользователей
    """

    def has_permission(self, request, view):
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_authenticated)
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            request.method in SAFE_METHODS
            or obj == request.user
        )


class IsAuthorOrReadOnly(BasePermission):
    """
    Разрешение, позволяющее владельцу объекта редактировать его,
    а остальным пользователям только читать.
    Анонимные пользователи могут только читать.
    Используется для рецептов
    """

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user