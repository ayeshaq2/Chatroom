#include <iostream>
#include <cpprest/http_listener.h>
#include <cpprest/json.h>

using namespace web;
using namespace web::http;
using namespace web::http::experimental::listener;

void set_cors(http_response& response) {
    // Add CORS headers to allow requests from any origin
    response.headers().add("Access-Control-Allow-Origin", "*");
    response.headers().add("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
    response.headers().add("Access-Control-Allow-Headers", "Content-Type");
}

void handle_post(http_request request) {
    // Extract JSON data from the request
    request.extract_json().then([=](json::value body) {
        double num1 = body["num1"].as_double();
        double num2 = body["num2"].as_double();
        
        // Perform addition
        double result = num1 + num2;
        
        // Create JSON response
        json::value response;
        response["result"] = result;
        
        // Send response with CORS headers
        http_response httpResponse(status_codes::OK);
        set_cors(httpResponse); // Set CORS headers for the response
        httpResponse.set_body(response);
        request.reply(httpResponse);
    }).wait();
}

int main() {
    http_listener listener("http://localhost:8080");
    listener.support(methods::POST, handle_post); // Add support for POST requests
    
    try {
        listener.open().then([&listener]() {
            std::cout << "Server is listening on http://localhost:8080\n";
        }).wait();
        
        std::cout << "Press ENTER to exit." << std::endl;
        std::string line;
        std::getline(std::cin, line);
    }
    catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }
    
    return 0;
}
