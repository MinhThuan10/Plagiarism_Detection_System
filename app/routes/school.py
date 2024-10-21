from flask import Blueprint, render_template, request, jsonify, session
from app.models.school import  load_school, create_school, update_school, delete_school
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db


school = Blueprint('school', __name__)

@school.route('/school', methods=['GET', 'POST'])
def load_school_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Manager":
            schools = load_school()
            list_school = []
            for school in schools:
                school_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in school.items()}
                list_school.append(school_data)
            return jsonify(success = True, list_school = list_school)
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 

@school.route('/api/create_school', methods=['POST'])
def create_school_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")


    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Manager":
            print("api tao school")

            school_name = data.get('school_name')
            school_email = data.get('school_email')
            school_key = data.get('school_key')


            if create_school(school_name, school_email, school_key):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 

@school.route('/api/update_school', methods=['POST'])
def update_school_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Nhập lại dữ liệu")

    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Manager":
            print("api update school")

            school_id = data.get('school_id')
            school_name = data.get('school_name')
            school_email = data.get('school_email')
            school_key = data.get('school_key')


            if update_school(school_id, school_name, school_email, school_key):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Email hoặc tên Trường đã tồn tại")
        
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 

@school.route('/api/delete_school', methods=['POST'])
def delete_school_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Manager":
            data = request.get_json()
            if not data:
                return jsonify(success = False, message = "Trường không tồn tại")

            print("api update school")

            school_id = data.get('school_id')

            if delete_school(school_id):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Trường không tồn tại")
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 