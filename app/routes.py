from flask import render_template, request
from app import app, mongo, es

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    # Tìm kiếm trong Elasticsearch
    results = es.search(index="plagiarism", body={"query": {"match": {"content": query}}})
    return render_template('result.html', results=results)
