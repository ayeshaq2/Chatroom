import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import socket

class Frontend(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Frontend')
        layout = QVBoxLayout()
        self.btn_send = QPushButton('Send Message to Backend')
        self.btn_send.clicked.connect(self.send_message)
        layout.addWidget(self.btn_send)
        self.setLayout(layout)

    def send_message(self):
        try:
            # Create a socket object
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Connect to the backend
            client_socket.connect(('localhost', 12347))
            # Send message to the backend
            client_socket.sendall(b'Hello from frontend!')
            # Receive response from the backend
            response = client_socket.recv(1024)
            print(f'Received from backend: {response.decode()}')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            client_socket.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    frontend = Frontend()
    frontend.show()
    sys.exit(app.exec_())
