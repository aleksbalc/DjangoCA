import socket
import json

def send_request(client_name):
    # Set the server IP address and port
    SERVER_IP = '127.0.0.1'  # Change this to the IP address of your Django app server
    SERVER_PORT = 8888  # Change this to the listener port you specified in the listener script

    # Create a socket connection to the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((SERVER_IP, SERVER_PORT))

    # Prepare the request data as a dictionary
    request_data = {
        'client_name': client_name,
    }

    # Send the request data to the server as JSON
    client.send(json.dumps(request_data).encode('utf-8'))

    # Receive the server's response
    response = client.recv(1024).decode('utf-8')

    # Print the response
    print(response)

    # Close the connection
    client.close()

if __name__ == "__main__":
    # Replace 'YourClientName' with the actual client name
    send_request(client_name='YourClientName')