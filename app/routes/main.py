from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from app.models.user import User
from app.extensions import es

main = Blueprint('main', __name__)

@main.route('/')
def index():
    # Lấy tất cả người dùng từ MongoDB
    users = User.get_all_users()

    # Tìm kiếm trong Elasticsearch
    query = request.args.get('q')
    es_results = []
    if query:
        es_response = es.search(
            index="users",
            body={
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["username", "email"]
                    }
                }
            }
        )
        es_results = es_response['hits']['hits']

    return render_template('index.html', users=users, es_results=es_results, query=query)

