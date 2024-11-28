from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

from recipes.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_MEASURE_CHAR_FIELD,
    MAX_LENGTH_RECIPE_CHAR_FIELD,
    MAX_LENGTH_TAG_CHAR_FIELD,
    MAX_LENGTH_USER_CHAR_FIELD,
    MAX_LENGTH_USERNAME,
    MAX_STR,
    MIN_AMOUNT_VALUE,
    MIN_DURATION_VALUE,
    MIN_LENGTH_PASSWORD,
)


class User(AbstractUser):

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    password = models.CharField(
        max_length=MAX_LENGTH_USER_CHAR_FIELD,
        help_text="Пароль",
        validators=[MinLengthValidator(MIN_LENGTH_PASSWORD)],
    )
    avatar = models.ImageField(
        "Аватар", upload_to="static/", blank=True, null=True
    )
    email = models.CharField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name="Электронная почта",
        help_text="Уникальный адрес электронной почты",
    )
    first_name = models.CharField(
        "first name", max_length=MAX_LENGTH_USERNAME
    )
    last_name = models.CharField(
        "last name", max_length=MAX_LENGTH_USERNAME
    )

    class Meta:
        verbose_name = "Пользователи"
        verbose_name_plural = "Пользователь"
        ordering = ["username"]

    def __str__(self):
        return self.username[:MAX_STR]


class IdDateFieldModel(models.Model):

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = [
            "name",
        ]

    def __str__(self):
        return self.name[:MAX_STR]


class Tag(IdDateFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_TAG_CHAR_FIELD,
        help_text="Наименование",
        db_index=True
    )
    slug = models.SlugField()

    class Meta(IdDateFieldModel.Meta):
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Ingredient(IdDateFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_USER_CHAR_FIELD,
        help_text="Наименование",
        db_index=True
    )

    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_MEASURE_CHAR_FIELD, help_text="Единица измерения"
    )

    class Meta(IdDateFieldModel.Meta):
        default_related_name = "ingredients"
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient_constraint"
            )
        ]


class Recipe(IdDateFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_RECIPE_CHAR_FIELD,
        help_text="Наименование",
        db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Автор рецепта"
    )
    ingredients = models.ManyToManyField(
        Ingredient, verbose_name="Ингредиенты", through="RecipeIngredient"
    )
    is_in_shopping_cart = models.BooleanField(
        default=False, help_text="Находится ли в корзине"
    )
    text = models.CharField(
        help_text="Текст рецепта",
        max_length=MAX_LENGTH_RECIPE_CHAR_FIELD,
        blank=True,
        null=True,
    )
    cooking_time = models.PositiveSmallIntegerField(
        help_text="Время приготовления",
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                MIN_DURATION_VALUE,
                message="Значение не менее {MIN_DURATION_VALUE} минуты"
            )
        ],
    )
    image = models.ImageField(
        upload_to="static/", blank=True, null=True, help_text="Изображение"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Список тегов")

    class Meta(IdDateFieldModel.Meta):
        default_related_name = "recipes"
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"
        ordering = ["-created_at"]


class RecipeIngredient(models.Model):

    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT, verbose_name="Ингредиент"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        "Количество",
        validators=[
            MinValueValidator(
                MIN_AMOUNT_VALUE,
                f"Значение не должно быть меньше {MIN_AMOUNT_VALUE}",
            )
        ],
    )

    class Meta:
        default_related_name = "recipe_ingredients"
        constraints = [
            models.UniqueConstraint(
                fields=["ingredient", "recipe"], name="unique ingredient"
            )
        ]
        verbose_name = "Ингредиент в рецепте"
        verbose_name_plural = "Ингредиенты в рецепте"

    def __str__(self):
        name = f"{self.recipe.name} - {self.ingredient.name}"
        return name[:MAX_STR]


class RecipeUserFieldModel(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, verbose_name="Рецепт"
    )

    class Meta:
        abstract = True

    @classmethod
    def set_constraints(cls, model):
        model._meta.constraints.append(
            models.UniqueConstraint(
                fields=["user", "recipe"],
                name=f"{model._meta.app_label}_{cls.__name__}_user_recipe",
            )
        )

    @classmethod
    def setup(cls):
        cls.set_constraints(cls)

    def __str__(self):
        name = f"{self.user.username} - {self.recipe.name}"
        return name[:MAX_STR]


class FavouriteRecipe(RecipeUserFieldModel):

    class Meta(RecipeUserFieldModel.Meta):
        default_related_name = "favorite_recipes"
        verbose_name = "Избранный рецепт"
        verbose_name_plural = "Избранные рецепты"


class ShoppingBusket(RecipeUserFieldModel):

    class Meta(RecipeUserFieldModel.Meta):
        default_related_name = "shopping_buckets"
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="followers"
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_subscriber"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F("author")),
                name="unique_subscriber_himself",
            ),
        ]


ShoppingBusket.setup()
FavouriteRecipe.setup()
