import paramiko
import os
import configparser
from django.conf import settings


def scp_transfer(local_path, remote_path, hostname, port, username, password=None, private_key_path=None):
    transport = paramiko.Transport((hostname, int(port)))

    if password:
        transport.connect(username=username, password=password)
    else:
        private_key = paramiko.RSAKey(filename=private_key_path)
        transport.connect(username=username, pkey=private_key)

    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_path, remote_path)
    sftp.close()

    transport.close()

def copy_file():
# Example usage:
    # Get the absolute path of the static directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'ca_config.ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)
    static_dir = r'D:\WAT\SEM VII\Praca inżynierska\DjangoCA\AppCA\notatki.txt'
   
    remote_file_path = '/home/ca/Testowy.txt'
    remote_hostname = config['ks']['ip']
    remote_port = config['ks']['port']
    remote_username = config['ks']['username']
    remote_password = config['ks']['password']  # or set to None if using key-based authentication
    private_key_path = None  # or set to None if using password authentication

    scp_transfer(static_dir, remote_file_path, remote_hostname, remote_port, remote_username, remote_password, private_key_path)
