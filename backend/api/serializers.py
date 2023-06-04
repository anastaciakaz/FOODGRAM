from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from recipe.models import (Favorite, Ingredient, IngredientQuantity, Recipe,
                           ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.validators import UniqueTogetherValidator
from api.fields import Hex2NameColor
from users.models import Subscriptions, User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Кастомный сериализатор для регистрации пользователя."""

    class Meta:
        model = User
        fields = (
            'email', 'username', 'first_name', 'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


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
    slug = serializers.SlugField()

    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор модели Ingredient."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class IngredientQuantityReadSerializer(serializers.ModelSerializer):
    """Сериализатор для отображения модели IngredientQuantity."""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientQuantity
        fields = ('id', 'name', 'measurement_unit', 'quantity')
        validators = [
            UniqueTogetherValidator(
                queryset=IngredientQuantity.objects.all(),
                fields=['ingredient', 'recipe']
            )
        ]


class RecipeIngredientAddSerializer(serializers.ModelField):
    """
    Сериализатор для создания рецепта с возможностью
    множественного выбора ингредиентов.
    """

    class Meta:
        model = IngredientQuantity
        fields = ('id', 'quantity')
        extra_kwargs = {
            'id': {
                'read_only': False,
                'error_message': {
                    'exist_error': 'Мы не знаем такого ингредиента',
                }
            },
            'quantity': {
                'error_message': {
                    'min_value': 'Укажите большее количество ингредиента'
                }
            }
        }


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецепта."""

    tag = TagSerializer(read_only=False, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientSerializer(many=True)
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

    ingredients = serializers.SerializerMethodField()
    tags = serializers.ListField(
        child=serializers.SlugRelatedField(
            slug_field='slug',
            queryset=Tag.objects.all(),
        )
    )
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
            if int(ingredient.get('quantity')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента должно быть больше 0'
                )
        return ingredients

    def add_ingredients_tags(self, tags, ingredients, recipe):
        """
        Метод для добавления ингредиентов, их количества
        и тегов в рецепт.
        """
        for tag in tags:
            recipe.tags.add(tag)
            recipe.save()
        IngredientQuantity.objects.bulk_create([IngredientQuantity(
            recipe=recipe,
            ingredient_id=ingredient.get('id'),
            quantity=ingredient.get('quantity')
        ) for ingredient in ingredients])

    def create(self, validated_data):
        """Метод переодпределния создания рецепта."""
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        return self.add_ingredients_tags(tags_data, ingredients_data, recipe)

    def update(self, instance, validated_data):
        instance.ingredients.clear()
        instance.tags.clear()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance = super().update(instance, validated_data)
        return self.add_ingredients_tags(
            tags, ingredients, instance
        )


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
