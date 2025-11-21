# WiComm/utils/ip_logger.py

import sqlite3
from datetime import datetime
import threading

db_lock = threading.Lock()
DB_FILE = 'data/logs.db'


def create_database():
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS logs
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           timestamp
                           TEXT,
                           sender_ip
                           TEXT,
                           message_type
                           TEXT,
                           message_content
                           TEXT,
                           gps_location
                           TEXT
                       )
                       ''')

        conn.commit()
        conn.close()


def log_message_to_db(sender_ip, message_content, message_type, gps_location="N/A"):
    with db_lock:
        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            timestamp = datetime.now().isoformat()

            cursor.execute('''
                           INSERT INTO logs (timestamp, sender_ip, message_type, message_content, gps_location)
                           VALUES (?, ?, ?, ?, ?)
                           ''', (timestamp, sender_ip, message_type, message_content, gps_location))

            conn.commit()
            print(f"Logged new entry: {sender_ip} - {message_type}")
        except Exception as e:
            print(f"Error logging to database: {e}")
        finally:
            conn.close()


def get_all_logs():
    with db_lock:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM logs ORDER BY timestamp DESC')
        logs = cursor.fetchall()

        conn.close()
        return logs


create_database()