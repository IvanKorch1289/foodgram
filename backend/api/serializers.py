from rest_framework import serializers

from api.custom_fields import Base64ImageField
from recipes.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USERNAME,
    NON_VALID_USERNAME
)
from recipes.models import FavoriteRecipe, Ingredient, Recipe, RecipeIngredient, ShoppingBusket, Follow, Tag, User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tags."""

    class Meta:
        fields = ('id', 'name', 'slug')
        model = Tag


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        current_user = self.context.get('request').user
        if Follow.filter(user=current_user, author=obj.pk):
            return True
        return False

    class Meta:
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'avatar')
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


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор модели User, используемый для аватара."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        fields = ('avatar')
        model = User


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredients."""

    class Meta:
        fields = ('id', 'name', 'measurement_unit')
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели RecipeIngredient."""

    id = serializers.SlugRelatedField(
        queryset=Ingredient.objects.all(),
        slug_field='id'
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')
        read_only_fields = ('recipe', 'id')

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError('Количество должно не меньше 1.')
        return value

    def to_representation(self, instance):
        recipe_ingredient = instance.recipe_ingredients.first()
        print(recipe_ingredient)
        representation = {
            'id': instance.id,
            'amount': recipe_ingredient.amount
        }
        return representation


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор модели Recipes."""

    ingredients = RecipeIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects.all())
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'ingredients', 'tags', 'author',
            'is_favorited', 'is_in_shopping_cart', 'name',
            'image', 'text', 'cooking_time', 'id'
        )
        read_only_fields = ('author', 'id', )
        model = Recipe

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        tags_data = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
        recipe.tags.set(tags_data)
        return recipe

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.favorite.filter(user=request.user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.shopping_bucket.filter(user=request.user).exists()
        return False


class FavoriteRecipeSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    recipe = serializers.PrimaryKeyRelatedField(queryset=Recipe.objects.all())

    class Meta:
        model = FavoriteRecipe
        fields = ('user', 'recipe')


class ShoppingBusketSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
    recipes = serializers.PrimaryKeyRelatedField(many=True, queryset=Recipe.objects.all())

    class Meta:
        model = ShoppingBusket
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Follow
        fields = ('user', 'author')
