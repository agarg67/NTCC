"""
The flask application package.
"""

import sys

sys.path.append('../../..')

print(sys.path)

import client


from flask import Flask
app = Flask(__name__)

import NTCC_Web_Project.views
