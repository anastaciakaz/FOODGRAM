from django.contrib.auth import get_user_model
from django.core import validators
from django.db import models

User = get_user_model()

MIN_VALUE_COOKING_TIME = 1
MIN_VALUE_INGREDIENT_QUANTITY = 1


class Tag(models.Model):
    """Модель тега."""

    COLOR_CHOICES = (
        ('Yellow', 'Жёлтый'),
        ('Blue', 'Синий'),
        ('Pink', 'Розовый'),
        ('Orange', 'Оранжевый'),
        ('Purple', 'Фиолетовый'),
        ('Green', 'Зелёный'),
    )
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Название'
    )
    color = models.CharField(max_length=16, choices=COLOR_CHOICES)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ['-id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """Модель ингредиента."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Игредиент'
        verbose_name_plural = 'Игредиенты'
        constraints = [
            models.UniqueConstraint(fields=['name', 'measurement_unit'],
                                    name='unique_ingredient')
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецепта."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название рецепта'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientAmount',
        verbose_name='Ингредиенты',
        related_name='recipes',
    )
    cooking_time = models.PositiveIntegerField(
        validators=[validators.MinValueValidator(
            MIN_VALUE_COOKING_TIME,
            message='Минимальное время приготовления не менее 1'
            )
        ],
        verbose_name='Время приготовления'
    )
    image = models.ImageField(
        upload_to='static/recipe',
        verbose_name='Фото блюда'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'{self.name}, {self.author}'


class IngredientAmount(models.Model):
    """Модель ингредиентов в рецепте с количеством."""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeamount',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[
            validators.MinValueValidator(
                MIN_VALUE_INGREDIENT_QUANTITY,
                message='Минимальное количество ингридиентов не менее 1'
            )
        ],
        verbose_name='Количество',
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_amount'
            )
        ]

    def __str__(self):
        return (f'В рецепте {self.recipe.name} {self.amount} '
                f'{self.ingredient.measurement_unit} {self.ingredient.name}')


class Favorite(models.Model):
    """Модель избранных рецептов пользователя."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_favorite_list'
            )
        ]

    def __str__(self):
        return f'{self.user} -> {self.recipe}'


class ShoppingCart(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='purchases',
        verbose_name='Рецепт'
    )

    class Meta:
        ordering = ['-id']
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique user shopping cart'
            )
        ]

    def __str__(self):
        return (f'{self.user}', рецепт в списке {self.recipe.name}')'
