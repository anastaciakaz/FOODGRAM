from api.fields import Hex2NameColor
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Favorite, Ingredient, IngredientAmount, Recipe,
                           ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueValidator
from users.models import Subscriptions

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериализатор для регистрации пользователя."""

    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all()
            )
        ]
    )
    username = serializers.CharField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all()
            )
        ]
    )
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'password',
            'username',
            'first_name',
            'last_name',
        )


class UserSerializer(UserSerializer):
    """Сериализатор модели User."""

    is_subscribed = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name',
            'password', 'is_subscribed'
        )

    def get_is_subscribed(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return Subscriptions.objects.filter(user=user, author=obj).exists()


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор модели Tag."""

    color = Hex2NameColor()

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения модели IngredientAmount."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')
        extra_kwargs = {
            'amount': {
                'error_message': {
                    'min_value': 'Укажите большее количество ингредиента'
                }
            }
        }


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецепта."""

    tag = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientAmountSerializer(source='recipeamount',
                                             many=True, read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author', 'tags', 'ingrediants', 'image',
            'description', 'pub_date', 'cooking_time', 'is_favorited',
            'is_in_the_shopping_cart'
        )

    def get_is_favorited(self, obj):
        """
        Метод для определения находится ли рецепт у аутентифицированного
        пользователя в списке любимых рецептов.
        """
        user = self.context['request'].user
        if user.is_anonymous:
            return False
        return (
            Favorite.objects.filter(recipe=obj, user=user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        """
        Метод для определения находится ли рецепт в корзине у
        аутентифицированного пользователя.
        """
        user = self.context['request'].user
        try:
            return (
                user.is_authenticated and
                ShoppingCart.objects.filter(recipe=obj, user=user).exists()
            )
        except ShoppingCart.DoesNotExist:
            return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    ingredients = IngredientAmountSerializer(many=True)
    tags = TagSerializer(many=True, read_only=True)
    image = Base64ImageField()
    author = UserSerializer(read_only=True, many=False)
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate_tags(self, tags):
        """Метод для валидации тегов в рецепте."""
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта')
        for tag in tags:
            if not Tag.objects.filter(id=tag.id).exists():
                raise serializers.ValidationError(
                    'Тега не существует'
                )
            return tags

    def validate_cooking_time(self, cooking_time):
        """Метод для валидации времени приготовления."""
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время приготовления должно быть больше минуты'
            )
        return cooking_time

    def validate_ingredients(self, ingredients):
        """Метод валидации игредиентов."""
        ingredients_list = []
        if not ingredients:
            raise serializers.ValidationError(
                'Игредиенты не выбраны'
            )
        for ingredient in ingredients:
            if ingredient['id'] in ingredients_list:
                raise serializers.ValidationError(
                    {
                        'ingredients': 'Игредиент не должен повторяться'
                    }
                )
            ingredients_list.append(ingredient['id'])
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
        return ingredients

    def add_ingredients(self, ingredients, recipe):
        """
        Метод для добавления ингредиентов и их количества в рецепт.
        """
        IngredientAmount.objects.bulk_create([IngredientAmount(
            recipe=recipe,
            ingredient_id=ingredient.get('id'),
            amount=ingredient.get('amount')
        ) for ingredient in ingredients])

    def create(self, validated_data):
        """Метод переодпределния создания рецепта."""
        image = validated_data.pop('image')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(image=image, **validated_data)
        tags_data = self.initial_data.get('tags')
        recipe.tags.set(tags_data)
        self.add_ingredients(ingredients_data, recipe)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = self.initial_data.get('ingredients')
        tags = self.initial_data.get('tags')
        recipe = super().update(recipe, validated_data)
        if ingredients:
            recipe.ingredients.clear()
            self.add_ingredients(ingredients, recipe)
        if tags:
            recipe.tags.set(tags)
        return recipe


class SubscriptionsSerializer(serializers.ModelSerializer):
    """Сериализатор для получения списка подписок."""

    is_subscribed = serializers.SerializerMethodField()
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'email', 'username',
            'last_name', 'first_name', 'is_subscribed',
            'recipes', 'recipes_count'
        )
        read_only_fields = ('email', 'username', 'first_name', 'last_name')

    def get_is_subscribed(self, obj):
        """Статус подписки на автора."""
        user = self.context.get('request').user
        return Subscriptions.objects.filter(
            user=user, author=obj.author
        ).exists()

    def get_recipes(self, obj):
        """Получение списка рецептов автора."""
        request = self.context['request']
        limit = request.GET.get('recipes_limit')
        queryset = Recipe.objects.filter(author=obj.author)
        if limit:
            queryset = queryset[:int(limit)]
        return RecipeReadSerializer(queryset, many=True).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор для списка избранных рецептов."""

    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        """Метод для валидации избранных рецептов."""
        recipe = data['recipe']
        user = data['user']
        if user == recipe.author:
            raise serializers.ValidationError(
                'Вы не можете добавить свои рецепты в избранное')
        if Favorite.objects.filter(recipe=recipe, user=user).exists():
            raise serializers.ValidationError(
                'Вы уже добавили этот рецепт в избранное')
        return data

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data


class ShoppingCartSerializer(serializers.ModelSerializer):
    """Сериализатор для списка покупок."""

    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        """Метод для валидации списка покупок."""
        recipe = data['recipe']
        user = data['user']
        if ShoppingCart.objects.filter(recipe=recipe, user=user):
            raise serializers.ValidationError(
                'Этот рецепт уже есть в списке покупок'
            )
        return data

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance.recipe,
            context={'request': self.context.get('request')}
        ).data
