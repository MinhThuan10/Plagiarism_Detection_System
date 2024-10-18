# app/__init__.py

from flask import Flask
from flask_pymongo import PyMongo
from config import Config  # Đảm bảo import đúng từ config.py
from .routes.main import main

mongo = PyMongo()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    mongo.init_app(app)

    app.register_blueprint(main)

    return app
