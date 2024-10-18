# models/user.py

from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
import smtplib
from app.extensions import db
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def create_user(firstname, lastname, email, password):

    if db.users.find_one({'email': email}):
        return False  # Tên người dùng đã tồn tại
    hashed_password = generate_password_hash(password)
    db.users.insert_one({'firstname': firstname, 
                         'lastname': lastname,
                         'email': email,
                         'password': hashed_password})
    return True

def check_user(email, password):
    user = db.users.find_one({'email': email})
    
    if user and check_password_hash(user['password'], password):
        return True
        
    return False


# Hàm để gửi email
def send_verification_email(recipient_email, verification_code):
    sender_email = "thuanphanminh01@gmail.com"
    sender_password = "xjkp jpxq zwks iuty"
    
    subject = "Mã xác nhận đăng ký"
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