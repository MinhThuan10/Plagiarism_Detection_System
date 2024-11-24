from dotenv import load_dotenv
import os

load_dotenv()
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    MONGO_URI = os.getenv('MONGO_URI')
    ELASTICSEARCH_URL = os.getenv('ELASTICSEARCH_URL')
    CX = os.getenv('CX')
    CX2 = os.getenv('CX2')
    CX3 = os.getenv('CX3')
    CX4 = os.getenv('CX4')
    API_KEYS = os.getenv('API_KEYS')
    API_KEYS2 = os.getenv('API_KEYS2')
    API_KEYS3 = os.getenv('API_KEYS3')
    API_KEYS4 = os.getenv('API_KEYS4')
