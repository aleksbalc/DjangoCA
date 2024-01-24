import os
import paramiko
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test

from .forms import KeyGenerationRandomForm, KeyGenerationSequentialForm, KeyGenerationFileUploadForm
from .key_functions import generateRandomNId, generateSequenceNId, addNIdsFromFile
from .models import KeyGeneration, Node, KeyRequests

# Create your views here.

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

# @user_passes_test(is_staff, login_url='/no_permission/')
# def add_node(request):
#     # Only staff members can access this view
#     # Your view logic here
#     return render(request, 'add_node.html')

def no_permission(request):
    referring_url = request.META.get('HTTP_REFERER', '/')
    return render(request, 'no_permission.html', {'referring_url': referring_url})


@user_passes_test(is_staff, login_url='/no_permission/')
def generate_keys(request):
    if request.method == 'POST':
        random_form = KeyGenerationRandomForm(request.POST)
        sequential_form = KeyGenerationSequentialForm(request.POST)
        file_upload_form = KeyGenerationFileUploadForm(request.POST, request.FILES)

        if random_form.is_valid() and 'generate_random' in request.POST:
            number_of_keys = random_form.cleaned_data['number_of_keys']
            key_generation = generateRandomNId(number_of_keys)
            return redirect('generated_keys', key_generation_id=key_generation.id)

        elif sequential_form.is_valid() and 'generate_sequential' in request.POST:
            number_of_elements = sequential_form.cleaned_data['number_of_keys']
            first_element = sequential_form.cleaned_data.get('first_value', '0000')  # Set default to '0000'
            key_generation, existing_ids = generateSequenceNId(number_of_elements, first_element)

            if key_generation is not None:
                return redirect('generated_keys', key_generation_id=key_generation.id)
            else:
                error_message = "The sequence cannot be added. The following N_IDs already exist in the database: " + ', '.join(existing_ids)
                return render(request, 'generation_error.html', {'error_message': error_message})

        elif file_upload_form.is_valid() and 'upload_file' in request.POST:
            uploaded_file = file_upload_form.cleaned_data['file']
            key_generation, incorrect_ids, duplicate_ids = addNIdsFromFile(uploaded_file)

            if key_generation is not None and not incorrect_ids and not duplicate_ids:
                return redirect('generated_keys', key_generation_id=key_generation.id)
            elif incorrect_ids:
                error_message = "The sequence cannot be added. The following N_IDs are not in the correct format: " + ', '.join(map(str, incorrect_ids))
                return render(request, 'generation_error.html', {'error_message': error_message})
            elif duplicate_ids:
                error_message = "The sequence cannot be added. The following N_IDs already exist in the database: " + ', '.join(map(str, duplicate_ids))
                return render(request, 'generation_error.html', {'error_message': error_message})
            else:
                return render(request, 'generation_error.html', {'error_message': "An error occurred during node generation."})

    else:
        random_form = KeyGenerationRandomForm()
        sequential_form = KeyGenerationSequentialForm()
        file_upload_form = KeyGenerationFileUploadForm()

    return render(request, 'generate_keys.html', {
        'random_form': random_form,
        'sequential_form': sequential_form,
        'file_upload_form': file_upload_form,
    })


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


@user_passes_test(is_staff, login_url='/no_permission/')
def add_node(request):
    # Get clients without credentials
    clients_without_credentials = KeyRequests.objects.exclude(device_id__in=Node.objects.values('device_id'))

    # Fetch all KeyRequests with additional information
    all_key_requests = KeyRequests.objects.all()

    # Create a dictionary to store the status for each KeyRequest
    key_request_status = {}
    
    for key_request in all_key_requests:
        status = "Waiting for credentials" if key_request in clients_without_credentials else "Credentials assigned"
        key_request_status[key_request.id] = {
            'client_name': key_request.client_name,
            'created_at': key_request.created_at,
            'status': status,
        }
    print(key_request_status)
    
    if request.method == 'POST':
        # Process form submission
        selected_client_id = request.POST.get('client_id')

        # Fetch the oldest Node record without credentials
        node_to_assign = Node.objects.filter(state='id ready', key_set_id__number_of_keys_created__gt=0).order_by('created_at').first()

        if node_to_assign and selected_client_id:
            # Assign credentials to the selected client
            selected_client = KeyRequests.objects.get(id=selected_client_id)
            selected_client.device_id = node_to_assign.device_id
            selected_client.save()

            # Update Node record
            node_to_assign.state = 'credentials taken'
            node_to_assign.save()

            # SSH logic (replace with your actual logic)
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Replace 'your_ssh_key' with the actual path to your private key file
            private_key_path = 'your_ssh_key'
            ssh_client.connect(node_to_assign.ip_address, username='your_ssh_username', key_filename=private_key_path)

            # Perform actions with the SSH connection (replace this with your actual logic)

            ssh_client.close()

            return redirect('success_page')  # Redirect to a success page

    # Render the form with the clients without credentials and all KeyRequests
    return render(request, 'add_node.html', {'clients_without_credentials': clients_without_credentials, 'all_key_requests': all_key_requests, 'key_request_status': key_request_status})