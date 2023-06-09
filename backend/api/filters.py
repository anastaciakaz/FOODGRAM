from django.contrib.auth import get_user_model
from django_filters.rest_framework import FilterSet, filters
from recipe.models import Recipe
from rest_framework.filters import SearchFilter

User = get_user_model()


class IngredientFilter(SearchFilter):
    """Фильтр для игредиентов."""

    search_param = 'name'


class RecipeFilter(FilterSet):
    """Фильтр для рецептов."""

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug'
    )
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_favorited = filters.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(shopping_list__user=self.request.user)
        return queryset
