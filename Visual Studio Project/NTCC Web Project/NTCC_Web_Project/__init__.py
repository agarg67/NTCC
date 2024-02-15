"""
The flask application package.
"""

import os
import sys

# Calculate the path to the root of the repository
current_dir = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.join(current_dir, '..', '..', '..')
sys.path.append(root_path)

import client
from flask import Flask
app = Flask(__name__)

import NTCC_Web_Project.views
