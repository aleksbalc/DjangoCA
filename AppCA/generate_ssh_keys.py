import os
import paramiko
import configparser

def generate_ssh_keypair(key_filename):
    """
    Generate SSH key pair and save it to the specified file.
    """
    key = paramiko.RSAKey.generate(bits=2048)

    # Save private key
    with open(key_filename, 'wb') as private_key_file:
        key.write_private_key(private_key_file)

    # Save public key
    with open(f"{key_filename}.pub", 'wb') as public_key_file:
        public_key_file.write(key.get_base64())

if __name__ == "__main__":
    current_file_directory = os.path.dirname(os.path.realpath(__file__))
    config_file_path = os.path.join(current_file_directory, '..', '..', 'ca_config.ini')
    onfig = configparser.ConfigParser()
    ca_private_key_path = "ca_private_key"
    ks_private_key_path = "ks_private_key"

    print(f"Generating CA private key: {ca_private_key_path}")
    generate_ssh_keypair(ca_private_key_path)

    print(f"\nGenerating KS private key: {ks_private_key_path}")
    generate_ssh_keypair(ks_private_key_path)

    print("\nKey generation completed.")