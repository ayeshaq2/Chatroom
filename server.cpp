#include <iostream>
#include <string>
#include <cstring>  // For memset
#include <unistd.h> // For close
#include <sys/socket.h>
#include <netinet/in.h>

int main()
{
    // Create a socket
    int listening = socket(AF_INET, SOCK_STREAM, 0);
    if (listening == -1)
    {
        std::cerr << "Error: Can't create socket!" << std::endl;
        return -1;
    }

    // Bind the socket to an IP address and port
    sockaddr_in hint;
    hint.sin_family = AF_INET;
    hint.sin_port = htons(12347);
    hint.sin_addr.s_addr = INADDR_ANY; // Use any IP address on the local machine

    if (bind(listening, (sockaddr *)&hint, sizeof(hint)) == -1)
    {
        std::cerr << "Error: Can't bind to IP/port!" << std::endl;
        return -1;
    }

    // Tell the socket to listen for incoming connections
    if (listen(listening, SOMAXCONN) == -1)
    {
        std::cerr << "Error: Can't listen!" << std::endl;
        return -1;
    }

    // Wait for a connection
    sockaddr_in client;
    socklen_t clientSize = sizeof(client);
    int clientSocket = accept(listening, (sockaddr *)&client, &clientSize);
    if (clientSocket == -1)
    {
        std::cerr << "Error: Can't accept client connection!" << std::endl;
        return -1;
    }

    char buf[4096];
    memset(buf, 0, 4096);

    // Receive message from frontend
    ssize_t bytesReceived = recv(clientSocket, buf, 4096, 0);
    if (bytesReceived == -1)
    {
        std::cerr << "Error in recv()" << std::endl;
        close(clientSocket);
        close(listening);
        return -1;
    }

    std::cout << "Received from frontend: " << std::string(buf, 0, bytesReceived) << std::endl;

    // Send response to the frontend
    std::string response = "Hello from backend!";
    send(clientSocket, response.c_str(), response.size() + 1, 0);

    // Close the socket
    close(clientSocket);
    close(listening);

    return 0;
}
