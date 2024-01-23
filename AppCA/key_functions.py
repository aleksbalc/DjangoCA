import paramiko
import random
import string
from .models import KeyGeneration, Node
from django.utils import timezone

def generateRandomNIdNumeral(n):
    # Add a new record to the KeyGeneration table
    key_generation = KeyGeneration.objects.create(number_of_keys_created=n)

    generated_ids = set()

    # Generate n unique random strings of 4 numbers
    while len(generated_ids) < n:
        new_id = str(random.randint(0, 9999)).zfill(4)  # Ensure the ID is 4 digits with leading zeros
        if not Node.objects.filter(N_ID=new_id).exists() and new_id not in generated_ids:
            # ID is unique, add to the set
            generated_ids.add(new_id)

    with open("node_desc_id.txt", 'w') as file:
        file.write('\n'.join(generated_ids))

    # Add the generated strings to the Node table
    for generated_id in generated_ids:
        node = Node.objects.create(
            N_ID=generated_id,
            NTAG='',  
            HMAC='',
            device_id='',  
            key_set_id=key_generation,
            state="ID ready"
        )

    return key_generation

def generateRandomNId(n):
    # Add a new record to the KeyGeneration table
    key_generation = KeyGeneration.objects.create(number_of_keys_created=n)

    generated_ids = set()

    # Generate n unique random strings of 4 characters (numbers and letters)
    while len(generated_ids) < n:
        new_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(4))
        
        if not Node.objects.filter(N_ID=new_id).exists() and new_id not in generated_ids:
            # ID is unique, add to the set
            generated_ids.add(new_id)

    with open("node_desc_id.txt", 'w') as file:
        file.write('\n'.join(generated_ids))

    # Add the generated strings to the Node table
    for generated_id in generated_ids:
        node = Node.objects.create(
            N_ID=generated_id,
            NTAG='',  
            HMAC='',
            device_id='',  
            key_set_id=key_generation,
            state="ID ready"
        )

    return key_generation

def generateSequenceNId(n, first='0000'):
    if first is None:
        first = '0000'
    
    # Check if any of the N_IDs in the sequence already exist in the database
    existing_ids = Node.objects.filter(N_ID__in=[str((int(first) + i) % 10000).zfill(4) for i in range(n)])
    
    if existing_ids.exists():
        # Return a tuple with key generation and existing N_IDs
        return None, list(existing_ids.values_list('N_ID', flat=True))

    # Add a new record to the KeyGeneration table
    key_generation = KeyGeneration.objects.create(number_of_keys_created=n)

    # Generate n random strings of 4 numbers
    generated_ids = [str((int(first) + i) % 10000).zfill(4) for i in range(n)]

    with open("node_desc_id.txt", 'w') as file:
        # Write the generated IDs to the file
        file.write('\n'.join(map(lambda x: str(x).zfill(4), generated_ids)))

    for generated_id in generated_ids:
        node = Node.objects.create(
            N_ID=generated_id,
            NTAG='',  
            HMAC='',
            device_id='',  
            key_set_id=key_generation,
            state="ID ready"
        )

    return key_generation, None

def is_valid_n_id(n_id):
    # Check if the N_ID is not longer than 4 characters
    if len(n_id) > 4:
        return False

    # Check if the N_ID is not empty and consists only of alphanumeric characters
    if not n_id.isalnum():
        return False

    return True

def addNIdsFromFile(uploaded_file):
    # Read the content of the file line by line
    with uploaded_file.open() as f:
        lines = f.readlines()

    content = [line.decode('utf-8').strip() for line in lines]

    all_nodes = set()
    incorrect_ids = set()

    # Process each line as an N_ID
    for line in content:
        n_id = line.strip()  # Remove leading and trailing whitespaces

        # Validate the N_ID
        if not is_valid_n_id(n_id):
            incorrect_ids.add(n_id)
            continue

        # If the N_ID has less than 4 characters, pad it with zeros on the left
        if len(n_id) < 4:
            n_id = n_id.zfill(4)
        # If the N_ID has more than 4 characters, consider only the last four characters
        else:
            n_id = n_id[-4:]

        all_nodes.add(n_id)

    if incorrect_ids:
        return None, incorrect_ids, None

    key_generation = KeyGeneration.objects.create(number_of_keys_created=len(all_nodes))

    existing_ids = set(Node.objects.values_list('N_ID', flat=True))

    duplicate_ids = all_nodes.intersection(existing_ids)

    if duplicate_ids:
        return None, None, duplicate_ids

    for node_id in all_nodes:
        node = Node.objects.create(
            N_ID=node_id,
            NTAG='',
            HMAC='',
            device_id='',
            key_set_id=key_generation,
            state="ID ready"
        )

    return key_generation, None, None

def getNodeFile(n):
    try:
        # Get the node which wants to get available connections and find it's generation id
        node = Node.objects.get(id=n)
        generation_id = node.key_set_id.id

        # Get all nodes with the same generation_id except the current node
        related_nodes = Node.objects.filter(key_set_id=generation_id).exclude(id=n)

        # Extract the IDs from the queryset
        node_ids = [str(related_node.N_ID) for related_node in related_nodes]

        with open("available_nodes.txt", 'w') as file:
            file.write(f"{node.N_ID} {node.NTAG}\n")
            file.write('\n'.join(node_ids))

    except Node.DoesNotExist:
        print("WARNING: Such node not found in the system")
        return
    return

getNodeFile(9)