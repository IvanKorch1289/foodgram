from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models

from recipes.constants import (
    MAX_LENGTH_32_CHAR_FIELD,
    MAX_LENGTH_64_CHAR_FIELD,
    MAX_LENGTH_128_CHAR_FIELD,
    MAX_LENGTH_256_CHAR_FIELD,
    MAX_LENGTH_EMAIL,
    MIN_AMOUNT_VALUE,
    MIN_DURATION_VALUE,
)
from recipes.validators import validate_username


class User(AbstractUser):

    password = models.CharField(
        max_length=MAX_LENGTH_128_CHAR_FIELD,
        help_text="Пароль",
        validators=[MinLengthValidator(8), validate_username],
    )
    avatar = models.ImageField("Аватар", upload_to="avatars/", blank=True, null=True)
    email = models.CharField(
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        verbose_name="Электронная почта",
        help_text="Уникальный адрес электронной почты",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        default_related_name = "users"
        verbose_name = "Пользователи"
        verbose_name_plural = "Пользователь"
        ordering = ["username"]


class BaseFieldModel(models.Model):

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = [
            "name",
        ]

    def __str__(self):
        return self.name


class Tag(BaseFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_32_CHAR_FIELD, help_text="Наименование", db_index=True
    )
    slug = models.SlugField()

    class Meta(BaseFieldModel.Meta):
        default_related_name = "tags"
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


class Ingredient(BaseFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_128_CHAR_FIELD, help_text="Наименование", db_index=True
    )

    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_64_CHAR_FIELD, help_text="Единица измерения"
    )

    class Meta(BaseFieldModel.Meta):
        default_related_name = "ingredients"
        verbose_name = "Ингредиент"
        verbose_name_plural = "Ингредиенты"
        unique_together = ("name", "measurement_unit")


class Recipe(BaseFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_256_CHAR_FIELD, help_text="Наименование", db_index=True
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
        max_length=MAX_LENGTH_256_CHAR_FIELD,
        blank=True,
        null=True,
    )
    cooking_time = models.IntegerField(
        help_text="Время приготовления",
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                MIN_DURATION_VALUE, message="Значение не может быть меньше 1 минуты"
            )
        ],
    )
    image = models.ImageField(
        upload_to="static/", blank=True, null=True, help_text="Изображение"
    )
    tags = models.ManyToManyField(Tag, verbose_name="Список тегов")

    class Meta(BaseFieldModel.Meta):
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


class FavouriteRecipe(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Отметивший пользователь"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепты")

    class Meta:
        default_related_name = "favorite_recipe"
        verbose_name = "Избранные рецепты"
        verbose_name_plural = "Избранные рецепты"
        constraints = [
            models.UniqueConstraint(fields=["user", "recipe"], name="unique_favorite")
        ]


class ShoppingBusket(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, verbose_name="Рецепты")

    class Meta:
        default_related_name = "shopping_bucket"
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "recipe"], name="unique_shopping_cart"
            )
        ]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")

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
