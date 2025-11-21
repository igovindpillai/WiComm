# Wi-COMM: More Than Just a Signal

A secure, local communication platform prototype built with Python. It features an aesthetic UI, end-to-end encrypted text messaging, and one-to-one voice calling over a local Wi-Fi network (LAN).

## Features

- **Peer-to-Peer Communication**: Works entirely on your local network, no internet required.
- **Secure Messaging**: All text messages are encrypted using AES-256 before transmission.
- **Real-time Voice Calling**: Low-latency voice calls using UDP, with optional encryption.
- **Aesthetic UI**: A clean, modern interface built with PyQt5 and custom QSS styling.
- **Local Logging**: Stores communication and metadata (IP addresses, timestamps) in a local SQLite database.

## Prerequisites

- **Python 3.10+**: Ensure you have a recent version of Python installed.
- **Required Libraries**: All necessary dependencies can be installed using pip.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/igovindpillai/WiComm.git](https://github.com/your-username/WiComm.git)
    cd WiComm
    ```

2.  **Install dependencies:**
    ```bash
    pip install PyQt5 pyaudio pycryptodomex
    ```
    *Note: If you encounter issues with `pyaudio`, you may need to install system-level audio libraries.*

## How to Run

The `main.py` script automatically handles the client/server logic. It will start a server if one is not detected on the network, and then it will launch the client.

1.  **Start the first instance:**
    ```bash
    python main.py
    ```
    This will start a server and a client on your machine.

2.  **Start another instance on a different machine on the same Wi-Fi network:**
    ```bash
    python main.py
    ```
    This second instance will detect the running server and connect to it as a client. You can now communicate between the two machines.

3.  **To start a voice call:**
    - Click the "Start Call" button.
    - The voice call is a one-to-one connection. Ensure you know the target IP address and connect to it directly. (Note: The current prototype initiates a local call; for peer-to-peer, you would select a user from the list to call).

## Folder Structure
```text
WiComm/
├── main.py
├── server.py
├── client.py
├── ui/
│   ├── chat_ui.py
│   └── style.qss
├── voice/
│   └── voice_stream.py
├── encryption/
│   └── aes_utils.py
├── utils/
│   ├── ip_logger.py
│   └── location.py
├── data/
│   └── logs.db
├── README.md
└── LICENSE