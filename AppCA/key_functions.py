import os
import paramiko
import time
import random
import string
import configparser
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

    # with open("node_desc_id.txt", 'w') as file:
    #     file.write('\n'.join(generated_ids))

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

    # with open("node_desc_id.txt", 'w') as file:
    #     file.write('\n'.join(generated_ids))

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
    createNIdGenerationFile(key_generation)
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

    # with open("node_desc_id.txt", 'w') as file:
    #     # Write the generated IDs to the file
    #     file.write('\n'.join(map(lambda x: str(x).zfill(4), generated_ids)))

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

# This function creates a file for nodes that want to register to the kgrd (n_id, ntag, and a list of other nodes that can be connected)
def getNodeFile(n):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'ca_config.ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)
    available_nodes = config['ca']['available_nodes']
    print("getNodeFile")
    try:
        # Get the node which wants to get available connections and find it's generation id
        node = Node.objects.get(id=n)
        generation_id = node.key_set_id.id

        # Get all nodes with the same generation_id except the current node
        related_nodes = Node.objects.filter(key_set_id=generation_id).exclude(id=n)

        # Extract the IDs from the queryset
        node_ids = [str(related_node.N_ID) for related_node in related_nodes]

        with open(available_nodes, 'w', encoding='utf-8') as file:
            # Use str() to ensure the content is a string before writing to the file
            file.write(f"{node.N_ID} {node.NTAG}\n")
            file.write('\n'.join(node_ids))

    except Node.DoesNotExist:
        print("getNodeFile WARNING: Such node not found in the system")
        return
    return

#This function creates and sends a file with new nodes to KS
def createNIdGenerationFile(key_generation):
    print("createNIdGenerationFile")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'ca_config.ini')
    config = configparser.ConfigParser()
    config.read(config_file_path)   

    nodes = Node.objects.filter(key_set_id = key_generation.id)
    n_ids = [node.N_ID for node in nodes]

    local_file_path = config['ca']['N_ID_list']
    local_directory = os.path.dirname(local_file_path)
    os.makedirs(local_directory, exist_ok=True)
    with open(local_file_path, 'w') as file:
        for n_id in n_ids:
            file.write(f"{n_id}\n")
    copy_file_ks(local_file_path)
    

def scp_transfer(local_path, remote_path, hostname, port, username, password=None, private_key_path=None):
    transport = paramiko.Transport((hostname, int(port)))

    if password:
        transport.connect(username=username, password=password)
    else:
        private_key = paramiko.RSAKey(filename=private_key_path)
        transport.connect(username=username, pkey=private_key)

    sftp = paramiko.SFTPClient.from_transport(transport)
    print("local path: ", local_path, " remote_path: ", remote_path)
    sftp.put(local_path, remote_path)
    sftp.close()

    transport.close()

def copy_file_ks(local_file_path):
# Example usage:
    # Get the absolute path of the static directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'ca_config.ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)
    static_dir = r'D:\WAT\SEM VII\Praca inżynierska\DjangoCA\AppCA\notatki.txt'
   
    remote_file_path =config['ks']['N_ID_list']
    remote_hostname = config['ks']['ip']
    remote_port = config['ks']['port']
    remote_username = config['ks']['username']
    remote_password = config['ks']['password']  # or set to None if using key-based authentication
    private_key_path = None  # or set to None if using password authentication

    scp_transfer(local_file_path, remote_file_path, remote_hostname, remote_port, remote_username, remote_password, private_key_path)


# def copyNIdsToKS(key_generation):
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     config_file_path = os.path.join(script_dir, 'ca_config.ini')


# createNIdGenerationFile(57)

