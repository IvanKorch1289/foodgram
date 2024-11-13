from rest_framework import serializers

from recipes.constants import NON_VALID_USERNAME
from recipes.models import Ingredient, Recipe, Tag, User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tags."""

    id = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Tag


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredients."""

    id = serializers.IntegerField(
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Ingredient


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
        model = Recipe


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    class Meta:
        fields = '__all__'
        model = User

    def validate(self, data):
        if data.get('username') == NON_VALID_USERNAME:
            raise serializers.ValidationError(
                f'Использовать имя "{NON_VALID_USERNAME}" запрещено'
            )
        if User.objects.filter(username=data.get('username')).exists():
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        if User.objects.filter(email=data.get('email')).exists():
            raise serializers.ValidationError(
                'Пользователь с таким email уже существует'
            )
        return data
