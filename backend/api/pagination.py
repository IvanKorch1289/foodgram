from rest_framework.pagination import PageNumberPagination

from recipes.constants import DEFAULT_PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    """Пагинация для проекта."""

    page_size = DEFAULT_PAGE_SIZE
    page_size_query_param = "limit"
