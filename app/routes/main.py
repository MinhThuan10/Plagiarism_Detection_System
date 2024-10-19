from flask import Blueprint, render_template, session

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/home')
def home():
    if 'role' in session:
        if session['role'] == 'Teacher':
            return render_template('home_teacher.html')
        elif session['role'] == 'Student':
            return render_template('home_student.html')
        else:
            return "Unauthorized role", 403
    else:
        return "User not logged in", 401