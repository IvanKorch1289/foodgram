from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MinLengthValidator
from django.db import models

from recipes.constants import (
    MAX_LENGTH_256_CHAR_FIELD,
    MAX_LENGTH_32_CHAR_FIELD,
    MAX_LENGTH_64_CHAR_FIELD,
    MIN_DURATION_VALUE
)
from recipes.validators import validate_username


class User(AbstractUser):

    password = models.CharField(
        max_length=128,
        help_text='Пароль',
        validators=[
            MinLengthValidator(8),
            validate_username
        ]
    )
    avatar = models.ImageField(
        help_text='Аватар',
        blank=True,
        null=True
    )
    subscriptions = models.ManyToManyField(
        related_name='subscriptions',
        to='recipes.User',
        verbose_name='Подписки',
        blank=True,
        null=True
    )

    class Meta:
        default_related_name = 'users'
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователь'
        ordering = ['username']


class BaseFieldModel(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(
        max_length=MAX_LENGTH_256_CHAR_FIELD,
        help_text='Наименование',
        db_index=True
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Tag(BaseFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_32_CHAR_FIELD,
        help_text='Наименование',
        db_index=True
    )
    slug = models.SlugField()

    class Meta(BaseFieldModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredient(BaseFieldModel):

    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_64_CHAR_FIELD,
        help_text='Единица измерения'
    )

    class Meta(BaseFieldModel.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = ('name', 'measurement_unit')


class Recipe(BaseFieldModel):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='Ингредиенты'
    )
    is_favorited = models.BooleanField(
        default=False,
        help_text='Находится ли в избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        default=False,
        help_text='Находится ли в корзине'
    )
    text = models.CharField(
        help_text='Текст рецепта',
        max_length=MAX_LENGTH_256_CHAR_FIELD,
        blank=True,
        null=True
    )
    cooking_time = models.DurationField(
        help_text='Время приготовления',
        blank=True,
        null=True,
        validators=[
            MinValueValidator(
                MIN_DURATION_VALUE,
                message='Значение не может быть меньше 1 минуты'
            )
        ],
    )
    image = models.ImageField(
        upload_to='static/',
        blank=True,
        null=True,
        help_text='Изображение'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Список тегов'
    )

    class Meta(BaseFieldModel.Meta):
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']
