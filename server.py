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
    message_type = sys.argv[3]
    if message_type == 'Publish':
        final_message = ""
        for i in range(3, len(sys.argv)):
            final_message += sys.argv[i]
            final_message += " "
        s.sendall(final_message.encode())
        while True:
            try:
                data = s.recv(1024)
            except Exception:
                print("unsuccessful, your connection has been closed")
                break
            if data.decode() == 'Ping':
                final_message = "Pong"
                s.sendall(final_message.encode())
            elif len(data.decode()) > 0:
                print("your message published successfully")
                # if "PubAck" in data.decode():
                #     print(data.decode())