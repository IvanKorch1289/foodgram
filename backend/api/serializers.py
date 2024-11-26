from django.db.models import Prefetch
from rest_framework import serializers

from api.custom_fields import Base64ImageField
from recipes.constants import NON_VALID_USERNAME
from recipes.models import FavouriteRecipe
from recipes.models import Follow
from recipes.models import Ingredient
from recipes.models import Recipe
from recipes.models import RecipeIngredient
from recipes.models import ShoppingBusket
from recipes.models import Tag
from recipes.models import User


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tags."""

    class Meta:
        fields = ("id", "name", "slug")
        model = Tag


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели User."""

    avatar = Base64ImageField(required=False)
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if self.context.get("request").user.is_authenticated:
            current_user = self.context.get("request").user
            if Follow.objects.filter(user=current_user, author=obj.pk).exists():
                return True
        return False

    class Meta:
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "avatar",
            "is_subscribed",
        )
        model = User

    def validate(self, data):
        errors = {}

        if data.get("username") == NON_VALID_USERNAME:
            errors["username"] = f'Имя "{NON_VALID_USERNAME}" запрещено'
        if not data.get("first_name"):
            errors["first_name"] = "Имя не должно быть пустым"
        if not data.get("last_name"):
            errors["last_name"] = ["Фамилия не должна быть пустой"]
        if User.objects.filter(username=data.get("username")).exists():
            errors["username"] = "Пользователь с таким username существует"
        if User.objects.filter(email=data.get("email")).exists():
            errors["email"] = "Пользователь с таким email уже существует"

        if errors:
            raise serializers.ValidationError(errors)

        return data


class UserAvatarSerializer(serializers.ModelSerializer):
    """Сериализатор модели User, используемый для аватара."""

    avatar = Base64ImageField(allow_null=True)

    class Meta:
        fields = ("avatar",)
        model = User


class FollowSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(queryset=User.objects.all(), slug_field="id")

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(source="recipes.count", read_only=True)

    class Meta:
        model = Follow
        fields = ("user", "recipes", "recipes_count", "author")

    def validate(self, data):
        user = self.initial_data.get("user")
        author = self.initial_data.get("author")

        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError("Вы уже подписаны на этого автора.")
        if user == author:
            raise serializers.ValidationError("Нельзя подписаться на себя.")
        return data

    def get_recipes(self, obj):
        request = self.context.get("request")
        limit = request.query_params.get("recipes_limit")
        if limit is not None:
            limit = int(limit)
        else:
            limit = None
        recipes = Recipe.objects.filter(author=obj.author)[:limit]
        serializer = RecipeSerializer(recipes, many=True)
        return serializer.data

    def to_representation(self, instance):
        representation = UserSerializer(instance.user, context=self.context).data
        recipes_data = self.get_recipes(instance)
        for recipe in recipes_data:
            del recipe["ingredients"]
            del recipe["tags"]
            del recipe["is_favorited"]
            del recipe["is_in_shopping_cart"]
            del recipe["author"]
            del recipe["text"]
        representation["recipes"] = recipes_data
        representation["recipes_count"] = len(recipes_data)
        return representation


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredients."""

    class Meta:
        fields = ("id", "name", "measurement_unit")
        model = Ingredient


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели RecipeIngredient."""

    id = serializers.SlugRelatedField(
        queryset=Ingredient.objects.all(), slug_field="id"
    )
    amount = serializers.IntegerField(required=True)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "amount")
        read_only_fields = ("recipe", "id")

    def validate_amount(self, value):
        if value < 1:
            raise serializers.ValidationError("Количество должно не меньше 1.")
        return value

    def to_representation(self, instance):
        amount = instance.recipe_ingredients.first().amount
        representation = {
            "id": instance.id,
            "name": instance.name,
            "measurement_unit": instance.measurement_unit,
            "amount": amount,
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
            "ingredients",
            "tags",
            "author",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
            "id",
        )
        read_only_fields = (
            "author",
            "id",
        )
        model = Recipe

    def validate(self, data):
        ingredients = data.get("ingredients")
        tags = data.get("tags")
        text = data.get("text")
        cooking_time = data.get("cooking_time")
        errors = {}
        if not ingredients:
            errors["ingredients"] = "Поле не может быть пустым."
        else:
            ingredient_list = [dict(ingredient)["id"] for ingredient in ingredients]
            if len(set(ingredient_list)) != len(ingredient_list):
                errors["ingredients"] = "Ингредиенты не должны повторяться."
        if not tags:
            errors["tags"] = "Поле не может быть пустым."
        elif len(set(tags)) != len(tags):
            errors["tags"] = "Тэги не должны повторяться."
        if not text:
            errors["text"] = "Поле не может быть пустым."
        if not cooking_time:
            errors["cooking_time"] = "Поле не может быть пустым."
        if errors:
            raise serializers.ValidationError(errors)
        return data

    def create(self, validated_data):
        ingredients_data = validated_data.pop("ingredients", [])
        tags_data = validated_data.pop("tags", [])
        recipe = Recipe.objects.create(**validated_data)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data["id"],
                amount=ingredient_data["amount"],
            )
        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop("ingredients", [])
        tags_data = validated_data.pop("tags", [])

        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.image = validated_data.get("image", instance.image)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        instance.save()

        if ingredients_data:
            instance.ingredients.clear()
            for ingredient_data in ingredients_data:
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient_data["id"],
                    amount=ingredient_data["amount"],
                )
        if tags_data:
            instance.tags.clear()
            instance.tags.set(tags_data)

        return instance

    def get_is_favorited(self, obj):
        if self.context.get("request").user.is_authenticated:
            current_user = self.context.get("request").user
            return obj.favorite_recipe.filter(user=current_user).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context.get("request").user.is_authenticated:
            current_user = self.context.get("request").user
            return obj.shopping_bucket.filter(user=current_user).exists()
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        tags_data = TagSerializer(instance.tags.all(), many=True).data
        author_data = UserSerializer(instance.author, context=self.context).data
        ingredients = instance.recipe_ingredients.prefetch_related(
            Prefetch("ingredient")
        )

        ingredient_list = [
            {
                "id": ingredient.ingredient.id,
                "name": ingredient.ingredient.name,
                "measurement_unit": ingredient.ingredient.measurement_unit,
                "amount": ingredient.amount,
            }
            for ingredient in ingredients
        ]

        representation["tags"] = tags_data
        representation["author"] = author_data
        representation["ingredients"] = ingredient_list

        return representation


class BusketFavouriteReprentSerializer(serializers.Serializer):

    def to_representation(self, instance):
        representation = RecipeSerializer(instance.recipe, context=self.context).data
        del representation["ingredients"]
        del representation["tags"]
        del representation["is_favorited"]
        del representation["is_in_shopping_cart"]
        del representation["author"]
        del representation["text"]
        return representation


class ShoppingBusketSerializer(
    BusketFavouriteReprentSerializer, serializers.ModelSerializer
):
    class Meta:
        model = ShoppingBusket
        fields = ("user", "recipe")

    def validate(self, data):
        if ShoppingBusket.objects.filter(
            user=data.get("user"), recipe=data.get("recipe")
        ).exists():
            raise serializers.ValidationError("Уже добавлен в Корзину.")
        return data


class FavouriteRecipeSerializer(
    BusketFavouriteReprentSerializer, serializers.ModelSerializer
):

    class Meta:
        model = FavouriteRecipe
        fields = (
            "user",
            "recipe",
        )

    def validate(self, data):
        if FavouriteRecipe.objects.filter(
            user=data.get("user"), recipe=data.get("recipe")
        ).exists():
            raise serializers.ValidationError("Уже добавлен в Избранное.")
        return data
