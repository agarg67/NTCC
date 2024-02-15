"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template, request, redirect, url_for
from NTCC_Web_Project import app
from client import Client  # Ensure client.py is properly referenced

# Global client instance
client_instance = None

@app.route('/')
@app.route('/home')
def home():
    """Renders the home page."""
    return render_template(
        'index.html',
        title='Home Page',
        year=datetime.now().year,
    )

@app.route('/contact')
def contact():
    """Renders the contact page."""
    return render_template(
        'contact.html',
        title='Contact',
        year=datetime.now().year,
        message='Your contact page.'
    )

@app.route('/about')
def about():
    """Renders the about page."""
    return render_template(
        'about.html',
        title='About',
        year=datetime.now().year,
        message='Your application description page.'
    )

@app.route('/connect', methods=['POST'])
def connect():
    global client_instance
    centralServerIp = request.form['centralServerIp']
    centralServerPort = int(request.form['centralServerPort'])
    # Assuming client.py setup requires IP and two ports; adjust as necessary
    client_instance = Client(centralServerIp, centralServerPort, 9999)  # Example port; adjust accordingly
    # Add any required startup logic for client_instance here
    return redirect(url_for('home'))

@app.route('/disconnect', methods=['GET'])
def disconnect():
    global client_instance
    # Add your disconnection logic here
    client_instance = None
    return redirect(url_for('home'))
