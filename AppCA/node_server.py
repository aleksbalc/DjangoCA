import paramiko
import threading
import os
import configparser

import paramiko

def send_file(source_path, destination_path, private_key_path, remote_host, remote_port, remote_username):
    # Connect to the remote server using SSH key authentication
    private_key = paramiko.RSAKey(filename=private_key_path)
    transport = paramiko.Transport((remote_host, remote_port))
    transport.connect(username=remote_username, pkey=private_key)

    # Create an SFTP client session
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        # Upload the file from the source path to the destination path on the remote server
        sftp.put(source_path, destination_path)
        print(f"File '{source_path}' successfully sent to '{destination_path}' on {remote_host}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the SFTP session and the SSH transport
        sftp.close()
        transport.close()

if __name__ == "__main__":
    # Replace the following variables with your own values
    source_file = r"D:\DjangoCA\files\available_nodes.txt"
    destination_file = "/home/ca/available_nodes.txt"
    remote_host = "192.168.56.101"
    remote_port = 22  # Change the port if necessary
    remote_username = "ca"
    private_key_path = r'C:\Users\olcia\.ssh\id_rsa'
    send_file(source_file, destination_file, private_key_path, remote_host, remote_port, remote_username)

# def handle_client(client, address):
#     print(f"Accepted connection from {address}")
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     config_file_path = os.path.join(script_dir, 'ca_config.ini')

#     config = configparser.ConfigParser()
#     config.read(config_file_path)

#     try:
#         # Receive message from the client
#         message = client.recv(1024).decode("utf-8")
#         print(f"Received message from {address}: {message}")

#         # Copy a file to /home/pi directory with the received message
#         filename = config['ca']['N_ID_list']  # Change this to the path of your file
#         destination = config['node']['remote_file_location']
        
#         # Check if the file exists
#         if os.path.exists(filename):
#             # Copy the file to the specified destination
#             os.system(f"cp {filename} {destination}")
#             print(f"File copied to {destination}")
#             client.send("File copied successfully!".encode("utf-8"))
#         else:
#             print(f"File not found: {filename}")
#             client.send("File not found!".encode("utf-8"))
#     except Exception as e:
#         print(f"Error handling connection from {address}: {str(e)}")
#     finally:
#         client.close()

# def start_server():
#     script_dir = os.path.dirname(os.path.abspath(__file__))
#     config_file_path = os.path.join(script_dir, 'ca_config.ini')

#     config = configparser.ConfigParser()
#     config.read(config_file_path)
    
#     host = config['ca']['ip']
#     port = config['ca']['node_listener_port']
#     print(host)
#     port = int(port)
#     private_key_password = config['ca']['key_password']
#     # Load the private key for authentication
#     private_key_path = config['ca']['private_key'] # Change this to your private key path
#     private_key = paramiko.RSAKey(filename=private_key_path, password=private_key_password)

#     # Create an SSH server
#     server = paramiko.Transport((host, port))
#     server.add_server_key(private_key)

#     # Start the server
#     server.start_server()

#     print(f"Server listening on {host}:{port}")

#     # while True:
#         # client, address = server.accept()
#         # client_handler = threading.Thread(target=handle_client, args=(client, address))
#         # client_handler.start()

# if __name__ == "__main__":
#     start_server()
