#include <iostream>
#include <string>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <mutex>
#include <queue>
#include <chrono>
#include <thread>
#include <unordered_map>
#include <vector>
#include <json/json.h> // JSON library

std::mutex mtx; //mutex for access to message queue
std::queue<std::string> messageQ; //queue storing messages

//structure for groupchats
struct GroupChat{
    std::vector<int> participants;
};

//groupchat class
class GroupChats{
    //constructor
    public:
        std::unordered_map<std::string, GroupChat> groupChats;
    //methods
    public:
        //new groupchat
        void createGroupChat(const std::string& groupChatName, const std::vector<int>& initialParticipant){
            groupChats[groupChatName] = {initialParticipant};
        }

        //add participant to groupchat
        void addParticipant(const std::string& groupChatName, int participant){
            groupChats[groupChatName].participants.push_back(participant);
        }
};
//initialize groupchats
GroupChats groupChatList;


//send messages
void sendMessage(){
    //access the queue, send message based on groupchat
    while (true){
        mtx.lock();
        if(!messageQ.empty()){
            //get message
            std::string messageDetails = messageQ.front();
            //remove from queue
            messageQ.pop();
            //print message
            std::cout << "From queue: " << messageDetails << std::endl;
            //send message to specific groupchat
            //parse into json
            Json::Value messageJson;
            Json::Reader reader;
            if (reader.parse(messageDetails, messageJson)) {
                std::string groupchatId = messageJson["groupchat_id"].asString();
                //check participants
                const std::vector<int>& participants = groupChatList.groupChats[groupchatId].participants;
                //for each participant, send message
                for (int client : participants){
                    std::cout << "Sent to client: " << client << std::endl;
                    send(client, messageJson["message"].asString().c_str(), messageJson["message"].asString().size() + 1, 0);
                }
            } else {
                std::cerr << "Error parsing message JSON: " << reader.getFormattedErrorMessages() << std::endl;
            }

        }
        mtx.unlock();
    }

}

//method to receive messages
void receiveMessage(int clientSocket){
    while(true){
        // Buffer to store received data
        char buf[4096];
        memset(buf, 0, 4096);

        // Receive JSON message from client
        ssize_t bytesReceived = recv(clientSocket, buf, 4096, 0);
        if (bytesReceived == -1) {
            std::cerr << "Error in recv()" << std::endl;
            close(clientSocket);
            return;
        }
        
        // Parse received JSON data
        Json::CharReaderBuilder builder;
        Json::Value jsonData;
        std::string parseErrors;
        std::istringstream jsonStream(std::string(buf, bytesReceived));
        if (!Json::parseFromStream(builder, jsonStream, &jsonData, &parseErrors)) {
            std::cerr << "Error parsing JSON: " << parseErrors << std::endl;
            close(clientSocket);
            return;
        }

        // Extract data from JSON
        std::string clientName = jsonData["name"].asString();
        std::string message = jsonData["message"].asString();
        std::string clientId = jsonData["groupchat_id"].asString();
        //add socket to data
        jsonData["client_socket"] = clientSocket;

        // Print received data
        std::cout << "Received JSON from frontend:" << std::endl;
        std::cout << "Client Name: " << clientName << std::endl;
        std::cout << "Message: " << message << std::endl;
        std::cout << "Groupchat ID: " << clientId << std::endl;

        std::string res = "Hello fro,m backend";
        // send(clientSocket, res.c_str(), res.size() + 1, 0);
        // std::cout << "SOCKET: " << clientSocket << std::endl;
        //add data to queue
        //lock mutex
        mtx.lock();
        //add message
        messageQ.push(jsonData.toStyledString());
        //unlock
        mtx.unlock();
        //sendMessage();
    }
}


int main() {
    //test-> initialize groupchat
    groupChatList.createGroupChat("GC", {});
    //initialize sender method thread
    std::thread senderThread(sendMessage);
    // Create a socket
    int listening = socket(AF_INET, SOCK_STREAM, 0);
    if (listening == -1) {
        std::cerr << "Error: Can't create socket!" << std::endl;
        return -1;
    }

    // Bind the socket to an IP address and port
    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(12349);
    hint.sin_addr.s_addr = INADDR_ANY; // Use any IP address on the local machine

    if (bind(listening, (sockaddr*)&hint, sizeof(hint)) == -1) {
        std::cerr << "Error: Can't bind to IP/port!" << std::endl;
        return -1;
    }

    // Tell the socket to listen for incoming connections
    if (listen(listening, SOMAXCONN) == -1) {
        std::cerr << "Error: Can't listen!" << std::endl;
        return -1;
    }

    //infinite loop
    while (true){
        // Wait for a connection
        sockaddr_in client;
        socklen_t clientSize = sizeof(client);
        int clientSocket = accept(listening, (sockaddr*)&client, &clientSize);
        std::cout << "Intial client socket: " << clientSocket << std::endl;
        if (clientSocket == -1) {
            std::cerr << "Error: Can't accept client connection!" << std::endl;
            return -1;
        }
        //add client to groupchat
        groupChatList.addParticipant("GC", clientSocket);
        //create thread to receive messages from client
        std::thread clientThread(receiveMessage, clientSocket);
        clientThread.detach();
        //close(clientSocket);
    }
    close(listening);
    return 0;
}
