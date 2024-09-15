from flask import Flask
from flask_pymongo import PyMongo
from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config.from_object('config.Config')

mongo = PyMongo(app)
es = Elasticsearch(app.config['ELASTICSEARCH_URL'])

from app import routes
