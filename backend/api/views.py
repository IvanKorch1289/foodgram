from collections import defaultdict
from io import StringIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser.views import UserViewSet as djoser_user
from pyshorteners import Shortener
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework.reverse import reverse

from api.filters import IngredientFilterSet, RecipeFilterSet
from api.permissions import IsOwnerOrReadOnly, IsAuthorOrReadOnly
from api.pagination import FoodgramPagination
from api.serializers import (FavouriteRecipeSerializer, FollowSerializer,
                             IngredientSerializer, RecipeSerializer,
                             ShoppingBusketSerializer, TagSerializer,
                             UserAvatarSerializer, UserSerializer)
from recipes.models import (FavouriteRecipe, Follow, Ingredient, Recipe,
                            ShoppingBusket, Tag, User)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilterSet
    filter_backends = [DjangoFilterBackend]
    pagination_class = FoodgramPagination
    permission_classes = (IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


    @action(detail=True, url_path="get-link")
    def get_short_link(self, request, pk=None):
        detail_url = reverse("recipes-detail", args=[pk], request=request)
        full_url = request.build_absolute_uri(detail_url)
        shortener = Shortener()
        shortened_url = shortener.tinyurl.short(full_url)
        return Response({"short-link": shortened_url})

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="shopping_cart",
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            serializer = ShoppingBusketSerializer(
                data={"user": user.id, "recipe": recipe.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            try:
                busket = get_object_or_404(
                    ShoppingBusket, user=user, recipe=recipe
                )
                busket.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shopping_cart",
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_list(self, request):
        shopping_buskets = ShoppingBusket.objects.filter(
            user=self.request.user
        ).select_related("recipe")
        file_buffer = StringIO()
        ingredients = defaultdict(int)
        for busket in shopping_buskets:
            for item in busket.recipe.recipe_ingredients.all():
                ingredients[item.ingredient.name] += item.amount
        for name, amount in ingredients.items():
            file_buffer.write(f"{name} — {amount}g\n")
        file_buffer.seek(0)
        file_content = file_buffer.read()
        header = {"Content-Disposition": 'attachment; filename="foodgram.txt"'}
        return HttpResponse(
            file_content, content_type="text/plain", headers=header
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        if request.method == "POST":
            serializer = FavouriteRecipeSerializer(
                data={"user": user.id, "recipe": recipe.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            try:
                favourite = get_object_or_404(
                    FavouriteRecipe, user=user, recipe=recipe
                )
                favourite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)


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
    pagination_class = FoodgramPagination
    permission_classes = (IsOwnerOrReadOnly, )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

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
        methods=["GET"],
        url_path="me",
        permission_classes=(IsAuthenticated, )
    )
    def get_profile(self, request):
        return super().me(request)

    @action(
        detail=False,
        methods=["PUT", "DELETE"],
        url_path="me/avatar",
        permission_classes=(IsAuthenticated,)
    )
    def avatar(self, request):
        user = request.user
        if request.method == "PUT":
            serializer = UserAvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == "DELETE":
            try:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        permission_classes=(IsAuthenticated,)
    )
    def get_all_subscriptions(self, request):
        follows = request.user.following.all()
        authors = follows.values_list("author", flat=True)
        recipes_limit = request.query_params.get("recipes_limit")
        if recipes_limit is not None:
            try:
                recipes_limit = int(recipes_limit)
            except ValueError:
                pass
            else:
                recipes = Recipe.objects.filter(author__in=authors).distinct()
                if recipes.exists():
                    recipes = recipes[:recipes_limit]
        page = self.paginate_queryset(follows)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(
            follows, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == 'POST':
            recipes_limit = request.query_params.get('recipes_limit')
            if recipes_limit is not None:
                try:
                    recipes_limit = int(recipes_limit)
                except ValueError:
                    recipes_limit = None

            recipes = Recipe.objects.filter(author=author)
            if recipes_limit:
                recipes = recipes[:recipes_limit]

            serializer = FollowSerializer(
                data={'user': user.id, 'author': author.id},
                context={"request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            try:
                follow = get_object_or_404(Follow, user=user, author=author)
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
