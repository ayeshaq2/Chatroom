import sys
import time
import select
import errno
import json
import socket
import threading
import random
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QTextEdit, QLineEdit, QLabel, QComboBox, QInputDialog, QMessageBox
from PyQt5.QtCore import Qt, QDateTime, QTimer, QThread, pyqtSignal


class Client(QWidget):
    connection_lost_signal = pyqtSignal()

    #defining some UI features
    def __init__(self):
        super().__init__()
        self.client_socket = None
        
        #self.connection_timer = QTimer()
        #self.connection_timer.timeout.connect(self.handle_connection_lost)
        self.connection_lost = False
        self.server_shutdown_handled = False
        
        self.gc = None  # Current chat room
        self.id = None  # Client's username
        self.user_colors = {}  # Stores colors assigned to users
        self.shades_of_pink = ['#FFC0CB', '#FFB6C1', '#FF69B4', '#FF1493', '#DB7093',
                                '#C71585', '#E6E6FA', '#D8BFD8', '#DDA0DD', '#EE82EE']  # Predefined shades of pink
        self.init_ui()

    #creating the UI 
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

        self.header_label = QLabel("Chatroom")
        self.header_label.setAlignment(Qt.AlignCenter)
        font = self.header_label.font()
        font.setPointSize(16)
        self.header_label.setFont(font)
        layout.addWidget(self.header_label)

        self.message_display = QTextEdit()
        self.message_display.setReadOnly(True)
        layout.addWidget(self.message_display)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type a message...")
        self.input_field.returnPressed.connect(self.send_message)
        layout.addWidget(self.input_field)

        self.leave_chatroom_button = QPushButton("Leave Chatroom")
        self.leave_chatroom_button.clicked.connect(self.leave_chat_room)
        layout.addWidget(self.leave_chatroom_button)


        self.btn_send = QPushButton('Send')
        self.btn_send.clicked.connect(self.send_message)
        layout.addWidget(self.btn_send)

        self.setLayout(layout)

    #method to define a participant leavinga chatroom 
    def leave_chat_room(self):
        if self.gc:
            data = {
                "name":self.id,
                "leave":self.gc
            }

            self.send_data(data)
            self.gc = None
            self.message_display.clear()    #clears history for that participant
            self.chat_room_selector.setCurrentIndex(0) #changes current chatroom
            QMessageBox.information(self, "Chat Room", "You have left the chatroom.")
        else:
            QMessageBox.warning(self, "Chat Room", "You are not in any chat room")

    #generating a colour for participant messages
    def generate_user_color(self, username):
        if username not in self.user_colors:
            self.user_colors[username] = random.choice(self.shades_of_pink)
        return self.user_colors[username]

    #method that displays all the messages within the chatroom display
    def display_message(self, message, username):
        #it displays the messages with the name of the participant, using one of the colours, and adds a timestamp 
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

    #displays the selected chatroom
    def on_chat_room_selected(self, index):
        if index > 0:
            chat_room_name = self.chat_room_selector.itemText(index)
            self.header_label.setText(f"Current Chatroom: {chat_room_name}")
            self.join_chat_room(chat_room_name)

    #method that allows the user to join a chatroom 
    def join_chat_room(self, name):
        self.clear_messages()
        self.gc = name
        data = {
            "name": self.id,
            "join": name
        }
        self.send_data(data)

    #clears the chatroom display
    def clear_messages(self):
        self.message_display.clear()

    #method with functionality to create a chatroom
    def create_chat_room(self):
        chat_room_name = self.new_chat_room_name.text()
        if chat_room_name:
            self.gc = chat_room_name

            #the following data is sent, adding the groupchat 
            data = {
                "name": self.id,
                "create": chat_room_name
            }
            self.send_data(data)
            self.chat_room_selector.addItem(chat_room_name)
            self.chat_room_selector.setCurrentIndex(self.chat_room_selector.count() - 1)
            self.new_chat_room_name.clear()


    #updating the dropdown chatrooms list when a new one is created
    def update_chat_room_list(self, chat_rooms):
        #print("Chat rooms:", chat_rooms)
        self.chat_room_selector.clear()
        self.chat_room_selector.addItem("Select a chat room")
        for chat_room in chat_rooms:
            self.chat_room_selector.addItem(chat_room)

    #sending a message into a selected chatroom:
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

    #sending the data to our server connection, in json format to be parsed and iterated
    def send_data(self, data):
        try:
            json_data = json.dumps(data)
            self.client_socket.sendall(json_data.encode())
        except Exception as e:
            self.message_display.append(f'Error: {e}')

    #receiving a message from the server
    def receive_message(self):
        try:
            #parsing the message
            while not self.connection_lost:
                response = self.client_socket.recv(1024)
                if response:
                    response_data_list = response.decode().split('\x00')
                    #response_data = json.loads(response.decode().rstrip(response.decode()[-1]))
                    for i, response_data_str in enumerate(response_data_list):
                        if not response_data_str:
                            continue

                        #group message:
                        response_data = json.loads(response_data_str)
                        if "message" in response_data:
                            message = response_data["message"]
                            username = response_data["name"]
                            self.display_message(message, username)
                        
                        #group chat names:
                        elif "group_chat_names" in response_data:
                            names = response_data["group_chat_names"].split(',')
                            #self.chat_room_selector.addItems(names)
                            self.update_chat_room_list(names)

                        #a new chatroom is created:
                        elif "new_chat_room" in response_data:
                            new_room = response_data["new_chat_room"]
                            if self.chat_room_selector.findText(new_room) == -1:
                                self.chat_room_selector.addItem(new_room)
                        # elif "type" in response_data and response_data["type"] == "server_shutdown":
                        #     if not self.server_shutdown_handled:

                        #         self.handle_connection_lost()
                        #         self.server_shutdown_handled = True
                        #         #response_data_list = response_data_list[:i+1]
                        #         #break

        #exception that handles a server error/shutdown:
        except ConnectionError as ce:
            if ce.errno == errno.ECONNRESET or ce.errno == errno.EPIPE:
                self.connection_lost_signal.emit()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error receieving message: {e}, {response}")
            self.message_display.append(f'Error receiving message: {e} , {response}')
            self.connection_lost = True
            #self.connection_timer.start(5000)

    #informs the user that server connection was lost:
    def handle_connection_lost(self):
        reply = QMessageBox.warning(self, "Connection Lost", "Server connection lost. Please restart the application")
        #time.sleep(10)
        if reply == QMessageBox.Ok:
            sys.exit()

    #how the client connects to the server, using socket programming
    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #self.client_socket.connect(('localhost', 12349))
            self.client_socket.connect(('34.234.80.97', 12349))

            threading.Thread(target=self.receive_message, daemon=True).start()
        except ConnectionRefusedError as ce:
            if ce.errno == errno.ECONNRESET or ce.errno == errno.EPIPE:
                QMessageBox.critical(self, "Connection Error", "Unable to connect to the server. Please make sure the server is running.")
                sys.exit()  
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Error connecting to server: {e}")
            sys.exit()  
            

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    client.connect_to_server()
    client.connection_lost_signal.connect(client.handle_connection_lost)
    sys.exit(app.exec_())
