from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from djoser.conf import settings
from djoser.views import UserViewSet as djoser_user
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from api.serializers import (
    FavoriteRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    UserAvatarSerializer,
    UserSerializer,
    ShoppingBusketSerializer
)
from api.filters import IngredientFilterSet, RecipeFilterSet
from api.pagination import FoodgramPagination
from recipes.models import FavoriteRecipe, Ingredient, Recipe, Tag, User, ShoppingBusket


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilterSet
    pagination_class = FoodgramPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, url_path='get-link')
    def get_recipe_link(self, request, pk=None):
        original_url = request.META.get('HTTP_REFERER')
        if original_url is None:
            url = reverse('api:recipe-detail', kwargs={'pk': pk})
            original_url = request.build_absolute_uri(url)
        data = {}
        data['short-link'] = original_url
        return Response(data)

    @action(detail=False, url_path='download_shopping_cart/')
    def download_shopping_cart(self, request):
        pass

    @action(detail=True, methods=['POST'], url_path='shopping_cart')
    def add_recipe_to_shopping_cart(self, request, pk=None):
        pass

    @action(detail=True, methods=['DELETE'], url_path='shopping_cart')
    def delete_recipe_from_shopping_cart(self, request, pk=None):
        pass

    @action(detail=True, methods=['POST'], url_path='favourite')
    def add_recipe_to_favourite(self, request, pk=None):
        pass

    @action(detail=True, methods=['DELETE'], url_path='favourite')
    def delete_recipe_from_favourite(self, request, pk=None):
        pass


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilterSet


class UserViewSet(djoser_user):
    """Вьюсет для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == "create":
            if settings.USER_CREATE_PASSWORD_RETYPE:
                return settings.SERIALIZERS.user_create_password_retype
            return settings.SERIALIZERS.user_create
        if self.action == "set_password":
            if settings.SET_PASSWORD_RETYPE:
                return settings.SERIALIZERS.set_password_retype
            return settings.SERIALIZERS.set_password
        return self.serializer_class

    @action(
        detail=False,
        methods=['GET'],
        url_path='me'
    )
    def get_profile(self, request):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated, )
    )
    def get_all_subscriptions(self, request):
        pass

    @action(
        detail=False,
        methods=['PUT'],
        url_path='me/avatar'
    )
    def set_avatar(self, request):
        instance = self.get_instance()
        serializer = UserAvatarSerializer(
            instance, 
            data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer

    @action(
        detail=True,
        methods=['POST'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated, )
    )
    def subscribe(self, request, pk=None):
        pass

    @action(
        detail=True,
        methods=['DELETE'],
        url_path='subscribe',
        permission_classes=(IsAuthenticated, )
    )
    def unsubscribe(self, request, pk=None):
        pass


class FavoriteRecipeViewset(viewsets.ModelViewSet):
    queryset = FavoriteRecipe.objects.all()
    serializer_class = FavoriteRecipeSerializer


class ShoppingBusketViewset(viewsets.ModelViewSet):
    queryset = ShoppingBusket.objects.all()
    serializer_class = ShoppingBusketSerializer