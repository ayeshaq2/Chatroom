#include <iostream>
#include <string>
#include <cstring>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <json/json.h> // JSON library

int main() {
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

    // Wait for a connection
    sockaddr_in client;
    socklen_t clientSize = sizeof(client);
    int clientSocket = accept(listening, (sockaddr*)&client, &clientSize);
    if (clientSocket == -1) {
        std::cerr << "Error: Can't accept client connection!" << std::endl;
        return -1;
    }

    // Buffer to store received data
    char buf[4096];
    memset(buf, 0, 4096);

    // Receive JSON message from client
    ssize_t bytesReceived = recv(clientSocket, buf, 4096, 0);
    if (bytesReceived == -1) {
        std::cerr << "Error in recv()" << std::endl;
        close(clientSocket);
        close(listening);
        return -1;
    }

    // Parse received JSON data
    Json::CharReaderBuilder builder;
    Json::Value jsonData;
    std::string parseErrors;
    std::istringstream jsonStream(std::string(buf, bytesReceived));
    if (!Json::parseFromStream(builder, jsonStream, &jsonData, &parseErrors)) {
        std::cerr << "Error parsing JSON: " << parseErrors << std::endl;
        close(clientSocket);
        close(listening);
        return -1;
    }

    // Extract data from JSON
    std::string clientName = jsonData["name"].asString();
    std::string message = jsonData["message"].asString();
    int clientId = jsonData["groupchat_id"].asInt();

    // Print received data
    std::cout << "Received JSON from frontend:" << std::endl;
    std::cout << "Client Name: " << clientName << std::endl;
    std::cout << "Message: " << message << std::endl;
    std::cout << "Groupchat ID: " << clientId << std::endl;

    // Send response to the frontend
    std::string response = "Hello from backend!";
    send(clientSocket, response.c_str(), response.size() + 1, 0);

    // Close the socket
    close(clientSocket);
    close(listening);

    return 0;
}
