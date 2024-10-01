from bson.objectid import ObjectId
from app.extensions import db

class User:
    def __init__(self, data):
        self.id = str(data.get('_id', ObjectId()))
        self.username = data.get('username')
        self.email = data.get('email')
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email
        }
    
    @staticmethod
    def get_all_users():
        users = db.users.find()
        return [User(user) for user in users]
    
    @staticmethod
    def create_user(username, email):
        user_id = db.users.insert_one({
            'username': username,
            'email': email
        }).inserted_id
        return str(user_id)
