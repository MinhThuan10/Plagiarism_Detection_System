from flask import Blueprint, render_template, request, jsonify, session
from app.models.user import create_user, check_user, send_verification_email, check_user_change_passwd, update_user  # Thay đổi import
import random
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

user = Blueprint('user', __name__)

@user.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')


# @user.route('/api/signup', methods=['POST'])
# def signup_api():
#     data = request.get_json()  # Nhận dữ liệu JSON từ client
#     print('call api tạo user')
#     print(data)

    
#     first_name = data.get('first_name')
#     last_name = data.get('last_name')
#     role = data.get('role')
#     email = data.get('email')
#     password = data.get('password')
#     verificationCode = data.get('verificationCode')
#     stored_code = session.get('verification_code')


#     if not stored_code:
#         return jsonify(success=False, message='Mã xác nhận không tồn tại hoặc đã hết hạn'), 400
    
#     if str(verificationCode) == str(stored_code):
#         # Kiểm tra và tạo user
#         if create_user(first_name, last_name, email, password, role):  
#             return jsonify(success=True)
#         else:
#             print('looo')
#             return jsonify(success=False, message='Email đã tồn tại, vui lòng nhập email khác') 
    
#     else:
#         print('looob')

#         return jsonify(success=False, message='Mã xác nhận không chính xác'), 400


def create_avatar_image(letter):
    # Tạo hình ảnh 100x100 với nền màu và chữ cái đầu
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))  # Nền màu xanh
    d = ImageDraw.Draw(img)

    # Chọn font và kích thước
    try:
        font = ImageFont.truetype("arial.ttf", 50)
    except IOError:
        font = ImageFont.load_default()

    # Tính toán vị trí vẽ chữ cái đầu tiên
    bbox = d.textbbox((0, 0), letter, font=font)
    text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    position = ((100 - text_width) // 2, (100 - text_height) // 2)

    # Vẽ chữ cái đầu tiên vào hình ảnh
    d.text(position, letter, fill=(255, 255, 255), font=font)  # Màu chữ trắng

    # Chuyển ảnh thành chuỗi base64
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return img_base64  # Trả về chuỗi base64 của ảnh


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

        if create_user(first_name, last_name, email, password, role, avatar_base64 ):  
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
    return "Logged out successfully"

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
        session['email'] = email
        session['role'] = checkuser[1]
        session['school_id'] = checkuser[2]
        return jsonify(success=True, role = checkuser[1], school_id =  checkuser[2] )
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
    data = request.get_json()  # Nhận dữ liệu JSON từ client
    print('call api update user')
    print(data)

    user_id = data.get('user_id')
    firstname = data.get('firstname')
    lastname = data.get('lastname')
    email = data.get('email')
    password = data.get('password')
    school_id = data.get('school_id')
    
    if update_user(user_id,firstname,lastname, email, password, school_id):  
            return jsonify(success=True)
    else:
        print('looo')
        return jsonify(success=False, message='Email đã tồn tại, vui lòng nhập email khác') 