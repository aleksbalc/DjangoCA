import os
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test

from .forms import KeyGenerationRandomForm
from .key_functions import generateRandomNId, generateSequenceNId, addNIdsFromFile
from .models import KeyGeneration, Node

# Create your views here.


def handle_uploaded_file(f):
   filename = os.path.basename(f.name)
   with open('/path/to/save/' + filename, 'wb+') as destination:
       for chunk in f.chunks():
           destination.write(chunk)
   return filename

def is_staff(user):
    return user.groups.filter(name='staff').exists()


def index(request):
    return render(request, 'index.html')

def register(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            login(request, authenticate(username=username, password=request.POST['password1']))
            return redirect('index')  # Redirect to your home page
    context = {'form':form}
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('index')  # Redirect to your home page
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')  # Redirect to your home page

@user_passes_test(is_staff, login_url='/no_permission/')
def add_node(request):
    # Only staff members can access this view
    # Your view logic here
    return render(request, 'add_node.html')

def no_permission(request):
    referring_url = request.META.get('HTTP_REFERER', '/')
    return render(request, 'no_permission.html', {'referring_url': referring_url})

@user_passes_test(is_staff, login_url='/no_permission/')
def generate_keys(request):
    if request.method == 'POST':
        form = KeyGenerationRandomForm(request.POST)
        if form.is_valid():
            number_of_keys = form.cleaned_data['number_of_keys']
            generation_type = form.cleaned_data.get('generation_type', 'random')

            if generation_type == 'random':
                key_generation = generateRandomNId(number_of_keys)
            elif generation_type == 'sequential':
                first_value = form.cleaned_data.get('first_value', '0000')  # Set default to '0000'
                key_generation = generateSequenceNId(number_of_keys, first_value)


            return redirect('generated_keys', key_generation_id=key_generation.id)
    else:
        form = KeyGenerationRandomForm()

    return render(request, 'generate_keys.html', {'form': form})

def handle_uploaded_file(file):
    # Add this function if not already present
    with open(file.name, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    return file.name

@user_passes_test(is_staff, login_url='/no_permission/')
def generated_keys(request, key_generation_id):
    key_generation = KeyGeneration.objects.get(pk=key_generation_id)
    generated_nodes = Node.objects.filter(key_set_id=key_generation)

    context = {
        'key_generation': key_generation,
        'generated_nodes': generated_nodes,
    }

    return render(request, 'generated_keys.html', context)

@user_passes_test(is_staff, login_url='/no_permission/')
def manage_nodes(request):
    nodes = Node.objects.all()
    context = {'nodes': nodes}
    return render(request, 'manage_nodes.html', context)
