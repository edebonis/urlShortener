from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        import routes
        import models  # Importar rutas y modelos aquí
        db.create_all()  # Crea las tablas en la base de datos
    return app
