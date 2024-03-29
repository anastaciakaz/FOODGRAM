from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import AuthorAdminPermission, IsAdminOrReadOnly
from api.serializers import (IngredientSerializer, RecipeCreateSerializer,
                             RecipeReadSerializer, RecipeShortSerializer,
                             SubscriptionsSerializer, TagSerializer,
                             UserSerializer)
from api.utils import download_shopping_list
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipe.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from users.models import Subscriptions, User


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = CustomPageNumberPagination

    @action(
            methods=['get'],
            permission_classes=(IsAuthenticated, ),
            detail=False,
            url_path='subscriptions',

        )
    def subscriptions(self, request):
        """Получение списка подписок."""
        queryset = User.objects.filter(
            subscriptions__user=request.user
        )
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated, ),
        detail=True
    )
    def subscribe(self, request, id):
        """Создание или отмена подписки."""
        user = request.user
        author = get_object_or_404(User, id=id)

        if request.method == 'POST':
            if user.id == author.id:
                return Response(
                    {'error_message': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscriptions.objects.filter(
                user=user, author=author
            ).exists():
                return Response(
                    {'error_message': f'Вы уже подписаны на {author}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Subscriptions.objects.create(user=user, author=author)
            serializer = SubscriptionsSerializer(author,
                                                 context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = get_object_or_404(Subscriptions,
                                             user=user,
                                             author=author)
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = (IsAdminOrReadOnly, )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вывод игредиентов."""

    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = (IsAdminOrReadOnly, )
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    serializer_class = RecipeCreateSerializer
    queryset = Recipe.objects.all()
    permission_classes = (AuthorAdminPermission, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        """Определение класса сериализатора в зависимости от запроса."""
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def add_recipe(self, model, request, recipe_id):
        """Метод добавления рецепта."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            return Response(
                {'error_message': 'Этот рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeShortSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, request, recipe_id):
        """Метод удаления рецепта."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        obj = model.objects.filter(user=user, recipe=recipe)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт уже удалён'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated, ))
    def favorite(self, request, pk=None):
        """Добавление и удаление рецептов из избранного."""
        if request.method == 'POST':
            return self.add_recipe(Favorite, request, pk)
        return self.delete_recipe(Favorite, request, pk)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated, ))
    def shopping_cart(self, request, pk=None):
        """Добавление и удаление рецептов из корзины."""
        if request.method == 'POST':
            return self.add_recipe(ShoppingCart, request, pk)
        return self.delete_recipe(ShoppingCart, request, pk)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated, ))
    def download_shopping_cart(self, request):
        return download_shopping_list(request)
