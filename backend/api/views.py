from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
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
from api.pagination import FoodgramPagination
from api.permissions import IsOwner
from api.serializers import (
    FollowSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
    UserAvatarSerializer,
    UserSerializer
)
from api.utils import write_to_file, call_serializer
from recipes.models import (
    FavouriteRecipe,
    Follow,
    Ingredient,
    Recipe,
    ShoppingBusket,
    Tag,
    User
)


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Recipes."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilterSet
    filter_backends = [DjangoFilterBackend]
    pagination_class = FoodgramPagination
    permission_classes = (IsOwner, IsAuthenticatedOrReadOnly)

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
        permission_classes=(IsAuthenticated,),
    )
    def shopping_cart(self, request, pk=None):
        return call_serializer(ShoppingBusket, request, pk)

    @action(
        detail=False,
        methods=["GET"],
        url_path="download_shopping_cart",
        permission_classes=(IsAuthenticated,),
    )
    def download_shopping_list(self, request):
        shopping_buskets = ShoppingBusket.objects.filter(
            user=self.request.user
        ).select_related("recipe").values_list(
            'recipe__recipe_ingredients__ingredient__name',
            'recipe__recipe_ingredients__amount'
        )

        data = [(name, amount) for name, amount in shopping_buskets]
        file = write_to_file(data)
        header = {"Content-Disposition": 'attachment; filename="foodgram.txt"'}

        return HttpResponse(
            file, content_type="text/plain", headers=header
        )

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="favorite",
        permission_classes=(IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        return call_serializer(FavouriteRecipe, request, pk)


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
    permission_classes = (IsAuthenticatedOrReadOnly, IsOwner)

    @action(
        detail=False,
        methods=["GET"],
        url_path="me",
        permission_classes=(IsAuthenticated,),
    )
    def get_profile(self, request):
        return super().me(request)

    @action(
        detail=False,
        methods=["PUT", "DELETE"],
        url_path="me/avatar",
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        user = request.user
        if request.method == "PUT":
            serializer = UserAvatarSerializer(user, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            try:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=["GET"],
        url_path="subscriptions",
        permission_classes=(IsAuthenticated,),
    )
    def get_all_subscriptions(self, request):
        follows = request.user.following.all()
        authors = follows.values_list("author", flat=True)
        page = self.paginate_queryset(follows)
        if page is not None:
            serializer = FollowSerializer(
                page, many=True, context={"request": request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = FollowSerializer(
            follows, many=True, context={"request": request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        url_path="subscribe",
        permission_classes=(IsAuthenticated,),
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, pk=id)
        user = request.user
        if request.method == "POST":
            serializer = FollowSerializer(
                data={"user": user.id, "author": author.id},
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            try:
                follow = get_object_or_404(Follow, user=user, author=author)
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Exception as ex:
                return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
