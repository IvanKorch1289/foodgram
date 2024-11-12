
from django.contrib.auth import get_user_model
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from api.serializers import (
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer
)
from recipes.models import Ingredients, Recipes, Tags

User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes."""

    queryset = Recipes.objects.all()
    serializer_class = RecipeSerializer


class TagViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Tags."""

    queryset = Tags.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Ingredients."""

    queryset = Ingredients.objects.all()
    serializer_class = IngredientSerializer
