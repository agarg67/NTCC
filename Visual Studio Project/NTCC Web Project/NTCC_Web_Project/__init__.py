"""
The flask application package.
"""

import os
import shutil
from flask import Flask

app = Flask(__name__)

import NTCC_Web_Project.views
