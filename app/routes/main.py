from flask import Blueprint, render_template, redirect, url_for, request, flash
from app.models.user import create_user, check_user  # Thay đổi import

main = Blueprint('main', __name__)

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if create_user(username, password):
            flash('Registration successful!')
            return redirect(url_for('main.login'))
        else:
            flash('Username already exists!')
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if check_user(username, password):
            return redirect(url_for('main.home'))  # Chuyển đến trang home
        else:
            flash('Invalid username or password!')
    return render_template('login.html')

@main.route('/')
def home():
    return render_template('home1.html')
