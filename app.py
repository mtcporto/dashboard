import os
from flask import Flask

# define base directory as parent of dashboard dir
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
app = Flask(__name__)
app.config['BASE_DIR'] = BASE_DIR

# register dashboard blueprint
from controllers.dashboard import dashboard_bp
app.register_blueprint(dashboard_bp)

# routes moved to controllers/dashboard.py
