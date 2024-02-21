"""
This script runs the NTCC_Web_Project application using a development server.
"""

from os import environ
from NTCC_Web_Project import app
from flask_socketio import SocketIO
from multiprocessing import Process
import os
import sys
import shutil
import webbrowser
import threading
import subprocess

# Initialize Flask-SocketIO
socketio = SocketIO(app)

import client2

def run_client_in_new_terminal():
    # Directly use PowerShell's Start-Process to run client2.py in a new window
    script_path = "client2.py"
    # Formulate the PowerShell command to open a new Command Prompt window running the script
    powershell_command = f'Start-Process -FilePath "cmd.exe" -ArgumentList "/k, python {script_path}"'
    # Execute the PowerShell command
    subprocess.Popen(["powershell", "-Command", powershell_command], shell=True)

def run_client():
    thread = threading.Thread(target=run_client_in_new_terminal)
    thread.start()

def open_browser():
    webbrowser.open_new('http://localhost:5555')

if __name__ == '__main__':
    
    run_client()

    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))  # Changed port to avoid conflict with default Flask port
    except ValueError:
        PORT = 5555

    # Use SocketIO to run the app instead of app.run
    threading.Timer(1.25, open_browser).start()  # Adjust the delay as necessary    
    socketio.run(app, host=HOST, port=PORT, debug=True)
