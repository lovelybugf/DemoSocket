import socket
import hashlib

# Thay bằng mã sinh viên và tên của bạn
STUDENT_ID = "B22DCAT206"
STUDENT_NAME = "Phạm Đức Nam"
SECRET_KEY = "mysecretkey"

def calculate_hash(message):
    # Tính giá trị băm của (thông điệp + key)
    return hashlib.sha256((message + SECRET_KEY).encode()).hexdigest()

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 12345))
    print("Connected to server")

    # Gửi thông điệp kèm giá trị băm
    message = f"Hello, I am {STUDENT_ID} client"
    message_hash = calculate_hash(message)
    data_to_send = f"{message}|{message_hash}"
    client_socket.send(data_to_send.encode())
    print(f"Sent to server: {message}")
    print(f"Sent hash: {message_hash}")

    # Nhận phản hồi từ server
    response = client_socket.recv(1024).decode()
    print(f"Received from server: {response}")

    # Đóng kết nối
    client_socket.close()

if __name__ == "__main__":
    start_client()