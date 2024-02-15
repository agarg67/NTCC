"""
This script runs the NTCC_Web_Project application using a development server.
"""

from os import environ
from NTCC_Web_Project import app
from flask import Flask
from multiprocessing import Process
import os
import shutil
import webbrowser
import threading

# Define the source and destination paths
current_dir = os.path.dirname(os.path.abspath(__file__))
source_path = os.path.join(current_dir, '..', '..', 'client.py')
destination_path = os.path.join(current_dir, 'client.py')

# Copy client.py to the current directory
shutil.copyfile(source_path, destination_path)

import client


def run_client():
    client.main() 

def open_browser():
      webbrowser.open_new('http://localhost:8080/connect')

if __name__ == '__main__':
    
    client_process = Process(target=run_client)
    client_process.start()

    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '8080'))
    except ValueError:
        PORT = 8080
    
    app.run(HOST, PORT, debug=True)
    
    # Use threading to prevent open_browser from blocking the application
    threading.Timer(1.25, open_browser).start()  # Adjust the delay as necessary