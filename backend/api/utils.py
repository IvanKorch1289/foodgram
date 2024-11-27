from collections import defaultdict
from io import StringIO

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from api.serializers import FavouriteRecipeSerializer, ShoppingBusketSerializer
from recipes.models import Recipe, RecipeIngredient, ShoppingBusket


def write_to_file(data):
    file_buffer = StringIO()
    ingredients = defaultdict(int)

    for name, amount in data:
        ingredients[name] += amount
        file_buffer.write(f"{name} — {amount}g\n")

    file_buffer.seek(0)
    return file_buffer.read()


def call_serializer(model, request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    user = request.user
    data = {"user": user.id, "recipe": recipe.id}
    context = {"request": request}
    if request.method == "POST":
        if model == ShoppingBusket:
            serializer = ShoppingBusketSerializer(
                data=data, context=context,
            )
        else:
            serializer = FavouriteRecipeSerializer(
                data={"user": user.id, "recipe": recipe.id},
                context={"request": request},
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        try:
            obj = get_object_or_404(
                model, user=user, recipe=recipe
            )
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as ex:
            return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
