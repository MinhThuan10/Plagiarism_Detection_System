from pymongo import MongoClient
from elasticsearch import Elasticsearch
import os

# Khởi tạo MongoClient
mongo = MongoClient('localhost', 27017)
db = mongo['mydatabase']

# Khởi tạo Elasticsearch
es = Elasticsearch("http://localhost:9200")

