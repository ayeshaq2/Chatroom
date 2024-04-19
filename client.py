import sys
import json
import socket
import threading
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLineEdit, QLabel, QComboBox, QInputDialog
from PyQt5.QtCore import Qt, QDateTime

class Client(QWidget):
    def __init__(self):
        super().__init__()
        self.client_socket = None
        self.gc = None  # Current chat room
        self.id = None  # Client's username
        self.user_colors = {}  # Stores colors assigned to users
        self.shades_of_pink = ['#FFC0CB', '#FFB6C1', '#FF69B4', '#FF1493', '#DB7093',
                                '#C71585', '#E6E6FA', '#D8BFD8', '#DDA0DD', '#EE82EE']  # Predefined shades of pink
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Chat Room')
        self.setGeometry(100, 100, 500, 900)
        layout = QVBoxLayout()

        self.id, okPressed = QInputDialog.getText(self, "Enter Name", "Your name:")
        if not okPressed or not self.id:
            sys.exit()

        self.label = QLabel("Select or create a chat room:")
        layout.addWidget(self.label)

        self.chat_room_selector = QComboBox()
        self.chat_room_selector.addItem("Select a chat room")
        self.chat_room_selector.currentIndexChanged.connect(self.on_chat_room_selected)
        layout.addWidget(self.chat_room_selector)

        self.new_chat_room_name = QLineEdit()
        self.new_chat_room_name.setPlaceholderText("Enter a new chat room name...")
        layout.addWidget(self.new_chat_room_name)

        self.create_chat_room_button = QPushButton('Create New Chat Room')
        self.create_chat_room_button.clicked.connect(self.create_chat_room)
        layout.addWidget(self.create_chat_room_button)

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)

        self.btn_send = QPushButton('Send')
        self.btn_send.clicked.connect(self.send_message)
        layout.addWidget(self.btn_send)

        self.setLayout(layout)

    def generate_user_color(self, username):
        if username not in self.user_colors:
            self.user_colors[username] = random.choice(self.shades_of_pink)
        return self.user_colors[username]

    def display_message(self, message, username):
        current_datetime = QDateTime.currentDateTime().toString('dd/MM/yyyy HH:mm')
        color = self.generate_user_color(username)
        message_html = f"""
            <div style='margin: 5px;'>
                <div style='margin-bottom: 2px; color: {color};'><b>{username}</b></div>
                <div style='padding: 5px 10px; background-color: {color}; color: #ffffff; 
                    border-radius: 15px; max-width: fit-content; word-wrap: break-word;'>
                    {message}
                </div>
                <div style='margin-top: 2px; font-size: 8pt; color: #888888;'>{current_datetime}</div>
            </div>
        """
        self.message_display.append(message_html)

    def on_chat_room_selected(self, index):
        if index > 0:
            chat_room_name = self.chat_room_selector.itemText(index)
            self.join_chat_room(chat_room_name)

    def join_chat_room(self, name):
        self.gc = name
        data = {
            "name": self.id,
            "join": name
        }
        self.send_data(data)

    def create_chat_room(self):
        chat_room_name = self.new_chat_room_name.text()
        if chat_room_name:
            self.gc = chat_room_name
            data = {
                "name": self.id,
                "create": chat_room_name
            }
            self.send_data(data)
            self.chat_room_selector.addItem(chat_room_name)
            self.chat_room_selector.setCurrentIndex(self.chat_room_selector.count() - 1)
            self.new_chat_room_name.clear()

    def send_message(self):
        message = self.input_field.text()
        if message and self.gc:
            self.input_field.clear()
            data = {
                "name": self.id,
                "message": message,
                "groupchat_id": self.gc
            }
            self.send_data(data)

    def send_data(self, data):
        try:
            json_data = json.dumps(data)
            self.client_socket.sendall(json_data.encode())
        except Exception as e:
            self.message_display.append(f'Error: {e}')

    def receive_message(self):
        try:
            while True:
                response = self.client_socket.recv(1024)
                if response:
                    response_data = json.loads(response.decode().rstrip(response.decode()[-1]))
                    if "message" in response_data:
                        message = response_data["message"]
                        username = response_data["name"]
                        self.display_message(message, username)
                    elif "group_chat_names" in response_data:
                        names = response_data["group_chat_names"].split(',')
                        self.chat_room_selector.addItems(names)
        except Exception as e:
            self.message_display.append(f'Error receiving message: {e}')

    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('localhost', 12349))
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            self.message_display.append(f'Error connecting to server: {e}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    client.connect_to_server()
    sys.exit(app.exec_())
