import socket
import threading
import json
import tkinter as tk
from tkinter import messagebox
from security import Security
from database import Database
import base64

class ChatClient:
    def __init__(self, host='localhost', port=12345):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.security = Security()
        self.db = Database()
        self.username = None

        # Giao diện GUI
        self.root = tk.Tk()
        self.root.title("Secure Chat System")
        self.root.geometry("600x500")

        # Form đăng nhập/đăng ký
        self.auth_frame = tk.Frame(self.root)
        self.auth_frame.pack(pady=10)

        tk.Label(self.auth_frame, text="Username").grid(row=0, column=0)
        self.username_entry = tk.Entry(self.auth_frame)
        self.username_entry.grid(row=0, column=1)

        tk.Label(self.auth_frame, text="Password").grid(row=1, column=0)
        self.password_entry = tk.Entry(self.auth_frame, show="*")
        self.password_entry.grid(row=1, column=1)

        tk.Button(self.auth_frame, text="Login", command=self.login).grid(row=2, column=0, pady=5)
        tk.Button(self.auth_frame, text="Register", command=self.register).grid(row=2, column=1)

        # Khu vực chat (ẩn ban đầu)
        self.chat_frame = tk.Frame(self.root)
        self.chat_area = tk.Text(self.chat_frame, height=20, width=50)
        self.chat_area.pack(pady=10)
        self.message_entry = tk.Entry(self.chat_frame, width=40)
        self.message_entry.pack(side=tk.LEFT, padx=5)
        tk.Button(self.chat_frame, text="Send", command=self.send_message).pack(side=tk.LEFT)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        packet = {'type': 'login', 'username': username, 'password': password}
        self.client.send(json.dumps(packet).encode())
        response = json.loads(self.client.recv(1024).decode())
        if response['status'] == 'success':
            self.username = username
            self.auth_frame.pack_forget()
            self.chat_frame.pack()
            self.load_chat_history()
            threading.Thread(target=self.receive_messages, daemon=True).start()
        else:
            messagebox.showerror("Error", "Login failed!")

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        packet = {'type': 'register', 'username': username, 'password': password}
        self.client.send(json.dumps(packet).encode())
        response = json.loads(self.client.recv(1024).decode())
        if response['status'] == 'success':
            messagebox.showinfo("Success", "Registration successful! Please login.")
        else:
            messagebox.showerror("Error", "Registration failed!")

    def load_chat_history(self):
        history = self.db.get_chat_history(self.username)
        for entry in history:
            username, message, timestamp = entry
            self.chat_area.insert(tk.END, f"[{timestamp}] {username}: {message}\n")

    def send_message(self):
        message = self.message_entry.get()
        if message:
            encrypted_message = self.security.encrypt_message(message)
            message_hmac = self.security.generate_hmac(encrypted_message)
            packet = {
                'type': 'message',
                'message': base64.b64encode(encrypted_message).decode(),
                'hmac': message_hmac
            }
            self.client.send(json.dumps(packet).encode())
            self.message_entry.delete(0, tk.END)

    def receive_messages(self):
        while True:
            try:
                data = self.client.recv(1024).decode()
                packet = json.loads(data)
                if packet.get('status') == 'fail':
                    self.chat_area.insert(tk.END, f"Error: {packet['message']}\n")
                else:
                    encrypted_message = base64.b64decode(packet['message'])
                    if self.security.verify_hmac(encrypted_message, packet['hmac']):
                        message = self.security.decrypt_message(encrypted_message)
                        self.chat_area.insert(tk.END, f"{message}\n")
                    else:
                        self.chat_area.insert(tk.END, "Error: Message integrity check failed.\n")
            except:
                break

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    client = ChatClient()
    client.run()