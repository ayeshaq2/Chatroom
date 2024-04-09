import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
import socket
import json
import threading

#global variable to define mode
chatting = False

class Client(QWidget):
    def __init__(self, id):
        super().__init__()
        self.id = id
        self.init_ui()
        self.client_socket = None

    def init_ui(self):
        self.setWindowTitle('Frontend')
        layout = QVBoxLayout()
        self.btn_send = QPushButton('Send Message to Backend')
        self.btn_send.clicked.connect(self.send_message)
        layout.addWidget(self.btn_send)
        self.setLayout(layout)

    def send_message(self, message):
        try:
            groupchat_id = "GC"
            data = {
                "name": self.id,
                "message": message,
                "groupchat_id": groupchat_id
            }
            # Serialize the dictionary to json format
            json_data = json.dumps(data)
            # Send message to the backend
            self.client_socket.sendall(json_data.encode())
        except Exception as e:
            print(f'Error: {e}')
        # finally:
        #     self.client_socket.close()
    
    #receive data
    def receive_message(self):
        try:
            while True:
                response = self.client_socket.recv(1024)
                if response:
                    response_data = json.loads(response.decode().rstrip(response.decode()[-1]))
                    print(f'Receieved from backend: {response_data}')
                    if "client_socket" in response_data:
                        print('message')
                    elif "group_chat_names" in response_data:
                        #intial data send
                        # join gc or create one
                        print('Welcome to the Chat Room! Choose an option from below: ')
                        choice = input('1- Join existing groupchat\n2- Create new groupchat\n')
                        #join
                        if (choice=='1'):
                            print('Available groupchats: ')
                            names = response_data["group_chat_names"].split(',')
                            for i in range(len(names)):
                                print(f'{i+1}: {names[i]}')
                            gc = input('Input number of groupchat you would like to join: ')
                            print(f'Joining groupchat "{names[int(gc)-1]}"...')
                            #send message to join groupchat
                            chatting = True
                        elif (choice=='2'):
                            new_name = input('Input your groupchat name: ')
                            print(f'Creating and joining new groupchat {new_name}...')
                            chatting = True
                        else:
                            print('Invalid choice!')
                # else:
                #     print("Connection closed by server")
                #     break
        except Exception as e:
            print(f'Error receiving message: {e}')
        # finally:
        #     self.client_socket.close()
    def connect_to_server(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(('localhost', 12349))
            #thread to receive messages
            receive_thread = threading.Thread(target=self.receive_message)
            receive_thread.daemon = True
            receive_thread.start()
        except Exception as e:
            print(f'Error connecting to server: {e}')



if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = Client('nada')
    client.show()
    client.connect_to_server()
    while(True):
        if chatting:
            message = input('Type a message to send: ')
            if (message == 'exit'):
                sys.exit()
            client.send_message(message)
    sys.exit(app.exec_())
