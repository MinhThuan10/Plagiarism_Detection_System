# models/user.py

from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from app.extensions import db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson.objectid import ObjectId
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont


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



def create_user(firstname, lastname, email, password, role, avatar_base64,school_id ):

    if db.users.find_one({'email': email}):
        return False  # Tên người dùng đã tồn tại
    max_user = db.users.find_one(sort=[('user_id', -1)])
    max_user = max_user['user_id'] if max_user else 0

    hashed_password = generate_password_hash(password)
    db.users.insert_one({'user_id':str(int(max_user) + 1),
                        'first_name': firstname, 
                         'last_name': lastname,
                         'role': role,
                         'email': email,
                         'password': hashed_password,
                         'avatar': avatar_base64,
                         'school_id': school_id})
    return True

def check_user(email, password):
    user = db.users.find_one({'email': email})

    if user and check_password_hash(user['password'], password):
        return True, user
        
    return False, None

def check_user_change_passwd(email, password):
    user = db.users.find_one({'email': email})
    hashed_password = generate_password_hash(password)
    
    if user:
        db.users.update_one(
            { "email": email },
            { "$set": { "password": hashed_password } }
        )
        return True
        
    return False


def update_user(user_id, first_name, last_name, email, password, school_id):
    if  db.users.find_one({
            '$or': [
                {'email': email}
            ],
            '_id': {'$ne': ObjectId(user_id)}
        }):
        return False 
    
    user = db.users.find_one({'_id': ObjectId(user_id)})
    hashed_password = generate_password_hash(password)
    
    if user:
        result = db.users.update_one(
            { "_id": ObjectId(user_id) },
            { "$set": { "first_name": first_name,  "last_name": last_name, "email": email, "password": hashed_password, "school_id": school_id} }
        )
        if result.modified_count > 0:
            return True
        else:
            return False
        
    return False

# Hàm để gửi email
def send_verification_email(recipient_email, verification_code):
    sender_email = "thuanphanminh01@gmail.com"
    sender_password = "xjkp jpxq zwks iuty"
    
    subject = "Mã xác nhận"
    body = f"Mã xác nhận của bạn là: {verification_code}"

    message = f"Subject: {subject}\n\n{body}"
    print('tiến hành gửi email')
    # Tạo message với phần nội dung mã hóa UTF-8
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = recipient_email
    message['Subject'] = subject

    # Thêm nội dung email
    message.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False
    
def update_account(user_id, first_name, last_name, old_password, new_password):
    user = db.users.find_one({"user_id": user_id})
    if user:
        checkuser = check_user(user['email'], old_password)
        if checkuser[0] :
            first_name = first_name or user['first_name']
            last_name = last_name or user['last_name']
            hashed_password = generate_password_hash(new_password)
            db.users.update_one(
            { "user_id": user_id},
            { "$set": { "first_name": first_name,  "last_name": last_name, "password": hashed_password  } }
        )
            return True
        return False
    return False

def update_account_mod(user_id, first_name, last_name):
    user = db.users.find_one({"user_id": user_id})
    if user:
        first_name = first_name or user['first_name']
        last_name = last_name or user['last_name']
        db.users.update_one(
            { "user_id": user_id},
            { "$set": { "first_name": first_name,  "last_name": last_name} }
        )
        return True
    return False

def update_role_account_mod(user_id, role):
    user = db.users.find_one({"user_id": user_id})
    if user:
        if user['role'] == "Teacher" or "Manager":
            return True
        role = role or user['role']
        db.users.update_one(
            { "user_id": user_id},
            { "$set": { "role": role} }
        )
        return True
    return False

def delete_account_mod(user_id):
    user = db.users.find_one({"user_id": user_id})
    if user:
        db.users.delete_one({"user_id": user_id})
        return True
    return False