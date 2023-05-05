from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField('Ингредиент', max_length=200)
    measurement_unit = models.CharField('Ед. измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['id']

    def __str__(self):
        return f'{self.name}({self.measurement_unit})'


class Tag(models.Model):
    """Модель тега."""
    name = models.CharField('Тэг', max_length=200)
    color = models.CharField('Цветовой HEX-код', max_length=7)
    slug = models.SlugField('Slug', max_length=50, unique=True)

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'
        ordering = ['id']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта."""
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='recipes',
        verbose_name='Автор рецепта'
    )
    name = models.CharField(max_length=200, verbose_name='Название рецепта')
    image = models.ImageField(
        upload_to='recipes/', verbose_name='Изображение рецепта'
    )
    text = models.TextField(verbose_name='Описание рецепта')
    ingredients = models.ManyToManyField(
        Ingredient, through='RecipeIngredient', verbose_name='Ингредиенты'
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления, мин.')
    tags = models.ManyToManyField(
        Tag, verbose_name='Тэги', related_name='recipes'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id', )

    def __str__(self):
        return f'{self.author}, {self.name}'


class RecipeIngredient(models.Model):
    """Связующая модель многие-ко-многим для ингредиентов и рецептов."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients')
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient')
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента')

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient')]


class FavoritRecipe(models.Model):
    """Модель для избранных рецептов."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='favorites')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite')]

    def __str__(self):
        return f'{self.user}, {self.recipe.name}'


class Cart(models.Model):
    """Модель для списка покупок."""
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='cart')

    class Meta:
        verbose_name = "Рецепт в корзине"
        verbose_name_plural = "Рецепты в корзине"
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name="unique_recipe"
            )
        ]

    def __str__(self):
        return f'{self.user}, {self.recipe.name}'
