import socket
import random
import time
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import tkinter as tk

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
def receive_messages(s, shared_secret_key, aes_key, text_frame):
    while True:
        encrypted_message = s.recv(1024)
        iv = encrypted_message[:16]
        ciphertext = encrypted_message[16:]
        decrypted_message = decrypt_message(ciphertext, aes_key, iv)

        label = tk.Label(text_frame, text="Server: " + decrypted_message, anchor="w", justify="left", bg="#ddeedd", fg="black", padx=10, pady=5, font=("Helvetica", 10))
        label.pack(fill="x", padx=10, pady=2)
        text_frame.update_idletasks()

def send_message(s, aes_key, message_entry, text_frame):
    message_to_send = message_entry.get()
    encrypted_message, iv = encrypt_message(message_to_send, aes_key)
    s.send(iv + encrypted_message)

    label = tk.Label(text_frame, text="You: " + message_to_send, anchor="e", justify="right", bg="#aaddaa", fg="white", padx=10, pady=5, font=("Helvetica", 10))
    label.pack(fill="x", padx=10, pady=2)
    text_frame.update_idletasks()

    if message_to_send.lower() == 'exit':
        s.close()
        root.quit()
    message_entry.delete(0, tk.END)

def client():
    host = '127.0.0.1'
    port = 12345

    s = socket.socket()
    s.connect((host, port))

    # Receive prime and base values from the server
    print("Waiting to receive prime...")
    s_prime = int(s.recv(1024).decode())
    print("Received prime:", s_prime)
   

    print("Waiting to receive base...")
    s_base = int(s.recv(1024).decode())
    print("Received base:", s_base)
    

    prime, base, private_key, public_key = diffie_hellman(s_prime, s_base)

    # Send public key to the server
    print("Sending public key...")
    s.send(str(public_key).encode())
    print("Sent public key:", public_key)
   

    # Receive the server's public key
    print("Waiting to receive server's public key...")
    server_public_key = int(s.recv(1024).decode())
    print("Received server's public key:", server_public_key)
    

    # Calculate the shared secret key
    shared_secret_key = calculate_shared_secret_key(server_public_key, private_key, prime)
    print("Shared Secret Key:", shared_secret_key)
  

    # Initialize GUI
    root = tk.Tk()
    root.title("Client Chat")

    text_frame = tk.Frame(root, bg="#f0f0f0")
    text_frame.pack(fill="both", expand=True)

    message_entry = tk.Entry(root, bg="white", fg="black", font=("Helvetica", 12))
    message_entry.pack(side="bottom", fill="x", padx=10, pady=5)

    send_button = tk.Button(root, text="Send", command=lambda: send_message(s, aes_key, message_entry, text_frame), bg="#008080", fg="white", font=("Helvetica", 12))
    send_button.pack(side="bottom", fill="x", padx=10, pady=5)

    # Start thread to receive messages
    aes_key = s.recv(1024)
    receive_thread = threading.Thread(target=receive_messages, args=(s, shared_secret_key, aes_key, text_frame))
    receive_thread.start()

    root.mainloop()

if __name__ == "__main__":
    client()
