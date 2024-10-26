# app/routes/__init__.py
from flask import Blueprint

# Import các route
from .main import main
from .user import user  
from .school import school  
from .classs import classs  
from .assignment import assignment
from .file import file



# Tạo blueprint cho main
blueprints = [main, user, school, classs, assignment, file]

def register_blueprints(app):
    for bp in blueprints:
        app.register_blueprint(bp)