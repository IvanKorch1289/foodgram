from django.contrib.auth.admin import UserAdmin, admin
from django.utils.html import format_html
from recipes.models import Ingredient, Recipe, Tag, User


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'tag_list', 'favorites_count')
    search_fields = ['name', 'author__username']
    list_filter = ['tags']

    def tag_list(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())

    tag_list.short_description = 'Теги'

    def favorites_count(self, obj):
        count = obj.favorited_by.count()
        return format_html(
            '<span style="color: green;">'
            'Добавлений в избранное: {}</span>',
            count,
        )

    favorites_count.short_description = 'Количество добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    search_fields = ('username', 'email')
