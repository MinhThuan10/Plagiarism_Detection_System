from flask import Flask
from .config import Config
from .extensions import mongo, es
from .routes.main import main as main_blueprint

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Khởi tạo các extension
    # Đối với PyMongo và Elasticsearch, không cần gọi init_app
    # Vì chúng được khởi tạo trực tiếp trong extensions.py

    # Đăng ký blueprint
    app.register_blueprint(main_blueprint)

    return app
