#include <iostream>
#include <websocketpp/websocketpp/config/asio_no_tls.hpp>
#include <websocketpp/server.hpp>
#include <cctype>
#include <map>

using websocketpp::connection_hdl;
using websocketpp::server;
using websocketpp::lib::bind;
using websocketpp::lib::thread;
using websocketpp::lib::placeholders::_1;
using websocketpp::lib::placeholders::_2;

using namespace std::placeholders;

class WebSocketServer
{
public:
    using server = websocketpp::server<websocketpp::config::asio>;
    void run(uint16_t port)
    {
        // Set logging level to suppress WebSocket++ logs
        server_.set_access_channels(websocketpp::log::alevel::none);

        // Initialize Asio
        server_.init_asio();

        // Register handler functions
        server_.set_message_handler([this](websocketpp::connection_hdl hdl, server::message_ptr msg)
                                    { on_message(hdl, msg); });

        // server_.set_message_handler((&WebSocketServer::on_message, this, &server_, ::_1, ::_2));
        // server_.set_open_handler(&WebSocketServer::on_open);
        // server_.set_close_handler(&WebSocketServer::on_close);

        server_.set_open_handler([this](websocketpp::connection_hdl hdl)
                                 { on_open(hdl); });

        server_.set_close_handler([this](websocketpp::connection_hdl hdl)
                                  { on_close(hdl); });

        // Listen on specified port
        server_.listen(port);

        // Start the server accept loop
        server_.start_accept();

        // Start the ASIO io_service run loop
        server_.run();
    }

    std::string toMorseCode(char c)
    {
        // morse code mapping
        std::map<char, std::string> morseCodeMap = {
            {'A', ".-"}, {'B', "-..."}, {'C', "-.-."}, {'D', "-.."}, {'E', "."}, {'F', "..-."}, {'G', "--."}, {'H', "...."}, {'I', ".."}, {'J', ".---"}, {'K', "-.-"}, {'L', ".-.."}, {'M', "--"}, {'N', "-."}, {'O', "---"}, {'P', ".--."}, {'Q', "--.-"}, {'R', ".-."}, {'S', "..."}, {'T', "-"}, {'U', "..-"}, {'V', "...-"}, {'W', ".--"}, {'X', "-..-"}, {'Y', "-.--"}, {'Z', "--.."}, {'0', "-----"}, {'1', ".----"}, {'2', "..---"}, {'3', "...--"}, {'4', "....-"}, {'5', "....."}, {'6', "-...."}, {'7', "--..."}, {'8', "---.."}, {'9', "----."}, {' ', " "} // space character
        };

        c = toupper(c);

        // look for morse code to match the character

        auto it = morseCodeMap.find(c);
        if (it != morseCodeMap.end())
        {
            return it->second; // morse code found
        }
        else
        {
            return ""; // character not found, if there are ny punctuation marks
        }
    }

    // converting the recieved message to more code
    std::string messageToMorseCode(const std::string &message)
    {
        std::string morseCodeMessage;

        for (char c : message)
        {
            morseCodeMessage += toMorseCode(c) + " ";
        }

        return morseCodeMessage;
    }

    void on_message(connection_hdl hdl, server::message_ptr msg)
    {
        // get message:
        std::string rcvd = msg->get_payload();

        // convert:
        std::string morse_code = messageToMorseCode(rcvd);

        // Echo back the received message
        server_.send(hdl, morse_code, websocketpp::frame::opcode::text);
    }

    void on_open(connection_hdl hdl)
    {
        std::cout << "Client connected" << std::endl;
    }

    void on_close(connection_hdl hdl)
    {
        std::cout << "Client disconnected" << std::endl;
    }

private:
    server server_;
};

int main()
{
    WebSocketServer ws_server;
    ws_server.run(9002); // Run the server on port 9002

    return 0;
}
