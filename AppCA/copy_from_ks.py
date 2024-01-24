import paramiko
import configparser
import os
import hexdump
from .models import Node

def copyFileFromKS(file):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'ca_config.ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)
    remote_host = config['ks']['ip']
    remote_username = config['ks']['username']
    remote_password = config['ks']['password']
    remote_file_path = config['ks'][file]
    local_file_path = config['ca'][file]

    # Create an SSH client
    ssh = paramiko.SSHClient()

    try:
        # Automatically add the server's host key
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote host
        ssh.connect(remote_host, username=remote_username, password=remote_password)
        print("Connected")
        # SCP (Secure Copy Protocol) the file from remote to local
        scp = ssh.open_sftp()
        scp.get(remote_file_path, local_file_path)
        scp.close()

        print(f"File copied successfully from {remote_host}:{remote_file_path} to {local_file_path}")
        printBinaryFile(local_file_path)
        process_binary_file(local_file_path)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the SSH connection
        ssh.close()

def printBinaryFile(filepath):
    try:
        with open(filepath, 'rb') as file:
            # Read the binary content of the file
            binary_data = file.read()

            # Print the hexadecimal representation using hexdump
            hexdump.hexdump(binary_data)

    except Exception as e:
        print(f"Error: {e}")

def process_binary_file(file_path):
    with open(file_path, 'rb') as file:
        while True:
            # Read 4 bytes for N_ID and 32 bytes for NTAG
            n_id_bytes = file.read(4)
            ntag_bytes = file.read(32)

            # Check if there is no more data
            if not n_id_bytes or not ntag_bytes:
                break

            # Convert bytes to hexadecimal strings
            n_id_str = n_id_bytes.decode('utf-8', errors='replace').replace('\x00', '')

            n_id_hex = n_id_bytes.hex()
            ntag_hex = ntag_bytes.hex()
            
            print("N_ID: ", n_id_str)
            print("NTAG: ", ntag_hex)
            # Find and update the corresponding Node record in the database
            try:
                node = Node.objects.get(N_ID=n_id_str)
                node.NTAG = ntag_hex
                node.save()
                print(f"Updated Node {n_id_str} with NTAG {ntag_hex}")
            except Node.DoesNotExist:
                print(f"Node with N_ID {n_id_str} not found in the database")


# Call the function to copy the file
copyFileFromKS('node_desc_export')
