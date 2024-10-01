from pymongo import MongoClient
from elasticsearch import Elasticsearch
import os

# Khởi tạo MongoClient
mongo = MongoClient('localhost', 27017)
db = mongo['mydatabase']  # Tên cơ sở dữ liệu

# Khởi tạo Elasticsearch
es = Elasticsearch("http://localhost:9200")
