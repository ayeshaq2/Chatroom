import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import socket
import json

class Client(QWidget):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Frontend')
        layout = QVBoxLayout()
        self.btn_send = QPushButton('Send Message to Backend')
        self.btn_send.clicked.connect(self.send_message)
        layout.addWidget(self.btn_send)
        self.setLayout(layout)

    def send_message(self, message):
        try:
            groupchat_id = 1
            data={
                "name":self.id,
                "message":message,
                "groupchat_id":groupchat_id
            }
            # serialize the dictionary to json format
            json_data = json.dumps(data)
            # Create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the backend
            client_socket.connect(('localhost', 12349))
            # Send message to the backend
            client_socket.sendall(json_data.encode())
            # Receive response from the backend
            response = client_socket.recv(1024)
            print(f'Received from backend: {response.decode()}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            client_socket.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client('nada')
    client.show()
    message = input('Type a message to send: ')
    client.send_message(message)
    sys.exit(app.exec_())
