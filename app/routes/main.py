from flask import Blueprint, render_template, session
from app.extensions import db
from bson.objectid import ObjectId


main = Blueprint('main', __name__)

@main.route('/')
def index():

    return render_template('index.html')

@main.route('/home')
def home():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == 'Teacher':
            return render_template('home_teacher.html', user = user)
        elif role == 'Student':
            return render_template('home_student.html', user = user)
        elif role == 'Manager':
            return render_template('home_manager.html', user = user)
        else:
            return "Unauthorized role", 403
    else:
        return "User not logged in", 401
