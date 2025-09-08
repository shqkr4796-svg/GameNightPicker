import os
import logging
from flask import Flask

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "life-sim-secret-key-2024")

# Import routes after app creation
from routes import *

