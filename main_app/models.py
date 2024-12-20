from django.db import models
from django.contrib.auth.models import User

class Recipe(models.Model):
    APPETIZER = 'appetizer'
    ENTREE = 'entree'
    DESSERT = 'dessert'
    
    CATEGORY_CHOICES = [
        (APPETIZER, 'Appetizer'),
        (ENTREE, 'Entree'),
        (DESSERT, 'Dessert'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recipes")
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='entree'
    )
    def __str__(self):
        return self.title


class Ingredient(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ingredients", default=1)

    def __str__(self):
        return self.name


class MeasurementUnit(models.TextChoices):
    # Volume Units
    TEASPOON = 'tsp', 'Teaspoon'
    TABLESPOON = 'tbsp', 'Tablespoon'
    FLUID_OUNCE = 'fl oz', 'Fluid Ounce'
    CUP = 'c', 'Cup'
    PINT = 'pt', 'Pint'
    QUART = 'qt', 'Quart'
    GALLON = 'gal', 'Gallon'
    MILLILITER = 'ml', 'Milliliter'
    LITER = 'L', 'Liter'

    # Weight Units
    OUNCE = 'oz', 'Ounce'
    POUND = 'lb', 'Pound'
    GRAM = 'g', 'Gram'
    KILOGRAM = 'kg', 'Kilogram'

#Links recipes and ingredients with associated quantities and units.
class RecipeIngredient(models.Model): 
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="recipe_ingredients")
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE, related_name="recipe_ingredients")
    measurement_unit = models.CharField(max_length=10, choices=MeasurementUnit.choices)
    measurement_qty = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 1001)])

def __str__(self):
    unit = self.get_measurement_unit_display()
    return f"{self.measurement_qty} {unit}{'s' if self.measurement_qty > 1 else ''} {self.ingredient.name}"


class Step(models.Model):
    text = models.TextField()
    step_num = models.PositiveIntegerField()
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="steps")

    class Meta:
        ordering = ['step_num']

    def __str__(self):
        return f"Step {self.step_num}"


class Favorite(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name="favorites")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="favorites")

    def __str__(self):
        return f"{self.recipe.title}"