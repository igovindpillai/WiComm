# WiComm/voice/voice_stream.py

import pyaudio
import socket
import threading
from encryption.aes_utils import encrypt_data, decrypt_data


class VoiceStream(threading.Thread):
    def __init__(self, target_ip, encryption_key):
        super().__init__()
        self.target_ip = target_ip
        self.port = 5001
        self.encryption_key = encryption_key

        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

        self.p = pyaudio.PyAudio()
        self.stream = None
        self.is_running = False

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start_stream(self):
        print("Starting voice stream...")
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  output=True,
                                  frames_per_buffer=self.CHUNK)
        self.is_running = True
        self.start()

    def run(self):
        self.server_socket.bind(('', self.port))

        send_thread = threading.Thread(target=self._send_audio, daemon=True)
        receive_thread = threading.Thread(target=self._receive_audio, daemon=True)

        send_thread.start()
        receive_thread.start()

        send_thread.join()
        receive_thread.join()

    def _send_audio(self):
        while self.is_running:
            try:
                data = self.stream.read(self.CHUNK)
                encrypted_data = encrypt_data(data, self.encryption_key)
                self.client_socket.sendto(encrypted_data, (self.target_ip, self.port))
            except IOError as e:
                print(f"Error reading from audio stream: {e}")
                self.is_running = False
            except Exception as e:
                print(f"Error sending audio: {e}")

    def _receive_audio(self):
        while self.is_running:
            try:
                data, addr = self.server_socket.recvfrom(4096)
                decrypted_data = decrypt_data(data, self.encryption_key)
                self.stream.write(decrypted_data)
            except Exception as e:
                print(f"Error receiving audio: {e}")

    def stop_stream(self):
        if self.is_running:
            print("Stopping voice stream...")
            self.is_running = False
            self.stream.stop_stream()
            self.stream.close()
            self.p.terminate()
            self.client_socket.close()
            self.server_socket.close()