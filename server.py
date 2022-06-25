import socket
import threading
import time

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 1378  # Port to listen on (non-privileged ports are > 1023)


def add_to_subscribers(conn, topic):
    if subscribers.get(topic) is not None:
        subscribers.get(topic).append(conn)
    else:
        subscribers[topic] = [conn]



def send_to_subscribers(topic, message):
    total_message = ""
    for i in range(len(message)):
        total_message += message[i]
    final_message = topic + " : " + total_message
    if subscribers.get(topic) is None:
        return False
    else:
        for connection in subscribers.get(topic):
            try:
                connection.sendall(final_message.encode())
            except Exception:
                print(f"could not send message for {connection} maybe because its closed")
        return True


def waiting_ping(connection, address):
    counter = 0
    connection.settimeout(1)
    while True:
        final_message = "Ping"
        connection.sendall(final_message.encode())
        current_time = time.time()
        while True:
            flag = True
            try:
                reply_message = connection.recv(1024)
            except socket.timeout as e:
                flag = False
                print(f"{address} did not respond to periodic ping")
            final_time = time.time()
            if flag:
                if reply_message.decode() == "Pong":
                    time.sleep(10 - (final_time - current_time))
                    counter = 0
                    break
            if final_time > current_time + 10:
                counter += 1
                print(f"{address} did not respond to periodic ping for {counter * 10} seconds")
                break
        if counter >= 3:
            print(f"{address} did not respond for 3 period and get disconnected", flush=True)
            close_socket(connection)
            break
        else:
            if counter == 0:
                print(f"{address} respond to periodic ping successfully", flush=True)


def message_handler(conn, message):
    msg = message.split(" ")
    message_type = msg[0]
    if message_type == 'Publish':
        topic = msg[1]
        message = msg[2:]
        result = send_to_subscribers(topic, message)
        return_message = "PubAck"
        # if not result:
        #     return_message += " no subscriber on this topic yet"
        # else:
        #     return_message += " send to all subscribers successfully"
    elif message_type == 'Subscribe':
        topic = msg[1]
        add_to_subscribers(conn, topic)
        return_message = f'{topic} : SubAck '
    elif message_type == 'Ping':
        return_message = 'Pong'
    else:
        return_message = 'Non defined'
    return return_message




def handler(conn, addr):
    print(f"connected by {addr}")
    with conn:
        conn.settimeout(1)
        current_time = time.time()
        answered = True
        while True:
            flag = True
            try:
                data = conn.recv(1024)
                answered = False
            except Exception:
                flag = False
            final_time = time.time()
            if flag:
                answer = message_handler(conn, data.decode())
                conn.sendall(answer.encode())
            elif not flag and not answered:
                if final_time < current_time + 10:
                    flag = True
                    break
            elif not flag and answered:
                if final_time > current_time + 10:
                    break

        if flag and not answered:
            waiting_ping(conn, addr)
        else:
            close_socket(conn)
        print('Disconnected by', addr)


def close_socket(conn):
    for connections in subscribers.values():
        if conn in connections:
            connections.remove(conn)
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    print("server is up. ready to go ...")
    s.bind((HOST, PORT))
    s.listen()
    while True:
        conn, addr = s.accept()
        threading.Thread(target=handler, args=(conn, addr)).start()
