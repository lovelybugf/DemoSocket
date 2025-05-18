import socket
import hashlib

# Thay bằng mã sinh viên và tên của bạn
STUDENT_ID = "B22DCAT206"
STUDENT_NAME = "Phạm Đức Nam"
SECRET_KEY = "B22DCAT206"

def verify_integrity(message, received_hash):
    expected_hash = hashlib.sha256((message + SECRET_KEY).encode()).hexdigest()
    return expected_hash == received_hash

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 12345))  # Thay bằng IP nếu cần
    server_socket.listen(1)
    print("Server is listening on port 12345...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connected to {addr}")

        data = client_socket.recv(1024).decode()
        if not data:
            client_socket.close()
            continue

        try:
            message, received_hash = data.rsplit('|', 1)
            print(f"Received message: {message}")
            print(f"Received hash: {received_hash}")

            if verify_integrity(message, received_hash):
                print("Message integrity verified.")
                response = f"Hello, I am {STUDENT_ID} server"
            else:
                print("Message integrity check failed.")
                response = "The received message has lost its integrity."

            client_socket.send(response.encode())
        except ValueError:
            print("Invalid data format.")
            client_socket.send("Invalid data format.".encode())

        client_socket.close()

if __name__ == "__main__":
    start_server()