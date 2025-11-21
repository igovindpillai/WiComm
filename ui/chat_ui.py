# WiComm/ui/chat_ui.py

from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, \
    QListWidget, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import threading

from voice.voice_stream import VoiceStream


class ChatApp(QMainWindow):
    def __init__(self, client, server=None):
        super().__init__()

        self.client = client
        self.server = server

        self.setWindowTitle("Wi-COMM: More Than Just a Signal")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(10, 10, 10, 10)

        self.user_list_label = QLabel("Connected Peers")
        self.user_list_label.setObjectName("panelTitle")
        self.user_list = QListWidget()
        self.user_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        self.log_label = QLabel("IP & Location Logs")
        self.log_label.setObjectName("panelTitle")
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setPlaceholderText("Logs will appear here...")
        self.log_display.setObjectName("logDisplay")

        left_layout.addWidget(self.user_list_label)
        left_layout.addWidget(self.user_list)
        left_layout.addWidget(self.log_label)
        left_layout.addWidget(self.log_display)

        right_panel = QWidget()
        right_panel.setObjectName("rightPanel")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(10, 10, 10, 10)

        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        self.chat_history.setObjectName("chatHistory")
        self.chat_history.setPlaceholderText("Start a conversation...")

        input_layout = QHBoxLayout()
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type a message...")
        self.message_input.setObjectName("messageInput")
        self.message_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self.send_message)

        self.call_button = QPushButton("Start Call")
        self.call_button.setObjectName("callButton")
        self.call_button.clicked.connect(self.toggle_call)

        input_layout.addWidget(self.message_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.call_button)

        right_layout.addWidget(self.chat_history)
        right_layout.addLayout(input_layout)

        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 3)

        self.voice_stream = None

        self.client.message_received.connect(self.display_message)
        self.client.peer_list_updated.connect(self.update_peer_list)
        self.client.log_message.connect(self.add_log_entry)

        self.client.start()

    def send_message(self):
        message = self.message_input.text().strip()
        if message:
            self.client.send_message(message)
            self.message_input.clear()

    def display_message(self, message):
        self.chat_history.append(message)

    def update_peer_list(self, peers):
        self.user_list.clear()
        for peer in peers:
            self.user_list.addItem(peer)

    def add_log_entry(self, log_entry):
        self.log_display.append(log_entry)

    def toggle_call(self):
        if self.voice_stream and self.voice_stream.is_running:
            self.voice_stream.stop_stream()
            self.voice_stream = None
            self.call_button.setText("Start Call")
            self.add_log_entry("Voice call ended.")
        else:
            target_ip = self.client.host

            if target_ip:
                self.voice_stream = VoiceStream(target_ip, self.client.encryption_key)
                self.voice_stream.start_stream()
                self.call_button.setText("End Call")
                self.add_log_entry(f"Voice call started with {target_ip}...")
            else:
                self.add_log_entry("Error: Could not determine target IP for call.")

    def closeEvent(self, event):
        if self.voice_stream:
            self.voice_stream.stop_stream()

        if self.server:
            self.server.stop()
        self.client.stop()
        event.accept()