from api.filters import IngredientFilterSet, RecipeFilterSet
from api.pagination import FoodgramPagination
from api.serializers import (FavouriteRecipeSerializer, FollowSerializer,
                             IngredientSerializer, RecipeSerializer,
                             ShoppingBusketSerializer, TagSerializer,
                             UserAvatarSerializer, UserSerializer)
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser.views import UserViewSet as djoser_user
from recipes.models import (FavouriteRecipe, Follow, Ingredient, Recipe,
                            ShoppingBusket, Tag, User)
from rest_framework import status, viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilterSet
    pagination_class = FoodgramPagination
    http_method_names = ["GET", "POST", "PATCH", "DELETE"]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, url_path="get-link")
    def get_recipe_link(self, request, pk=None):
        original_url = request.META.get("HTTP_REFERER")
        if original_url is None:
            url = reverse("api:recipe-detail", kwargs={"pk": pk})
            original_url = request.build_absolute_uri(url)
        data = {}
        data["short-link"] = original_url
        return Response(data)

    @action(detail=False, url_path="download_shopping_cart/")
    def download_shopping_cart(self, request):
        pass

    @action(detail=True, methods=["POST"], url_path="shopping_cart")
    def add_recipe_to_shopping_cart(self, request, pk=None):
        pass

    @action(detail=True, methods=["DELETE"], url_path="shopping_cart")
    def delete_recipe_from_shopping_cart(self, request, pk=None):
        pass

    @action(detail=True, methods=["POST", "DELETE"], url_path="favorite")
    def favourite(self, request, pk=None):
        recipe = self.get_object()
        user = request.user
        if request.method == "POST":
            if FavouriteRecipe.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {"error": "Рецепт уже добавлен в избранное."},
                    status=status.HTTP_409_CONFLICT,
                )

            favourite = FavouriteRecipe.objects.create(user=user, recipe=recipe)
            serializer = FavouriteRecipeSerializer(favourite)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            favourite = get_object_or_404(FavouriteRecipe, user=user, recipe=recipe)
            favourite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Tags."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    http_method_names = ["GET"]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для модели Ingredients."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilterSet
    http_method_names = ["GET"]


class UserViewSet(djoser_user):
    """Вьюсет для модели User."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = FoodgramPagination
    http_method_names = ["GET", "POST"]

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

    @action(detail=False, methods=["GET"], url_path="me")
    def get_profile(self, request):
        return super().me(request)

    @action(detail=False, methods=["PUT"], url_path="me/avatar")
    def set_avatar(self, request):
        user = request.user
        serializer = UserAvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["DELETE"], url_path="me/avatar")
    def delete_avatar(self, request):
        user = request.user
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        permission_classes=[IsAuthenticated],
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
            serializer = FollowSerializer(page, many=True, context={"request": request})
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(follows, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        user = request.user
        if request.method == "POST":
            serializer = FollowSerializer(data={"user": user.id, "author": author.id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == "DELETE":
            follow = get_object_or_404(Follow, user=user, author=author)
            follow.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
