from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Create the SQLAlchemy instance
db = SQLAlchemy()

def create_app():
    # Create the Flask app
    app = Flask(__name__)
    # Load the database config from Config in config.py
    app.config.from_object(Config)

    # Initialize the SQLAlchemy instance with the Flask app
    db.init_app(app)

    # get context to create the database
    with app.app_context():
        # Create the database if it doesn't exist
        db.create_all()
    return app
