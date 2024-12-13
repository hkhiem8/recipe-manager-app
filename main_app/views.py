from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Recipe, Ingredient, Step, Favorite, RecipeIngredient, MeasurementUnit
# Import HttpResponse to send text-based responses
from django.http import HttpResponse


#################
#Auth Views
#################

# Login view
class Login(LoginView):
    template_name = 'main_app/login.html'


#Sign up
def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('login')
        else:
            error_message = 'Invalid sign up - try again'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'signup.html', context)

# Home view
def home(request):
    return render(request, 'main_app/home.html')

#################
#Recipe Views
#################

# Create a recipe
class RecipeCreate(LoginRequiredMixin, CreateView):
    model = Recipe
    fields = ['title', 'description']
    template_name = 'recipes/recipe_form.html'

    def form_valid(self, form):
        # Associate the currently logged-in user with the recipe
        form.instance.user = self.request.user
        self.object = form.save()
        # Redirect to the ingredient creation page with the recipe ID
        return redirect('ingredient-create', recipe_id=self.object.id)


# View all recipes
class RecipeList(LoginRequiredMixin, ListView):
    model = Recipe
    template_name = 'recipes/recipe_list.html'
    context_object_name = 'recipes'

    def get_queryset(self):
        return Recipe.objects.filter(user=self.request.user) 

#View individual recipe details
class RecipeDetail(LoginRequiredMixin, DetailView):
    model = Recipe
    template_name = 'recipes/recipe_detail.html'
    context_object_name = 'recipe'

#Update recipes - make a view
class RecipeUpdate(LoginRequiredMixin, UpdateView):
    model = Recipe
    fields = ['title', 'description']
    success_url = '/recipes/'
    template_name = 'recipes/recipe_update_form.html'

#Delete recipes
class RecipeDelete(LoginRequiredMixin, DeleteView):
    model = Recipe
    success_url = '/recipes/'
    template_name = 'recipes/recipe_confirm_delete.html'

#################
#Ingredient Views
#################

#Create ingredients
@login_required
def ingredient_create(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id, user=request.user)
   
    # Get existing ingredients for the dropdown
    user_ingredients = Ingredient.objects.filter(user=request.user)
    context = {
        'recipe': recipe,
        'ingredients': user_ingredients,
        'measurement_units': MeasurementUnit.choices,
        'measurement_quantities': range(1, 1001)
    }
    # Handle new ingredient creation
    if request.method == 'POST':
        ingredient_name = request.POST.get('ingredient_name')
        if ingredient_name:
            ingredient, created = Ingredient.objects.get_or_create(
                name=ingredient_name.lower().strip(),
                user=request.user
            )

        # Create the recipe-ingredient association
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient,
                measurement_qty=request.POST.get('measurement_qty'),
                measurement_unit=request.POST.get('measurement_unit')
            )

            if 'add_another' in request.POST:
                return redirect('ingredient-create', recipe_id=recipe.id)
            return redirect('recipe-detail', pk=recipe.id)
        
    return render(request, 'ingredients/ingredient_form.html', context)


#Get all ingredients
@login_required
def ingredient_list(request):
    ingredients = Ingredient.objects.filter(user=request.user)
    return render(request, 'ingredients/ingredient_list.html', {'ingredients': ingredients})

#Update Ingredient
@login_required
def ingredient_update(request, ingredient_id):
    ingredient = Ingredient.objects.get(id=ingredient_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            ingredient.name = name
            ingredient.save()
            return redirect('ingredient-list')
    return render(request, 'ingredients/ingredient_form.html', {'ingredient': ingredient})

#Delete Ingredient
@login_required
def ingredient_delete(request, ingredient_id):
    ingredient = Ingredient.objects.get(id=ingredient_id)
    if request.method == 'POST':
        ingredient.delete()
        return redirect('ingredient-list')
    return render(request, 'ingredients/ingredient_confirm_delete.html', {'ingredient': ingredient})

#################
#Step Views
#################

#Create a step
def step_create(request, recipe_id):
    if request.method == 'POST':
        text = request.POST.get('text')
        step_num = request.POST.get('step_num')
        if text and step_num:
            Step.objects.create(id=recipe_id, text=text, step_num=step_num)
            return redirect('recipe-detail', pk=recipe_id) #circle back
    return render(request, 'steps/steps_form.html')

#List all steps
def step_list(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    steps = recipe.steps.all()
    return render(request, 'steps/step_list.html', {'recipe': recipe, 'steps': steps})

#Update a step
def step_update(request, recipe_id):
    step = Step.objects.get(id=recipe_id)
    if request.method == 'POST':
        text = request.POST.get('text')
        step_num = request.POST.get('step_num')
        if text and step_num:
            step.text = text
            step.step_num = step_num
            step.save()
            return redirect('recipe-detail', id=step.recipe.id) #circle back
    return render(request, 'steps/step_form.html', {'step': step})

#Delete a step
def step_delete(request, recipe_id):
    step = Step.objects.get(id=recipe_id)
    if request.method == 'POST':
        step.delete()
        return redirect('recipe-detail', id=step.recipe.id)
    return render(request, 'steps/step_confirm_delete.html', {'step': step})   

#################
#Favorites Views
#################

#Create favorites
def favorite_create(request, recipe_id):
    recipe = Recipe.objects.get(id=recipe_id)
    Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    return redirect('recipe-list')

#List all favorites
class FavoriteList(LoginRequiredMixin, ListView):
    model = Favorite
    template_name = 'favorites/favorite_list.html'
    context_object_name = 'favorites'

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

#Delete/remove favorites
def favorite_delete(request, recipe_id):
    favorite = Favorite.objects.get(id=recipe_id)
    if request.method == 'POST':
        favorite.delete()
        return redirect('favorite-list')
    return render(request, 'favorites/favorite_confirm_delete.html', {'favorite': favorite})