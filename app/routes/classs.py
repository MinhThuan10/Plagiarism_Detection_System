from flask import Blueprint, render_template, request, jsonify, session
from app.models.classs import  load_class_teacher, load_class_student, create_class, update_class, delete_school
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db

classs = Blueprint('class', __name__)

@classs.route('/classs', methods=['GET', 'POST'])
def load_class_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        school_id = user['school_id']
        user_id = str(user['_id'])

        if role == "Teacher":
            classs = load_class_teacher(school_id)
            list_classs = []
            for clas in classs:
                class_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in clas.items()}
                list_classs.append(class_data)
            return jsonify(success = True, list_classs = list_classs)
        elif role == "Student":
            classs = load_class_student(user_id)
            list_classs = []
            for clas in classs:
                class_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in clas.items()}

                list_classs.append(class_data)
            return jsonify(success = True, list_classs = list_classs)
        else:
            return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 


@classs.route('/api/create_class', methods=['POST'])
def create_class_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Nhập lại dữ liệu")
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            school_id = user['school_id']
            teacher_id = session['user_id']

            class_name = data.get('class_name')
            class_key = data.get('class_key')
            start_day = data.get('start_day')
            end_day = data.get('end_day')

            if create_class(school_id, class_name, class_key, teacher_id, start_day, end_day):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Tên lớp đã tồn tại")
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 

@classs.route('/api/update_class', methods=['POST'])
def update_class_api():

    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Nhập lại dữ liệu")

    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            print("api update class")
            school_id = user['school_id']

            class_id = data.get('class_id')
            class_name = data.get('class_name')
            class_key = data.get('class_key')
            start_day = data.get('start_day')
            end_day = data.get('end_day')
            student_ids = data.get('student_ids')

            if update_class(school_id, class_id, class_name, class_key, start_day, end_day, student_ids):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Không thể cập nhật lớp")
        
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 


@classs.route('/api/delete_class', methods=['POST'])
def delete_class_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            data = request.get_json()
            if not data:
                return jsonify(success = False, message = "Lớp không tồn tại")
            print("api delete class")
            school_id = user['school_id']


            class_id = data.get('class_id')

            if delete_school(school_id, class_id):
                return jsonify(success = True)
            else:
                return jsonify(success = False, message = "Không thể xóa lớp")
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 