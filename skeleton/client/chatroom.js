var userName = '';
var webSocket;

function joinChatroom() {
    userName = document.getElementById('userName').value;
    // Connect to WebSocket server
    connectWebSocket();
    // Send request to server to join chatroom
    // Include userName in request data
    // Upon successful response, show chatroom interface
    document.getElementById('userInput').style.display = 'none';
    document.getElementById('chatroom').style.display = 'block';
}

function createChatroom() {
    userName = document.getElementById('userName').value;
    // Connect to WebSocket server
    connectWebSocket();
    // Send request to server to create new chatroom
    // Include userName in request data
    // Upon successful response, show chatroom interface
    document.getElementById('userInput').style.display = 'none';
    document.getElementById('chatroom').style.display = 'block';
}

function connectWebSocket() {
    // Create a new WebSocket connection
    webSocket = new WebSocket('ws://localhost:8080');
    // Setup WebSocket event listeners
    webSocket.onopen = function(event) {
        console.log('Connected to WebSocket server');
    };
    webSocket.onmessage = function(event) {
        receiveMessage(event.data);
    };
    webSocket.onerror = function(event) {
        console.error('WebSocket error:', event);
    };
}

function receiveMessage(message) {
    var messagesDiv = document.getElementById('messages');
    messagesDiv.innerHTML += `<p>${message}</p>`;
}

function sendMessage() {
    var messageInput = document.getElementById('messageInput');
    var message = messageInput.value;
    // Send message to server
    webSocket.send(JSON.stringify({ user: userName, message: message }));
    messageInput.value = ''; // Clear input field after sending
}
