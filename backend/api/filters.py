from django_filters import rest_framework as filters

from recipes.models import Recipe, Tag, User
from rest_framework.filters import SearchFilter


class RecipeFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )

    is_favorited = filters.NumberFilter(method='_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author']

    def _is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites__user=self.request.user)
        return queryset

    def _is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart__user=self.request.user)
        return queryset


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'
