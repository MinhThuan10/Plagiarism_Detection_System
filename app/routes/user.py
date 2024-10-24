from flask import Blueprint, render_template, request, jsonify, session
from app.models.user import create_user, check_user, send_verification_email, check_user_change_passwd, update_user, create_avatar_image  # Thay đổi import
import random

from app.extensions import db
from bson.objectid import ObjectId



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
    role = data.get('role')
    email = data.get('email')
    password = data.get('password')
    school_id = data.get('school_id')

    verificationCode = data.get('verificationCode')
    stored_code = session.get('verification_code')
    # Lấy chữ cái đầu tiên của first_name làm avatar
    avatar_letter = first_name[0].upper() if first_name else ""

    if not stored_code:
        return jsonify(success=False, message='Mã xác nhận không tồn tại hoặc đã hết hạn'), 400
    
    if str(verificationCode) == str(stored_code):
        # Kiểm tra và tạo user
        # Tạo hình ảnh avatar từ chữ cái đầu tiên
        avatar_base64  = create_avatar_image(avatar_letter)

        if create_user(first_name, last_name, email, password, role, avatar_base64, school_id ):  
            return jsonify(success=True)
        else:
            print('looo')
            return jsonify(success=False, message='Email đã tồn tại, vui lòng nhập email khác') 
    
    else:
        print('looob')

        return jsonify(success=False, message='Mã xác nhận không chính xác'), 400
    
    
    
@user.route('/logout')
def logout():
    session.clear()  # Xóa toàn bộ dữ liệu trong session
    return render_template('index.html')

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

    checkuser = check_user(email, password)
    if checkuser[0]:  
        session['user_id'] = str(checkuser[1]['_id'])
        return jsonify(success=True, role = checkuser[1].get('role'), school_id =  checkuser[1].get('school_id'))
    else:
        print('looo')
        return jsonify(success=False, message='Tài khoản hoặc mật khẩu không chính xác') 

@user.route('/api/forgot_password', methods=['POST'])
def forgot_password():
    data = request.get_json()  # Nhận dữ liệu JSON từ client
    print('call api đổi mật khẩu')
    print(data)

    
    email = data.get('email')
    password = data.get('password')
    verificationCode = data.get('verificationCode')
    stored_code = session.get('verification_code')


    if not stored_code:
        return jsonify(success=False, message='Mã xác nhận không tồn tại hoặc đã hết hạn'), 400
    
    if str(verificationCode) == str(stored_code):
        # Kiểm tra và tạo user
        if check_user_change_passwd(email, password):  
            return jsonify(success=True)
        else:
            print('looo')
            return jsonify(success=False, message='Email đã tồn tại, vui lòng nhập email khác') 
    
    else:
        print('looob')

        return jsonify(success=False, message='Mã xác nhận không chính xác'), 400
    

@user.route('/api/update_user', methods=['POST'])
def update_user_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        
        print('call api update user')

        user_id = user['user_id']
        firstname = user['firstname']
        lastname = user['lastname']
        email = user['email']
        password = user['password']
        school_id = user['school_id']
        
        if update_user(user_id,firstname,lastname, email, password, school_id):  
                return jsonify(success=True)
        else:
            print('looo')
            return jsonify(success=False, message='Email đã tồn tại, vui lòng nhập email khác') 