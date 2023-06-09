from django.contrib import admin
from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)


class RecipeAdmin(admin.ModelAdmin):
    """Админ панель для управления рецептами."""
    list_display = ('author', 'name', 'cooking_time',
                    'get_favorites', )
    search_fields = ('name', 'author', 'tags', )
    readonly_fields = ('get_favorites', )
    list_filter = ('author', 'name', 'tags', )
    empty_value_display = '-пусто-'

    def get_favorites(self, obj):
        """
        Метод для отображения сколько раз рецепт добавили
        в избранное.
        """
        return obj.favorites.count()


class IngredientAdmin(admin.ModelAdmin):
    """Админ панель для управления ингридиентами."""

    list_display = ('name', 'measurement_unit', )
    search_fields = ('name', )
    list_filter = ('name', )
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    """Админ панель для управления тегами."""

    list_display = ('name', 'color', 'slug', )
    search_fields = ('name', 'slug', )
    list_filter = ('name', )
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    """Админ панель для управления избранными рецептами."""

    list_display = ('user', 'recipe', )
    list_filter = ('user', 'recipe', )
    search_fields = ('user', 'recipe', )
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    """Админ панель для управления списком покупок."""

    list_display = ('user', )
    list_filter = ('recipe', 'user', )
    search_fields = ('user', )
    empty_value_display = '-пусто-'


class IngredientAmountAdmin(admin.ModelAdmin):
    """Админ панель для управления моделью IngredientAmount."""

    list_display = ('recipe', 'ingredient',
                    'amount', 'get_measurement_unit', )

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Favorite, FavoriteAdmin)
