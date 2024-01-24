import paramiko
import threading
import os
import configparser

def handle_client(client, address):
    print(f"Accepted connection from {address}")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'ca_config.ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)

    try:
        # Receive message from the client
        message = client.recv(1024).decode("utf-8")
        print(f"Received message from {address}: {message}")

        # Copy a file to /home/pi directory with the received message
        filename = config['ca']['N_ID_list']  # Change this to the path of your file
        destination = config['node']['remote_file_location']
        
        # Check if the file exists
        if os.path.exists(filename):
            # Copy the file to the specified destination
            os.system(f"cp {filename} {destination}")
            print(f"File copied to {destination}")
            client.send("File copied successfully!".encode("utf-8"))
        else:
            print(f"File not found: {filename}")
            client.send("File not found!".encode("utf-8"))
    except Exception as e:
        print(f"Error handling connection from {address}: {str(e)}")
    finally:
        client.close()

def start_server():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file_path = os.path.join(script_dir, 'ca_config.ini')

    config = configparser.ConfigParser()
    config.read(config_file_path)
    
    host = config['ca']['ip']
    port = config['ca']['node_listener_port']
    print(host)
    port = int(port)
    private_key_password = config['ca']['key_password']
    # Load the private key for authentication
    private_key_path = config['ca']['private_key'] # Change this to your private key path
    private_key = paramiko.RSAKey(filename=private_key_path, password=private_key_password)

    # Create an SSH server
    server = paramiko.Transport((host, port))
    server.add_server_key(private_key)

    # Start the server
    server.start_server()

    print(f"Server listening on {host}:{port}")

    # while True:
        # client, address = server.accept()
        # client_handler = threading.Thread(target=handle_client, args=(client, address))
        # client_handler.start()

if __name__ == "__main__":
    start_server()