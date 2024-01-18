import socket
import threading
import json
import configparser
import os
from getmac import get_mac_address
from django.core.management.base import BaseCommand
from django.utils import timezone
from AppCA.models import KeyRequests


current_file_directory = os.path.dirname(os.path.realpath(__file__))
config_file_path = os.path.join(current_file_directory, '..', '..', 'ca_config.ini')
config = configparser.ConfigParser()
config.read(config_file_path)

# Set your Django app's IP address and port
DJANGO_IP = config['ca']['ip']
DJANGO_PORT = config['ca']['web_port']  # Use the port where your Django app is running

# Set the listener IP address and port
LISTENER_IP = config['ca']['ip']  # Listen on all available network interfaces
LISTENER_PORT = config['ca']['listener_port']  # Choose a different port for the listener

class Command(BaseCommand):
    def handle(self, *args, **options):
        
        def handle_client(client_socket):
            # Receive data from the client
            data = client_socket.recv(1024)
            try:
                # Assuming the received data is in JSON format
                request_data = json.loads(data.decode('utf-8'))
                client_name = request_data.get('client_name', '')

                # Get the MAC address of the client device
                client_ip = client_socket.getpeername()[0]
                mac_address = get_mac_address(ip=client_ip, network_request=True)
                # Create a KeyRequests instance and save it to the database
                key_request = KeyRequests(
                    client_name=client_name,
                    ip_address=client_ip,  # Use MAC address as IP address
                    device_id=mac_address,
                    created_at=timezone.now()
                )
                key_request.save()

                # Send a response back to the client
                response = {'status': 'success', 'message': 'Request processed successfully'}
                client_socket.send(json.dumps(response).encode('utf-8'))
            except json.JSONDecodeError:
                # Handle invalid JSON data
                response = {'status': 'error', 'message': 'Invalid JSON data'}
                client_socket.send(json.dumps(response).encode('utf-8'))

            # Close the connection
            client_socket.close()
                
        def start_listener():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind((LISTENER_IP, LISTENER_PORT))
            server.listen(5)
            print(f"[*] Listening on {LISTENER_IP}:{LISTENER_PORT}")

            try:
                while True:
                    client, addr = server.accept()
                    print(f"[*] Accepted connection from {addr[0]}:{addr[1]}")

                    # Handle the client in a separate thread
                    client_handler = threading.Thread(target=handle_client, args=(client,))
                    client_handler.start()
            except KeyboardInterrupt:
                print("\n[*] Shutting down the listener...")
                server.close()
        start_listener()
