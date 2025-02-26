import socket

def process_message(message):
# Reverse the message
 return message[::-1]

# Create a TCP/IP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('10.0.0.92', 9100))
server_socket.listen(3)
print('Server is listening for connections...')

while True:
    client_socket, client_address = server_socket.accept()
    try:
        print(f'Connected to {client_address}')
        message = client_socket.recv(1024).decode()
        print(f'Received message: {message}')
        response = process_message(message)
        client_socket.sendall(response.encode())
    finally:
        # Close the connection
        client_socket.close()

