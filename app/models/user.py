# models/user.py

from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db

def create_user(username, password):
    if db.users.find_one({'username': username}):
        return False  # Tên người dùng đã tồn tại
    hashed_password = generate_password_hash(password)
    db.users.insert_one({'username': username, 'password': hashed_password})
    return True

def check_user(username, password):
    user = db.users.find_one({'username': username})
    if user and check_password_hash(user['password'], password):
        return True
    return False
