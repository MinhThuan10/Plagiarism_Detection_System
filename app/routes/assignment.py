from flask import Blueprint, render_template, request, jsonify, session
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.assignment import  find_class_id, load_assigment, create_assignment, update_assignment, delete_assignment

assignment = Blueprint('assignment', __name__)



@assignment.route('/api/assignments@class=<class_id>', methods=['GET'])
def load_assignments_api(class_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        classs = find_class_id(class_id)
        assignments = load_assigment(class_id)
        if user['school_id'] == classs['school_id']:
            return jsonify(success = True, classs = classs, assignments = assignments)
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai")


@assignment.route('/api/create_assignment@school=<school_id>-class=<class_id>', methods=['POST'])
def create_class_api(school_id, class_id):
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Nhập lại dữ liệu")
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            if school_id == user['school_id']:
                assignment_name = data.get('class_name')
                start_day = data.get('start_day')
                end_day = data.get('end_day')
                create_day = data.get('create_day')

                if create_assignment(school_id, class_id, assignment_name, start_day, end_day, create_day):
                    return jsonify(success = True,message = "Tạo lớp mới thành công")
                else:
                    return jsonify(success = False, message = "Tên lớp đã tồn tại")
            return jsonify(success = False, message = "sai") 
            
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 


@assignment.route('/api/update_assignment@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['PUT'])
def update_class_api(school_id, class_id, assignment_id):
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Nhập lại dữ liệu")
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            if school_id == user['school_id']:
                assignment_name = data.get('class_name')
                start_day = data.get('start_day')
                end_day = data.get('end_day')
                create_day = data.get('create_day')

                if update_assignment(school_id, class_id, assignment_id, assignment_name, start_day, end_day, create_day):
                    return jsonify(success = True,message = "Cập nhật lớp  thành công")
                else:
                    return jsonify(success = False, message = "Cập nhật không thành công")
            return jsonify(success = False, message = "sai") 
            
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 


@assignment.route('/api/update_assignment@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['DELETE'])
def delete_class_api(school_id, class_id, assignment_id):
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Nhập lại dữ liệu")
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            if school_id == user['school_id']:
                if delete_assignment(school_id, assignment_id):
                    return jsonify(success = True,message = "Xóa lớp thành công")
                else:
                    return jsonify(success = False, message = "Xóa lớp không thành công")
            return jsonify(success = False, message = "sai") 
            
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 