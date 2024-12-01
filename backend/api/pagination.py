from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from recipes.constants import DEFAULT_PAGE_SIZE


class FoodgramPagination(LimitOffsetPagination):
    """Пагинация для проекта."""

    default_limit = DEFAULT_PAGE_SIZE
    page_size = DEFAULT_PAGE_SIZE

    def get_paginated_response(self, data):
        return Response(
            {
                "count": self.count,
                "next": self.get_next_link(),
                "previous": self.get_previous_link(),
                "results": data,
            }
        )
