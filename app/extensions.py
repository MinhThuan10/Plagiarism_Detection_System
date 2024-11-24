from pymongo import MongoClient
from elasticsearch import Elasticsearch
from config import Config

# Khởi tạo MongoClient
mongo = MongoClient(Config.MONGO_URI)
db = mongo['mydatabase']

# Khởi tạo Elasticsearch
es = Elasticsearch(Config.ELASTICSEARCH_URL)

