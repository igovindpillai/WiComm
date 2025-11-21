# WiComm/server.py

import socket
import threading
import json


class Server(threading.Thread):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # {client_socket: client_address}
        self.is_running = True

    def run(self):
        """
        Starts the server and listens for incoming connections.
        """
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.server_socket.settimeout(1.0)  # Non-blocking accept
        print(f"Server started on {self.host}:{self.port}")

        while self.is_running:
            try:
                client_socket, client_address = self.server_socket.accept()
                print(f"New connection from {client_address}")
                self.clients[client_socket] = client_address
                # Handle client in a new thread
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()

            except socket.timeout:
                continue
            except Exception as e:
                if self.is_running:
                    print(f"Server error: {e}")

    def handle_client(self, client_socket):
        """
        Handles incoming data from a specific client.
        """
        while self.is_running:
            try:
                data = client_socket.recv(4096)
                if not data:
                    break

                # We expect JSON data with a 'type' key
                message = json.loads(data.decode('utf-8'))

                # If it's a chat message, broadcast it to all other clients
                if message['type'] == 'chat':
                    self.broadcast(data, client_socket)

            except (ConnectionResetError, json.JSONDecodeError):
                break
            except Exception as e:
                print(f"Error handling client data: {e}")
                break

        # Clean up client connection
        if client_socket in self.clients:
            print(f"Connection closed by {self.clients[client_socket]}")
            del self.clients[client_socket]
            client_socket.close()

    def broadcast(self, message, sender_socket):
        """
        Sends a message to all connected clients except the sender.
        """
        for client_socket in list(self.clients.keys()):
            if client_socket != sender_socket:
                try:
                    client_socket.sendall(message)
                except Exception as e:
                    print(f"Failed to send to client: {e}")
                    # Remove the failed client
                    del self.clients[client_socket]
                    client_socket.close()

    def stop(self):
        """
        Stops the server gracefully.
        """
        print("Stopping server...")
        self.is_running = False
        self.server_socket.close()