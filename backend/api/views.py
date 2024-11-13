
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from django.urls import reverse
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    UserSerializer,
)
from api.filters import IngredientFilterSet
from recipes.models import Ingredient, Recipe, Tag, User


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer

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


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
        detail=False,
        url_path='me',
        permission_classes=(IsAuthenticated, )
    )
    def profile_update(self, request):
        serializer = UserSerializer(self.request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False,
        url_path='set_password',
        methods=['POST'],
        permission_classes=(IsAuthenticated, )
    )
    def set_password(self, request):
        pass

    @action(
        detail=False,
        url_path='subscriptions',
        permission_classes=(IsAuthenticated, )
    )
    def get_all_subscriptions(self, request):
        pass

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
