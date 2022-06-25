import socket
import sys
import threading
import time

HOST = sys.argv[1]
PORT = int(sys.argv[2])

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        print(HOST, PORT)
        s.connect((HOST, PORT))
        print("trying to connect...")
    except Exception:
        print(f"could not connect to the server {HOST}, {PORT}")
        exit()

    print(f"connected successfully to {HOST}, {PORT}")
