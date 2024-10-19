# app/routes/__init__.py
from flask import Blueprint

# Import các route
from .main import main
from .user import user  
from .school import school  

# Tạo blueprint cho main
blueprints = [main, user, school]

def register_blueprints(app):
    for bp in blueprints:
        app.register_blueprint(bp)