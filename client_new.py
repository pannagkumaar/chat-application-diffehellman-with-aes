# import socket
# import random
# import time
# import threading

# def diffie_hellman(prime, base):
#     private_key = random.randint(2, prime - 2)
#     public_key = (base ** private_key) % prime
#     return prime, base, private_key, public_key

# def calculate_shared_secret_key(public_key, private_key, prime):
#     return (public_key ** private_key) % prime

# def encrypt_string(string, key):
#     encrypted_string = ""
#     for char in string:
#         encrypted_char = chr(ord(char) + key)
#         encrypted_string += encrypted_char
#     return encrypted_string

# def decrypt_string(encrypted_string, key):
#     decrypted_string = ""
#     for char in encrypted_string:
#         decrypted_char = chr(ord(char) - key)
#         decrypted_string += decrypted_char
#     return decrypted_string

# def receive_messages(s, shared_secret_key):
#     while True:
#         encrypted_response = s.recv(1024).decode()
#         response = decrypt_string(encrypted_response, shared_secret_key)
#         print("\nServer:", response)

# def client():
#     host = '127.0.0.1'
#     port = 12345

#     s = socket.socket()
#     s.connect((host, port))

#     # Receive prime and base values from the server
#     print("Waiting to receive prime...")
#     s_prime = int(s.recv(1024).decode())
#     print("Received prime:", s_prime)
#     time.sleep(3)

#     print("Waiting to receive base...")
#     s_base = int(s.recv(1024).decode())
#     print("Received base:", s_base)
#     time.sleep(3)

#     prime, base, private_key, public_key = diffie_hellman(s_prime, s_base)

#     # Send public key to the server
#     print("Sending public key...")
#     s.send(str(public_key).encode())
#     print("Sent public key:", public_key)
#     time.sleep(3)

#     # Receive the server's public key
#     print("Waiting to receive server's public key...")
#     server_public_key = int(s.recv(1024).decode())
#     print("Received server's public key:", server_public_key)
#     time.sleep(3)

#     # Calculate the shared secret key
#     shared_secret_key = calculate_shared_secret_key(server_public_key, private_key, prime)
#     print("Shared Secret Key:", shared_secret_key)
#     time.sleep(3)

#     # Start thread to receive messages
#     receive_thread = threading.Thread(target=receive_messages, args=(s, shared_secret_key))
#     receive_thread.start()

#     # Chat loop
#     while True:
#         # Sending message to the server
#         message_to_send = input("You: ")
#         encrypted_message = encrypt_string(message_to_send, shared_secret_key)
#         s.send(encrypted_message.encode())

#         if message_to_send.lower() == 'exit':
#             break

#     s.close()

# if __name__ == "__main__":
#     client()
import socket
import random
import time
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

def diffie_hellman(prime, base):
    private_key = random.randint(2, prime - 2)
    public_key = pow(base, private_key, prime)
    return prime, base, private_key, public_key

def calculate_shared_secret_key(public_key, private_key, prime):
    return pow(public_key, private_key, prime)

def encrypt_message(message, key):
    cipher = AES.new(key, AES.MODE_CBC, iv=get_random_bytes(16))
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return ciphertext, cipher.iv

def decrypt_message(ciphertext, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode()

def receive_messages(s, shared_secret_key, aes_key):
    while True:
        encrypted_message = s.recv(1024)
        iv = encrypted_message[:16]
        ciphertext = encrypted_message[16:]
        decrypted_message = decrypt_message(ciphertext, aes_key, iv)
        print("\nServer:", decrypted_message)

def client():
    host = '127.0.0.1'
    port = 12345

    s = socket.socket()
    s.connect((host, port))

    # Receive prime and base values from the server
    print("Waiting to receive prime...")
    s_prime = int(s.recv(1024).decode())
    print("Received prime:", s_prime)
    time.sleep(3)

    print("Waiting to receive base...")
    s_base = int(s.recv(1024).decode())
    print("Received base:", s_base)
    time.sleep(3)

    prime, base, private_key, public_key = diffie_hellman(s_prime, s_base)

    # Send public key to the server
    print("Sending public key...")
    s.send(str(public_key).encode())
    print("Sent public key:", public_key)
    time.sleep(3)

    # Receive the server's public key
    print("Waiting to receive server's public key...")
    server_public_key = int(s.recv(1024).decode())
    print("Received server's public key:", server_public_key)
    time.sleep(3)

    # Calculate the shared secret key
    shared_secret_key = calculate_shared_secret_key(server_public_key, private_key, prime)
    print("Shared Secret Key:", shared_secret_key)
    time.sleep(3)

    # Start thread to receive messages
    aes_key = s.recv(1024)
    receive_thread = threading.Thread(target=receive_messages, args=(s, shared_secret_key, aes_key))
    receive_thread.start()

    # Chat loop
    while True:
        # Sending message to the server
        message_to_send = input("You: ")
        encrypted_message, iv = encrypt_message(message_to_send, aes_key)
        s.send(iv + encrypted_message)

        if message_to_send.lower() == 'exit':
            break

    s.close()

if __name__ == "__main__":
    client()
