from flask import Blueprint, render_template, request, jsonify, session
from app.models.school import  load_school, create_school, update_school, delete_school
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db


school = Blueprint('school', __name__)

@school.route('/api/list_school', methods=['GET'])
def load_school_api():
    print("load list school")
    schools = load_school()
    list_school = []
    for school in schools:
        school_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in school.items()}
        list_school.append(school_data)
    return jsonify(success = True, list_school = list_school)


@school.route('/api/create_school', methods=['POST'])
def create_school_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Email or School name already exists")
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
            index_name = data.get('index_name')
            ip_cluster = data.get('ip_cluster')



            print(school_email)
            if create_school(school_name, school_email, school_key, index_name, ip_cluster):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Email or School name already exists")
        return jsonify(success = False, message = "Unauthorized access") 
        
    return jsonify(success = False, message = "User not logged in") 

@school.route('/api/update_school@school=<school_id>', methods=['PUT'])
def update_school_api(school_id):
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Re-enter data")

    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Manager":
            print("api update school")

            school_name = data.get('school_name')
            school_email = data.get('school_email')
            school_key = data.get('school_key')
            index_name = data.get('index_name')
            ip_cluster = data.get('ip_cluster')



            if update_school(school_id, school_name, school_email, school_key, index_name, ip_cluster):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Email or School name already exists")
        
        return jsonify(success = False, message = "Unauthorized access") 
        
    return jsonify(success = False, message = "User not logged in") 

@school.route('/api/delete_school@school=<school_id>', methods=['DELETE'])
def delete_school_api(school_id):
    print('Xoa school')
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Manager":
            print("api update school")

            if delete_school(school_id):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "School does not exist")
        return jsonify(success = False, message = "Unauthorized access") 
        
    return jsonify(success = False, message = "User not logged in") 