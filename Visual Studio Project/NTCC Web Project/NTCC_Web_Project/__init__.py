"""
The flask application package.
"""

import os
import shutil
from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

import NTCC_Web_Project.views

# Example SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message_from_client')
def handle_client_message(message):
    print('Received message from client:', message)
    # Here you can also include any logic to respond back to the client
    socketio.emit('message_from_server', {'data': 'Server received your message'})
