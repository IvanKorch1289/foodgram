from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from backend.recipes.constants import (
    MAX_LENGTH_256_CHAR_FIELD,
    MAX_LENGTH_32_CHAR_FIELD,
    MAX_LENGTH_64_CHAR_FIELD,
    MIN_DURATION_VALUE
)


User = get_user_model()


class BaseFieldModel(models.Model):

    id = models.IntegerField(primary_key=True)
    name = models.CharField(
        max_length=MAX_LENGTH_256_CHAR_FIELD,
        help_text='Наименование',
        db_index=True
    )
    is_active = models.BooleanField(default=True)
    create_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['name', ]

    def __str__(self):
        return self.name


class Tags(BaseFieldModel):

    name = models.CharField(
        max_length=MAX_LENGTH_32_CHAR_FIELD,
        help_text='Наименование',
        db_index=True
    )
    slug = models.SlugField()

    class Meta(BaseFieldModel.Meta):
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Ingredients(BaseFieldModel):

    measurement_unit = models.CharField(
        max_length=MAX_LENGTH_64_CHAR_FIELD,
        help_text='Единица измерения'
    )

    class Meta(BaseFieldModel.Meta):
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        unique_together = ('name', 'measurement_unit')


class Recipes(BaseFieldModel):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        Ingredients,
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
    text = models.StringField(
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
        Tags,
        verbose_name='Список тегов',
        blank=True,
        null=True
    )

    class Meta(BaseFieldModel.Meta):
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
