from django.contrib import admin

from users.models import Subscription
from recipes.models import (Cart, FavoritRecipe, Ingredient, Recipe,
                            RecipeIngredient, Tag)


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'author', 'name', 'text',
        'cooking_time', 'favorites_count')
    search_fields = (
        'name', 'cooking_time',
        'author__email', 'ingredients__name')
    list_filter = ('name', 'author__username', 'tags')
    inlines = (RecipeIngredientInLine, )

    @admin.display(description='В избранном')
    def favorites_count(self, obj):
        return obj.favorites.count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',)
    search_fields = ('name', 'slug',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',)
    search_fields = ('^name',)


@admin.register(Subscription)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'author')
    search_fields = (
        'user__email', 'author__email',)


@admin.register(FavoritRecipe)
class FavoritRecipeAdmin(admin.ModelAdmin):
    pass


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    pass
