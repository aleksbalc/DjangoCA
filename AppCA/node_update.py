import os
import configparser
import rsa

script_dir = os.path.dirname(os.path.abspath(__file__))
config_file_path = os.path.join(script_dir, 'ca_config.ini')
config = configparser.ConfigParser()
config.read(config_file_path)

def generateKeyPair():
    private_key_dir = config['ca']['private_key']
    public_key_dir = config['ca']['public_key']

    os.makedirs(os.path.dirname(public_key_dir), exist_ok=True)
    os.makedirs(os.path.dirname(private_key), exist_ok=True)

    public_key, private_key = rsa.newkeys(1024)

    with open(public_key_dir, "wb") as file:
        file.write(public_key.save_pkcs1("PEM"))

    with open(private_key_dir, "wb") as file:
        file.write(private_key.save_pkcs1("PEM"))

    print(private_key)

def encryptMessage():
    private_key_dir = config['ca']['private_key']
    public_key_dir = config['ca']['public_key']

    with open(public_key_dir, "rb") as file:
        public_key=rsa.PublicKey.load_pkcs1(file.read())

    with open(private_key_dir, "rb") as file:
        private_key=rsa.PrivateKey.load_pkcs1(file.read())

generateKeyPair()