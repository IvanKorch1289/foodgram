from django.contrib.auth.admin import UserAdmin, admin
from django.utils.html import format_html

from recipes.models import Ingredient, Recipe, Tag, User


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    search_fields = ["slug"]


class TagInline(admin.TabularInline):
    model = Recipe.tags.through
    extra = 0


class IngredientInline(admin.StackedInline):
    model = Recipe.ingredients.through
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [TagInline, IngredientInline]
    list_display = ("name", "author", "tag_list", "favorites_count")
    search_fields = ["name", "author__username"]
    list_filter = ["tags"]

    def tag_list(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())

    tag_list.short_description = "Теги"

    def favorites_count(self, obj):
        count = obj.favorite_recipes.count()
        return format_html(
            '<span style="color: green;">' "Добавлений в избранное: {}</span>",
            count,
        )

    favorites_count.short_description = "Количество добавлений в избранное"


@admin.register(User)
class FoodgramUserAdmin(UserAdmin):
    search_fields = ("username", "email")

    def followers_count(self, obj):
        count = obj.followers.count()
        return format_html(
            '<span style="color: green;">' "Подписчиков: {}</span>",
            count,
        )

    followers_count.short_description = "Количество подписчиков"

    def recipes_count(self, obj):
        count = obj.recipes.count()
        return format_html(
            '<span style="color: green;">' "Рецептов: {}</span>",
            count,
        )

    recipes_count.short_description = "Количество рецептов"
