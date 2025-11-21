# WiComm/client.py

import socket
import threading
import json
from PyQt5.QtCore import QObject, pyqtSignal

from encryption.aes_utils import encrypt_data, decrypt_data, generate_key
from utils.ip_logger import log_message_to_db # Corrected
from utils.location import get_live_location # New line


class Client(QObject):
    message_received = pyqtSignal(str)
    peer_list_updated = pyqtSignal(list)
    log_message = pyqtSignal(str)

    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.is_running = False
        self.encryption_key = generate_key()

    def start(self):
        try:
            self.client_socket.connect((self.host, self.port))
            self.is_running = True
            self.log_message.emit(f"Connected to server at {self.host}:{self.port}")
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except ConnectionRefusedError:
            self.log_message.emit("Connection refused. The server might not be running.")
        except Exception as e:
            self.log_message.emit(f"Failed to connect: {e}")

    def receive_messages(self):
        while self.is_running:
            try:
                data = self.client_socket.recv(4096)
                if not data:
                    break

                decrypted_data = decrypt_data(data, self.encryption_key)
                if decrypted_data is None:
                    self.log_message.emit("Error: Received tampered or un-decryptable data.")
                    continue

                message = json.loads(decrypted_data.decode('utf-8'))

                if message['type'] == 'chat':
                    sender_ip = message['sender']
                    text = message['content']
                    display_message = f"[{sender_ip}] {text}"

                    self.message_received.emit(display_message)
                    self.log_message.emit(f"Message received from {sender_ip}")

                    log_message_to_db(sender_ip, text, 'text_message', get_live_location())

            except (ConnectionResetError, json.JSONDecodeError) as e:
                if self.is_running:
                    self.log_message.emit(f"Connection lost with server: {e}")
                break
            except Exception as e:
                self.log_message.emit(f"Error receiving message: {e}")
                break

        self.stop()

    def send_message(self, message):
        if not self.is_running:
            self.log_message.emit("Cannot send message. Not connected to a server.")
            return

        try:
            data_to_send = {
                'type': 'chat',
                'sender': socket.gethostbyname(socket.gethostname()),
                'content': message
            }

            json_data = json.dumps(data_to_send).encode('utf-8')
            encrypted_data = encrypt_data(json_data, self.encryption_key)

            if encrypted_data is None:
                self.log_message.emit("Encryption failed. Message not sent.")
                return

            self.client_socket.sendall(encrypted_data)

            display_message = f"[Me] {message}"
            self.message_received.emit(display_message)
            self.log_message.emit(f"Message sent: {message}")

            log_message_to_db('self', message, 'text_message', get_live_location())

        except Exception as e:
            self.log_message.emit(f"Failed to send message: {e}")

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.log_message.emit("Disconnecting from server.")
            self.client_socket.close()