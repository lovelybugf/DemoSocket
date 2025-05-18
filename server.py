import socket
import threading
import json
from security import Security
from database import Database

class ChatServer:
    def __init__(self, host='localhost', port=12345):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen()
        self.clients = {}  # {client_socket: username}
        self.security = Security()
        self.db = Database()
        print(f"Server listening on {host}:{port}")

    def broadcast(self, message, sender_socket):
        encrypted_message = self.security.encrypt_message(message)
        message_hmac = self.security.generate_hmac(encrypted_message)
        data = {
            'message': base64.b64encode(encrypted_message).decode(),
            'hmac': message_hmac
        }
        for client_socket in self.clients:
            if client_socket != sender_socket:
                client_socket.send(json.dumps(data).encode())

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024).decode()
                if not data:
                    break
                packet = json.loads(data)

                # Xử lý đăng nhập/đăng ký
                if packet['type'] == 'login':
                    username = packet['username']
                    password = packet['password']
                    if self.db.login_user(username, password):
                        self.clients[client_socket] = username
                        client_socket.send(json.dumps({'status': 'success'}).encode())
                        self.broadcast(f"{username} joined the chat!", client_socket)
                    else:
                        client_socket.send(json.dumps({'status': 'fail'}).encode())

                elif packet['type'] == 'register':
                    username = packet['username']
                    password = packet['password']
                    if self.db.register_user(username, password):
                        client_socket.send(json.dumps({'status': 'success'}).encode())
                    else:
                        client_socket.send(json.dumps({'status': 'fail'}).encode())

                elif packet['type'] == 'message':
                    encrypted_message = base64.b64decode(packet['message'])
                    received_hmac = packet['hmac']
                    if self.security.verify_hmac(encrypted_message, received_hmac):
                        message = self.security.decrypt_message(encrypted_message)
                        username = self.clients[client_socket]
                        self.db.save_message(username, message)
                        formatted_message = f"{username}: {message}"
                        self.broadcast(formatted_message, client_socket)
                    else:
                        client_socket.send(json.dumps({
                            'status': 'fail',
                            'message': 'Message integrity check failed.'
                        }).encode())
            except:
                break

        # Xóa client khi ngắt kết nối
        username = self.clients.pop(client_socket, None)
        if username:
            self.broadcast(f"{username} left the chat!", client_socket)
        client_socket.close()

    def start(self):
        while True:
            client_socket, addr = self.server.accept()
            print(f"Connected to {addr}")
            thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            thread.start()

if __name__ == "__main__":
    server = ChatServer()
    server.start()