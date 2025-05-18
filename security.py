from cryptography.fernet import Fernet
import hmac
import hashlib
import base64

class Security:
    def __init__(self):
        # Tạo khóa mã hóa AES
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.hmac_key = b'my_hmac_secret_key'

    def encrypt_message(self, message):
        # Mã hóa thông điệp
        return self.cipher.encrypt(message.encode())

    def decrypt_message(self, encrypted_message):
        # Giải mã thông điệp
        return self.cipher.decrypt(encrypted_message).decode()

    def generate_hmac(self, message):
        # Tạo HMAC cho thông điệp
        if isinstance(message, str):
            message = message.encode()
        return hmac.new(self.hmac_key, message, hashlib.sha256).hexdigest()

    def verify_hmac(self, message, received_hmac):
        # Kiểm tra tính toàn vẹn
        if isinstance(message, str):
            message = message.encode()
        expected_hmac = hmac.new(self.hmac_key, message, hashlib.sha256).hexdigest()
        return expected_hmac == received_hmac