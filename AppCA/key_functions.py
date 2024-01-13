import paramiko
import random
from .models import KeyGeneration, Node
from django.utils import timezone

def generateRandomNId(n):
    # Step 2: Add a new record to the KeyGeneration table
    key_generation = KeyGeneration.objects.create(number_of_keys_created=n)

    # Step 3: Generate n random strings of 4 numbers
    generated_ids = set()
    while len(generated_ids) < n:
        generated_ids.add(str(random.randint(1000, 9999)))

    with open("node_desc_id.txt", 'w') as file:
            file.write('\n'.join(generated_ids))


    # Step 4: Add the generated strings to the Node table
    for generated_id in generated_ids:
        node = Node.objects.create(
            N_ID=generated_id,
            NTAG='',  # You may want to replace with appropriate values
            NNSK='',
            NNSKiv='',
            NNSKsign='',
            HMAC='',
            device_id='',  # You may want to replace with appropriate values
            generation_id=key_generation,
            state="Unknown"
        )

    return key_generation
