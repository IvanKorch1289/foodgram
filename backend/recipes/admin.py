from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.shortcuts import get_object_or_404

from recipes.constants import SHORT_TITLE
from recipes.models import Ingredient, Recipe, Tag, User


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")

    @admin.display(description="Тэг")
    def short_name(self, obj):
        if len(obj.name) > SHORT_TITLE:
            return f"{obj.name[:SHORT_TITLE]}..."
        return obj.name


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name",)

    @admin.display(description="Ингредиент")
    def short_name(self, obj):
        if len(obj.name) > SHORT_TITLE:
            return f"{obj.name[:SHORT_TITLE]}..."
        return obj.name


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets
    fieldsets[0][1]["fields"] = fieldsets[0][1]["fields"] + (
        "role",
        "bio",
    )
    list_display = (
        "username",
        "email",
    )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    filter_horizontal = ("tags",)
    list_display = ("short_name", "name", "author", "text", "cooking_time")
    search_fields = ("name",)

    @admin.display(description="Рецепт")
    def short_name(self, obj):
        if len(obj.name) > SHORT_TITLE:
            return f"{obj.name[:SHORT_TITLE]}..."
        return obj.name

    @admin.display(description="Тэги рецепта")
    def get_recipe_tags(self, obj):
        genres = get_object_or_404(Recipe, pk=obj.pk).tags.all()
        return list(genres)

    @admin.display(description="Ингредиенты рецепта")
    def get_recipe_ingredients(self, obj):
        ingredients = get_object_or_404(Recipe, pk=obj.pk).ingredients.all()
        return list(ingredients)


admin.site.empty_value_display = "Не задано."
admin.site.site_title = "Администрирование"
admin.site.site_header = "Администрирование"
admin.site.disable_action("delete_selected")
