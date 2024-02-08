# import socket
# import random
# from prime import primitive_root, getLowLevelPrime, isMillerRabinPassed
# import time
# import threading

# def get_prime_and_base():
#     while True:
#         n = 20
#         prime_candidate = getLowLevelPrime(n)
#         if not isMillerRabinPassed(prime_candidate):
#             continue
#         else:
#             base = primitive_root(prime_candidate)
#             return prime_candidate, base

# def diffie_hellman():
#     prime, base = get_prime_and_base()
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

# def receive_messages(conn, shared_secret_key):
#     while True:
#         encrypted_message = conn.recv(1024).decode()
#         message = decrypt_string(encrypted_message, shared_secret_key)
#         print("\nClient:", message)

# def server():
#     host = '127.0.0.1'
#     port = 12345

#     s = socket.socket()
#     s.bind((host, port))
#     s.listen(1)

#     print("Waiting for incoming connection...")
#     conn, addr = s.accept()
#     print("Connection from: " + str(addr))

#     # Perform Diffie-Hellman key exchange
#     prime, base, private_key, public_key = diffie_hellman()

#     # Send prime to the client
#     print("Sending prime to the client...")
#     conn.send(str(prime).encode())
#     print("Sent prime:", prime)
#     time.sleep(3)

#     # Send base to the client
#     print("Sending base to the client...")
#     conn.send(str(base).encode())
#     print("Sent base:", base)
#     time.sleep(3)

#     # Send public key to the client
#     print("Sending public key to the client...")
#     conn.send(str(public_key).encode())
#     print("Sent public key:", public_key)
#     time.sleep(3)

#     # Receive the client's public key
#     print("Waiting to receive client's public key...")
#     client_public_key = int(conn.recv(1024).decode())
#     print("Received client's public key:", client_public_key)
#     time.sleep(3)

#     # Calculate the shared secret key
#     shared_secret_key = calculate_shared_secret_key(client_public_key, private_key, prime)
#     print("Shared Secret Key:", shared_secret_key)
#     time.sleep(3)

#     # Start thread to receive messages
#     receive_thread = threading.Thread(target=receive_messages, args=(conn, shared_secret_key))
#     receive_thread.start()

#     # Chat loop
#     while True:
#         # Sending message to the client
#         message_to_send = input("You: ")
#         encrypted_message = encrypt_string(message_to_send, shared_secret_key)
#         conn.send(encrypted_message.encode())

#         if message_to_send.lower() == 'exit':
#             break

#     conn.close()

# if __name__ == "__main__":
#     server()
import socket
import random
import time
import threading
from prime import primitive_root, getLowLevelPrime, isMillerRabinPassed
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import hashlib

def get_prime_and_base():
    while True:
        n = 20
        prime_candidate = getLowLevelPrime(n)
        if not isMillerRabinPassed(prime_candidate):
            continue
        else:
            base = primitive_root(prime_candidate)
            return prime_candidate, base

def diffie_hellman():
    prime, base = get_prime_and_base()
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

def receive_messages(conn, shared_secret_key, aes_key):
    while True:
        encrypted_message = conn.recv(1024)
        iv = encrypted_message[:16]
        ciphertext = encrypted_message[16:]
        decrypted_message = decrypt_message(ciphertext, aes_key, iv)
        print("\nClient:", decrypted_message)

def server():
    host = '127.0.0.1'
    port = 12345

    s = socket.socket()
    s.bind((host, port))
    s.listen(1)

    print("Waiting for incoming connection...")
    conn, addr = s.accept()
    print("Connection from: " + str(addr))

    # Perform Diffie-Hellman key exchange
    prime, base, private_key, public_key = diffie_hellman()

    # Send prime to the client
    print("Sending prime to the client...")
    conn.send(str(prime).encode())
    print("Sent prime:", prime)
    time.sleep(3)

    # Send base to the client
    print("Sending base to the client...")
    conn.send(str(base).encode())
    print("Sent base:", base)
    time.sleep(3)

    # Send public key to the client
    print("Sending public key to the client...")
    conn.send(str(public_key).encode())
    print("Sent public key:", public_key)
    time.sleep(3)

    # Receive the client's public key
    print("Waiting to receive client's public key...")
    client_public_key = int(conn.recv(1024).decode())
    print("Received client's public key:", client_public_key)
    time.sleep(3)

    # Calculate the shared secret key
    shared_secret_key = calculate_shared_secret_key(client_public_key, private_key, prime)
    print("Shared Secret Key:", shared_secret_key)
    time.sleep(3)

    # Generate AES key from the shared secret key
    aes_key = hashlib.sha256(str(shared_secret_key).encode()).digest()

    # Send AES key to the client
    conn.send(aes_key)

    # Start thread to receive messages
    receive_thread = threading.Thread(target=receive_messages, args=(conn, shared_secret_key, aes_key))

    receive_thread.start()

    # Chat loop
    while True:
        # Sending message to the client
        message_to_send = input("You: ")
        encrypted_message, iv = encrypt_message(message_to_send, aes_key)
        conn.send(iv + encrypted_message)

        if message_to_send.lower() == 'exit':
            break

    conn.close()

if __name__ == "__main__":
    server()
