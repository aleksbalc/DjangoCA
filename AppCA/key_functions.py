import paramiko
import random
from .models import KeyGeneration, Node
from django.utils import timezone

def generateRandomNId(n):
    # Add a new record to the KeyGeneration table
    key_generation = KeyGeneration.objects.create(number_of_keys_created=n)

    # Generate n random strings of 4 numbers
    generated_ids = set()
    while len(generated_ids) < n:
        generated_ids.add(str(random.randint(0000, 9999)))

    with open("node_desc_id.txt", 'w') as file:
            file.write('\n'.join(generated_ids))

    # Add the generated strings to the Node table
    for generated_id in generated_ids:
        node = Node.objects.create(
            N_ID=generated_id,
            NTAG='',  
            NNSK='',
            NNSKiv='',
            NNSKsign='',
            HMAC='',
            device_id='', 
            generation_id=key_generation,
            state="Unknown"
        )

    return key_generation

def generateSequenceNId(n, first='0000'):
    # Add a new record to the KeyGeneration table
    key_generation = KeyGeneration.objects.create(number_of_keys_created=n)

    # Generate n random strings of 4 numbers
    generated_ids = [str((first + i) % 10000).zfill(4) for i in range(n)]

    with open("node_desc_id.txt", 'w') as file:
        # Write the generated IDs to the file
        file.write('\n'.join(map(lambda x: str(x).zfill(4), generated_ids)))


    for generated_id in generated_ids:
        node = Node.objects.create(
            N_ID=generated_id,
            NTAG='',  
            NNSK='',
            NNSKiv='',
            NNSKsign='',
            HMAC='',
            device_id='',  
            generation_id=key_generation,
            state="Unknown"
        )

    return key_generation


def getAvailableNodes(n):
    try:
        # Get the node which wants to get available connections and find it's generation id
        node = Node.objects.get(id=n)
        generation_id = node.generation_id.id

        # Get all nodes with the same generation_id except the current node
        related_nodes = Node.objects.filter(generation_id=generation_id).exclude(id=n)

        # Extract the IDs from the queryset
        node_ids = [str(related_node.N_ID) for related_node in related_nodes]

        with open("available_nodes.txt", 'w') as file:
            file.write('\n'.join(node_ids))

    except Node.DoesNotExist:
        print("WARNING: Such node not found in the system")
        return
    return