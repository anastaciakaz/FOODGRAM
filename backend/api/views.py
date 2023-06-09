from api.filters import IngredientFilter, RecipeFilter
from api.pagination import CustomPageNumberPagination
from api.permissions import AuthorPermission, IsAdminOrReadOnly
from api.serializers import (IngredientAmountSerializer, IngredientSerializer,
                             RecipeCreateSerializer, RecipeReadSerializer,
                             SubscriptionsSerializer, TagSerializer,
                             UserSerializer)
from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from users.models import Subscriptions, User


class CustomUserViewSet(UserViewSet):
    """Кастомный вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(
            methods=['get'],
            permission_classes=(IsAuthenticated),
            detail=False
        )
    def subscriptions(self, request):
        """Получение списка подписок."""
        queryset = Subscriptions.objects.filter(
            subscribers__user=request.user
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionsSerializer(
                page,
                many=True,
                context={'request': request}
            )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated),
        detail=True
    )
    def subscribe_create_delete(self, request, id):
        """Создание или отмена подписки."""
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if request.user == author:
                return Response(
                    {'error_message': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Subscriptions.objects.filter(user=request.user, author=author):
                return Response(
                    {'error_message': f'Вы уже подписаны на {author}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscriber = Subscriptions.objects.create(
                user=request.user, author=author
            )
            serializer = SubscriptionsSerializer(
                subscriber, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        Subscriptions.objects.filter(user=request.user, author=author).exists()
        subscriber = get_object_or_404(
            Subscriptions, user=request.user, author=author
        )
        subscriber.delete()
        return Response(
            {'message': f'Подписка на {author} отменена'}
        )


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
    search_fields = ('^name', )


class IngredientAmountViewSet(viewsets.ModelViewSet):
    queryset = IngredientAmount.objects.all()
    serializer_class = IngredientAmountSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    """Рецепты."""

    serializer_class = RecipeCreateSerializer
    queryset = Recipe.objects.all()
    permission_classes = (AuthorPermission, )
    filter_backends = (DjangoFilterBackend, )
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_serializer_class(self):
        """Определение класса сериализатора в зависимости от запроса."""
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        """
        Метод используется для добавления дополнительной
        информации при создании нового объекта
        """
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        """Обновление рецепта."""
        serializer.save()

    def add_recipe(self, model, user, id):
        """Метод добавления рецепта."""
        obj = model.objects.filter(author=user, recipe__id=id)
        if obj.exists():
            return Response(
                {'error_message': 'Этот рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = get_object_or_404(Recipe, id=id)
        model.objects.create(user=user, recipe=recipe)
        serializer = RecipeReadSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete_recipe(self, model, user, id):
        """Метод удаления рецепта."""
        obj = model.objects.filter(author=user, recipe__id=id)
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
    def favorite(self, request, id=None):
        """Добавление и удаление рецептов из избранного."""
        if request.method == 'GET':
            return self.add_recipe(Favorite, request.user, id)
        return self.delete_recipe(Favorite, request.user, id)

    @action(detail=True,
            methods=['post', 'delete'],
            permission_classes=(IsAuthenticated, ))
    def shopping_cart(self, request, id=None):
        """Добавление и удаление рецептов из корзины."""
        if request.method == 'GET':
            return self.add_recipe(ShoppingCart, request.user, id)
        return self.delete_recipe(ShoppingCart, request.user, id)

    @action(detail=False,
            methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        """Формирвоание и скачивание списка покупок."""
        shopping_list = []
        ingredients_list = IngredientAmount.objects.filter(
            recipe__purchases__user=request.user
        ).order_by('ingredient__name').values(
            'ingredient__name', 'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))
        for ingredient in ingredients_list:
            shopping_list.append(
                f'{ingredient["ingredient__name"]} - {ingredient["amount"]} '
                f'{ingredient["ingredient__measurement_unit"]} \n'
            )
        response = HttpResponse(
            '\n'.join(shopping_list), content_type='application/pdf'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="{request.user} shoppinglist.pdf"'
        )
        p = canvas.Canvas(response)
        p.setFont("Times-Roman", 18)
        p.drawString(100, 700, "Список покупок: ")
        p.showPage()
        p.save()
        return response
