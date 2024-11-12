from rest_framework import serializers

from recipes.models import Ingredients, Recipes, Tags


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tags."""

    id = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Tags


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredients."""

    id = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Ingredients


class RecipeSerializer(serializers.Serializer):
    """Сериализатор модели Recipes."""

    id = serializers.IntegerField(
        read_only=True
    )
    author_id = serializers.IntegerField(
        read_only=True
    )
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        fields = '__all__'
        model = Recipes
