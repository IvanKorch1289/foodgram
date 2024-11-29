from collections import defaultdict
from io import StringIO

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response

from recipes.models import Recipe


def write_to_file(data):
    file_buffer = StringIO()
    ingredients = defaultdict(int)

    for name, amount in data:
        ingredients[name] += amount
        file_buffer.write(f"{name} — {amount}g\n")

    file_buffer.seek(0)
    file = file_buffer.read()
    header = {"Content-Disposition": 'attachment; filename="foodgram.txt"'}

    return HttpResponse(
        file, content_type="text/plain", headers=header
    )


def call_serializer(serializer, request, recipe_id):
    recipe = get_object_or_404(Recipe, pk=recipe_id)
    user = request.user
    data = {"user": user.id, "recipe": recipe.id}
    context = {"request": request}
    if request.method == "POST":
        serializer = serializer(
            data=data, context=context,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    try:
        obj = get_object_or_404(
            serializer.Meta.model, user=user, recipe=recipe
        )
        obj.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Exception as ex:
        return Response(str(ex), status=status.HTTP_400_BAD_REQUEST)
