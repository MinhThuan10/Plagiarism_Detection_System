from flask import Blueprint, render_template, request, jsonify, session
from app.models.user import create_user, check_user, send_verification_email, check_user_change_passwd, update_user, create_avatar_image, update_account, update_account_mod, delete_account_mod  # Thay đổi import
import random

from app.extensions import db
from bson.objectid import ObjectId



user = Blueprint('user', __name__)

@user.route('/signup')
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
        return jsonify(success=False, message='The verification code does not exist or has expired.'), 400
    
    if str(verificationCode) == str(stored_code):
        # Kiểm tra và tạo user
        # Tạo hình ảnh avatar từ chữ cái đầu tiên
        avatar_base64  = create_avatar_image(avatar_letter)

        if create_user(first_name, last_name, email, password, role, avatar_base64, school_id ):  
            return jsonify(success=True)
        else:
            print('looo')
            return jsonify(success=False, message='Email already exists, please enter another email') 
    
    else:
        print('looob')

        return jsonify(success=False, message='Incorrect confirmation code'), 400
    
    
    
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
        return jsonify(success=False, message='Invalid email'), 400
    
    # Tạo mã xác nhận
    verification_code = random.randint(100000, 999999)
    session['verification_code'] = verification_code
    # Gửi email
    if send_verification_email(email, verification_code):
        return jsonify(success=True, verification_code=verification_code)
    else:
        return jsonify(success=False, message='Unable to send confirmation email')
    
@user.route('/login')
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
        return jsonify(success=False, message='Incorrect account or password') 

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
        return jsonify(success=False, message='The verification code does not exist or has expired.'), 400
    
    if str(verificationCode) == str(stored_code):
        # Kiểm tra và tạo user
        if check_user_change_passwd(email, password):  
            return jsonify(success=True)
        else:
            print('looo')
            return jsonify(success=False, message='Email already exists, please enter another email') 
    
    else:
        print('looob')

        return jsonify(success=False, message='Incorrect confirmation code'), 400
    

@user.route('/api/update_user', methods=['PUST'])
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
            return jsonify(success=False, message='Email already exists, please enter another email') 
        

@user.route('/profile')
def account_profile():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if user['role'] == "Teacher":
            return render_template('account_teacher.html', user = user)
        if user['role'] == "Student":
            return render_template('account_student.html', user = user)
        return render_template('login.html')
    return render_template('login.html')


@user.route('/api/update_user', methods=["POST"])
def update_account_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        data = request.get_json()  # Nhận dữ liệu JSON từ client
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        if update_account(user["user_id"],first_name, last_name, old_password, new_password):
            return jsonify(success=True, message="Update success")
        return jsonify(success=False, message="wrong password")
    return jsonify(success=False, message="wrong password")      



# Moodle

@user.route('/mod/api/add_user', methods=['POST'])
def add_user():
    data = request.get_json()  # Nhận dữ liệu JSON từ client
    print('call api tạo user')
    print(data)

    
    first_name = data.get('firstname')
    last_name = data.get('lastname')
    role = "Student"
    email = data.get('email')
    password = "111111"
    school_key = data.get('school_key')

    school_name = data.get('school_name')
    school = db.schools.find_one({'school_name': school_name})
    school_id = school['school_id']


    avatar_letter = first_name[0].upper() if first_name else ""

    # Kiểm tra và tạo user
    # Tạo hình ảnh avatar từ chữ cái đầu tiên
    avatar_base64  = create_avatar_image(avatar_letter)
    if school_key == school['school_key']:
        if create_user(first_name, last_name, email, password, role, avatar_base64, school_id ):  
            return jsonify(success=True, message=True)
        else:
            return jsonify(success=False, message='Email already exists, please enter another email') 
    return jsonify(success=False, message='school key error') 



@user.route('/mod/api/update_user', methods=["PUT"])
def update_account_api_mod():
    data = request.get_json() 
    school_key = data.get('school_key')
    school_name = data.get('school_name')
    school = db.schools.find_one({'school_name': school_name})

    email = data.get('email')
    print(email)
    user = db.users.find_one({'email': email})
    if user and school_key == school['school_key']:
        first_name = data.get('firstname')
        last_name = data.get('lastname')
        if update_account_mod(user["user_id"],first_name, last_name):
            return jsonify(success=True, message="Update success")
        return jsonify(success=False, message="wrong password")
    return jsonify(success=False, message="wrong password") 


@user.route('/mod/api/delete_user', methods=["DELETE"])
def delete_account_api_mod():
    data = request.get_json() 
    school_key = data.get('school_key')
    school_name = data.get('school_name')
    school = db.schools.find_one({'school_name': school_name})

    email = data.get('email')
    print(email)

    user = db.users.find_one({'email': email})
    if user and school_key == school['school_key']:
        if delete_account_mod(user["user_id"]):
            return jsonify(success=True, message="Update success")
        return jsonify(success=False, message="wrong password")
    return jsonify(success=False, message="wrong password") 