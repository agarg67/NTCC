from flask import render_template
from NTCC_Web_Project import app, socketio
from client2 import Client  # Ensure client2.py is properly referenced

# Initialize your Client instance globally if needed
client_instance = None

def get_client_instance():
    global client_instance
    if client_instance is None:
        client_instance = Client("localhost", 20001, 20002)  # Adjust as necessary
    return client_instance

@app.route('/')
def home():
    # Initialize client instance here or in another appropriate place
    get_client_instance()
    return render_template('index.html', title='Home')

@socketio.on('connect')
def handle_connect():
    print('Client connected to WebSocket.')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected from WebSocket.')

@socketio.on('send_command')
def handle_command(data):
    command = data['command']
    print(f"Received command from web: {command}")
    client_instance.handle_command(command)
    socketio.emit('server_response', {'data': f'Command processed: {command}'})