from django_filters.rest_framework import BooleanFilter
from django_filters.rest_framework import CharFilter
from django_filters.rest_framework import FilterSet
from django_filters.rest_framework import ModelChoiceFilter
from django_filters.rest_framework import ModelMultipleChoiceFilter
from recipes.models import Ingredient
from recipes.models import Recipe
from recipes.models import Tag
from recipes.models import User


class IngredientFilterSet(FilterSet):
    """Фильтр для модели Ingredient."""

    name = CharFilter(lookup_expr="istartswith")

    class Meta:
        model = Ingredient
        fields = ("name",)


class RecipeFilterSet(FilterSet):
    """Фильтр для модели Recipe."""

    author = ModelChoiceFilter(
        field_name="author", to_field_name="id", queryset=User.objects.all()
    )
    tags = ModelMultipleChoiceFilter(
        field_name="tags__slug", to_field_name="slug", queryset=Tag.objects.all()
    )
    is_favorited = BooleanFilter(method="filter_is_favorited")
    is_in_shopping_cart = BooleanFilter(method="filter_is_in_shopping_cart")

    class Meta:
        model = Recipe
        fields = ["author", "tags"]

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            user = self.request.user
            return queryset.filter(favorite_recipe__user=user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            user = self.request.user
            return queryset.filter(shopping_bucket__user=user)
        return queryset
