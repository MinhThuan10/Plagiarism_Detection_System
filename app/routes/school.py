from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from app.models.school import  load_school, create_school, update_school, delete_school
from bson import ObjectId
school = Blueprint('school', __name__)

@school.route('/school', methods=['GET', 'POST'])
def school_page():
    schools = load_school()
    list_school = []
    for school in schools:
        school_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in school.items() if key != '_id'}
        list_school.append(school_data)
    print(list_school)
    return jsonify(success = True, list_school = list_school)

@school.route('/api/create_school', methods=['POST'])
def create_school_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")

    print("api tao school")

    school_name = data.get('school_name')
    school_email = data.get('school_email')
    school_key = data.get('school_key')


    if create_school(school_name, school_email, school_key):
        return jsonify(success = True)
    else:
        return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")
        

@school.route('/api/update_school', methods=['POST'])
def update_school_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")

    print("api update school")

    school_id = data.get('school_id')
    school_name = data.get('school_name')
    school_email = data.get('school_email')
    school_key = data.get('school_key')


    if update_school(school_id, school_name, school_email, school_key):
        return jsonify(success = True)
    else:
        return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")
        

@school.route('/api/delete_school', methods=['POST'])
def delete_school_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")

    print("api update school")

    school_id = data.get('school_id')

    if delete_school(school_id):
        return jsonify(success = True)
    else:
        return jsonify(success = False, message = "Trường không tồn tại")
        