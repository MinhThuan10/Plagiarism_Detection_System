from dotenv import load_dotenv
import os
import ast  

load_dotenv()
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')
    CX = os.getenv('CX')
    CX2 = os.getenv('CX2')
    CX3 = os.getenv('CX3')
    CX4 = os.getenv('CX4')
    CX5 = os.getenv('CX5')
    CX6 = os.getenv('CX6')

    # Sử dụng ast.literal_eval để chuyển chuỗi thành list
    API_KEYS = ast.literal_eval(os.getenv('API_KEYS', '[]'))
    API_KEYS2 = ast.literal_eval(os.getenv('API_KEYS2', '[]'))
    API_KEYS3 = ast.literal_eval(os.getenv('API_KEYS3', '[]'))
    API_KEYS4 = ast.literal_eval(os.getenv('API_KEYS4', '[]'))
    API_KEYS5 = ast.literal_eval(os.getenv('API_KEYS5', '[]'))
    API_KEYS6 = ast.literal_eval(os.getenv('API_KEYS6', '[]'))


    
