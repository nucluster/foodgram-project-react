from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.formats import date_format
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet

from users.models import Subscription, User
from users.permissions import IsAuthorOrReadOnly
from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import Pagination
from recipes.models import (Cart, FavoritRecipe, Ingredient, Recipe,
                            RecipeIngredient, Tag)
from api.serializers import (CartSerializer, FavoritRecipeSerializer,
                             IngredientSerializer, RecipePostSerializer,
                             RecipeSerializer, SubscribeSerializer,
                             TagSerializer)


class CustomUserViewSet(UserViewSet):
    pagination_class = Pagination

    def get_queryset(self):
        return User.objects.all()

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, **kwargs):
        user = get_object_or_404(User, username=request.user)
        author = get_object_or_404(User, id=self.kwargs.get('id'))

        if request.method == 'POST':
            serializer = SubscribeSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        subscription = get_object_or_404(
            Subscription, user=user, author=author
        )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribe__user=user)
        pages = self.paginate_queryset(queryset)
        serializer = SubscribeSerializer(
            pages, many=True, context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = Pagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filterset_class = RecipeFilter
    ordering = ('-id',)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipePostSerializer
        return RecipeSerializer

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, **kwargs):
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))

        if request.method == 'POST':
            serializer = FavoritRecipeSerializer(
                recipe, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            FavoritRecipe.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        favorite_recipe = get_object_or_404(
            FavoritRecipe, user=user, recipe=recipe
        )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, **kwargs):
        user = get_object_or_404(User, username=request.user)
        recipe = get_object_or_404(Recipe, id=self.kwargs.get('pk'))

        if request.method == 'POST':
            serializer = CartSerializer(
                recipe, data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            Cart.objects.create(user=user, recipe=recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        cart_recipe = get_object_or_404(
            Cart, user=user, recipe=recipe
        )
        cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        user = request.user
        if not user.cart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)

        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__cart__user=user
            )
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(sum_amount=Sum('amount')).order_by()
        )

        today = date_format(timezone.now(), use_l10n=True)
        headline = (
            f'Дата: {today} \n\n'
            f'Список покупок: \n\n'
        )
        lines = []
        for ingredient in ingredients:
            line = (
                f'➤ {ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]})'
                f' -- {ingredient["sum_amount"]}'
            )
            lines.append(line)

        shopping_list = headline + '\n'.join(lines)
        filename = 'shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
