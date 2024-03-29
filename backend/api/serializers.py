from api.fields import Base64ImageField, Hex2NameColor
from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer, UserSerializer
from recipe.models import (Ingredient, IngredientAmount, Recipe, ShoppingCart,
                           Tag)
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
            'id', 'email', 'username', 'first_name', 'last_name',
            'is_subscribed'
        )

    def get_is_subscribed(self, author):
        if Subscriptions.objects.filter(
            author=author, user=self.context['request'].user
        ).exists():
            return True
        return False


class RecipeShortSerializer(serializers.ModelSerializer):
    """Сериализатор для компактного отображения рецептов."""

    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(UserSerializer):
    """Сериализатор для получения списка подписок."""

    recipes_count = serializers.IntegerField(source='recipes.count',
                                             read_only=True)
    recipes = SerializerMethodField(method_name='get_recipes')
    is_subscribed = SerializerMethodField(method_name='get_is_subscribed')

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name',
                  'last_name', 'recipes_count', 'recipes',
                  'is_subscribed')
        read_only_fields = ('email', 'username',
                            'first_name', 'last_name')

    def get_recipes_count(self, user):
        return user.recipes.count()

    def get_recipes(self, obj):
        limit = self.context['request'].query_params.get('recipes_limit')
        if limit:
            queryset = Recipe.objects.filter(author=obj)[:int(limit)]
        else:
            queryset = obj.recipes
        return RecipeShortSerializer(queryset, many=True).data

    def get_is_subscribed(self, author):
        if Subscriptions.objects.filter(
            author=author, user=self.context['request'].user
        ).exists():
            return True
        return False


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
    """Сериализатор для отображения ингредиента в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['id'] = instance.ingredient.id
        return data


class IngredientsAddSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления ингредиента в рецептах."""

    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = ('id', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    """Сериализатор для просмотра рецепта."""

    tags = TagSerializer(read_only=True, many=True)
    author = UserSerializer(read_only=True, many=False)
    ingredients = IngredientAmountSerializer(many=True, source='recipeamount')
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'image', 'text', 'cooking_time')

    def get_is_favorited(self, recipe):
        """
        Метод для определения находится ли рецепт у аутентифицированного
        пользователя в списке любимых рецептов.
        """
        user = self.context['request'].user
        return user.is_authenticated and user.favorites.filter(
            recipe=recipe).exists()

    def get_is_in_shopping_cart(self, recipe):
        """
        Метод для определения находится ли рецепт в корзине у
        аутентифицированного пользователя.
        """
        user = self.context['request'].user
        try:
            user = self.context['request'].user
            return user.is_authenticated and user.purchases.filter(
                recipe=recipe
            ).exists()
        except ShoppingCart.DoesNotExist:
            return False


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания рецептов."""

    ingredients = IngredientsAddSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )
    image = Base64ImageField()
    cooking_time = serializers.IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

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

    def add_ingredients_tags(self, ingredients, tags, recipe):
        """
        Метод для добавления ингредиентов и их количества в рецепт.
        """
        recipe.tags.set(tags)
        IngredientAmount.objects.bulk_create([IngredientAmount(
            recipe=recipe,
            ingredient=ingredient.get('id'),
            amount=ingredient.get('amount')
        ) for ingredient in ingredients])
        return recipe

    def create(self, validated_data):
        """Метод переодпределния создания рецепта."""
        user = self.context['request'].user
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=user, **validated_data)
        self.add_ingredients_tags(ingredients, tags, recipe)
        return recipe

    def update(self, recipe, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe.tags.clear()
        recipe.ingredients.clear()
        self.add_ingredients_tags(ingredients, tags, recipe)
        return super().update(recipe, validated_data)

    def to_representation(self, instance):
        """Метод для отображения рецепта после создания или измененния."""
        context = {'request': self.context['request']}
        return RecipeReadSerializer(instance, context=context).data
