# WiComm/main.py

import sys
import socket
from PyQt5.QtWidgets import QApplication
from ui.chat_ui import ChatApp
from server import Server
from client import Client


def is_server_running(host, port):
    """
    Checks if a server is already running on the given host and port.
    """
    try:
        # Create a temporary socket to attempt a connection
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(1)  # Set a short timeout
            s.connect((host, port))
            return True
    except (socket.error, ConnectionRefusedError):
        return False


def run_app():
    """
    Main function to run the Wi-COMM application.
    """
    app = QApplication(sys.argv)

    # Load the custom QSS style sheet
    try:
        with open("ui/style.qss", "r") as f:
            _style = f.read()
            app.setStyleSheet(_style)
    except FileNotFoundError:
        print("Warning: style.qss not found. Running with default PyQt5 style.")

    # Core application setup
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 5000

    server_instance = None

    # Check if a server is already running on the network
    # We use a placeholder IP for this check; actual communication will be local.
    local_ip = socket.gethostbyname(socket.gethostname())

    if not is_server_running(local_ip, port):
        print("No existing server found. Starting a new server instance.")
        # If no server is running, start one on this machine
        server_instance = Server(host, port)
        server_instance.start()

    print("Starting client instance.")
    client_instance = Client(local_ip, port)

    # Initialize the UI
    ui = ChatApp(client_instance, server_instance)
    ui.show()

    # Ensure server thread is properly closed when the app exits
    def close_app():
        if server_instance:
            server_instance.stop()
        client_instance.stop()
        app.quit()

    app.aboutToQuit.connect(close_app)

    sys.exit(app.exec_())


if __name__ == '__main__':
    run_app()