from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from app.models.user import create_user, check_user, send_verification_email  # Thay đổi import
import random

user = Blueprint('user', __name__)

@user.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


@user.route('/api/signup', methods=['POST'])
def signup_api():
    data = request.get_json()  # Nhận dữ liệu JSON từ client
    print('call api tạo user')
    print(data)

    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    password = data.get('password')
    verificationCode = data.get('verificationCode')
    stored_code = session.get('verification_code')


    if not stored_code:
        return jsonify(success=False, message='Mã xác nhận không tồn tại hoặc đã hết hạn'), 400
    
    if str(verificationCode) == str(stored_code):
        # Kiểm tra và tạo user
        if create_user(first_name, last_name, email, password):  
            return jsonify(success=True)
        else:
            print('looo')
            return jsonify(success=False, message='Email đã tồn tại, vui lòng nhập email khác') 
    
    else:
        print('looob')

        return jsonify(success=False, message='Mã xác nhận không chính xác'), 400
    
    
    

# API để gửi mã xác nhận
@user.route('/api/send_verification', methods=['POST'])
def send_verification():
    data = request.get_json()
    email = data.get('email')
    
    if not email:
        return jsonify(success=False, message='Email không hợp lệ'), 400
    
    # Tạo mã xác nhận
    verification_code = random.randint(100000, 999999)
    session['verification_code'] = verification_code
    # Gửi email
    if send_verification_email(email, verification_code):
        return jsonify(success=True, verification_code=verification_code)
    else:
        return jsonify(success=False, message='Không thể gửi email xác nhận')
    
@user.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')


@user.route('/api/login', methods=['POST'])
def login_api():
    data = request.get_json()  # Nhận dữ liệu JSON từ client

    email = data.get('email')
    password = data.get('password')


    if check_user(email, password):  
        return jsonify(success=True)
    else:
        print('looo')
        return jsonify(success=False, message='Tài khoản hoặc mật khẩu không chính xác') 
