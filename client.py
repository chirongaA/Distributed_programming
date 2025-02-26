import socket

# Create a TCP/IP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('10.0.0.92',9100)
client_socket.connect(server_address)

try:
    # Send a message to the server
    message = input("Enter a message to send: ")
    client_socket.sendall(message.encode())
    response = client_socket.recv(1024).decode()
    print(f'Response from server: {response}')
finally:
    # Close the connection
    client_socket.close()
