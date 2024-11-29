from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsOwner(BasePermission):
    """
    Разрешение, позволяющее владельцу объекта редактировать

    Автор объекта может редактировать и удалять его, для
    остальных доступно только чтение.
    """

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj == request.user
            or obj.author == request.user)
