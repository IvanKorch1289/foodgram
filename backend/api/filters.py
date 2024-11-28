from django_filters.rest_framework import (
    AllValuesMultipleFilter,
    BooleanFilter,
    CharFilter,
    FilterSet,
)

from recipes.models import Ingredient, Recipe


class IngredientFilterSet(FilterSet):
    """Фильтр для модели Ingredient."""

    name = CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilterSet(FilterSet):
    """Фильтр для модели Recipe."""

    tags = AllValuesMultipleFilter(
        field_name="tags__slug",
        lookup_expr="contains"
    )
    is_favorited = BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = BooleanFilter(method="filter_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ["author", "tags"]

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            user = self.request.user
            return queryset.filter(favorite_recipes__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            user = self.request.user
            return queryset.filter(shopping_buckets__user=user)
        return queryset
