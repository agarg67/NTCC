"""
This script runs the NTCC_Web_Project application using a development server.
"""

from os import environ
from NTCC_Web_Project import app
import webbrowser
import threading

def open_browser():
      webbrowser.open_new('http://localhost:5555/connect')

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    # Use threading to prevent open_browser from blocking the application
    threading.Timer(1.25, open_browser).start()  # Adjust the delay as necessary
    app.run(HOST, PORT, debug=True)
