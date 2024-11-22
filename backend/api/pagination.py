from recipes.constants import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class FoodgramPagination(LimitOffsetPagination):
    """Пагинация для проекта"""

    default_limit = DEFAULT_PAGE_SIZE
    max_limit = MAX_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
