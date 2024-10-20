# models/user.py

from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from app.extensions import db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bson.objectid import ObjectId


def create_user(firstname, lastname, email, password, role, avatar_base64 ):

    if db.users.find_one({'email': email}):
        return False  # Tên người dùng đã tồn tại
    hashed_password = generate_password_hash(password)
    db.users.insert_one({'firs_tname': firstname, 
                         'last_name': lastname,
                         'role': role,
                         'email': email,
                         'password': hashed_password,
                         'avatar': avatar_base64 ,
                         'school_id': ""})
    return True

def check_user(email, password):
    user = db.users.find_one({'email': email})

    if user:
        role = user.get('role')  # Lấy giá trị của 'role'
        school_id = user.get('school_id')  # Lấy giá trị của 'school_id'
    else:
        role = None
        school_id = None

    if user and check_password_hash(user['password'], password):
        return True, role, school_id
        
    return False, role, school_id

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
        db.users.update_one(
            { "_id": ObjectId(user_id) },
            { "$set": { "first_name": first_name,  "last_name": last_name, "email": email, "password": hashed_password, "school_id": school_id} }
        )
        return True
        
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