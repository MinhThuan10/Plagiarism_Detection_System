from flask import Blueprint, render_template, request, jsonify, session
from app.models.classs import  load_class_teacher, load_class_student, create_class, update_class, delete_class, load_school_id, add_user_to_class, delete_user_to_class
from app.models.file import delete_file_for_user
from app.models.assignment import delete_student_in_assignments
from datetime import datetime
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db

classs = Blueprint('class', __name__)

@classs.route('/api/school', methods=['GET'])
def load_class_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        school_id = user['school_id']

        school_data = load_school_id(school_id)
        if role == "Teacher":
            if school_id == user['school_id']:
                classs = load_class_teacher(school_id)
                return jsonify(success = True, school_data = school_data, classs = classs)
            return jsonify(success = False, message = "School ID does not match") 

        elif role == "Student":
            if school_id == user['school_id']:
                classs = load_class_student(user['user_id'])
                return jsonify(success = True, school_data = school_data, classs = classs)
            return jsonify(success = False, message = "School ID does not match") 
            
        else:
            return jsonify(success = False, message = "Invalid role") 
        
    return jsonify(success = False, message = "User not logged in") 



@classs.route('/class=<class_id>')
def render_page_class(class_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    clas = db.classs.find_one({'class_id': class_id})
    if user and clas:
        if user['school_id'] == clas['school_id']:
            role = user['role']
            if role == 'Teacher':

                return render_template('assignment_teacher.html', user = user)
            elif role == 'Student' and any(user['user_id'] in student for student in clas['student_ids']):
                return render_template('assignment_student.html', user = user, user_id = user['user_id'])
            else:
                return render_template('error.html')
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@classs.route('/api/create_class@school=<school_id>', methods=['POST'])
def create_class_api(school_id):
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please enter valid data")
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            if school_id == user['school_id']:
                print("Creating class")
                teacher_id = user['user_id']
                class_name = data.get('class_name')
                class_key = data.get('class_key')
                start_day = data.get('start_day')
                end_day = data.get('end_day')
                
                created_class = create_class(school_id, class_name, class_key, teacher_id, start_day, end_day)

                if created_class[0]:
                    return jsonify(success = True, class_id = created_class[1], message = "Class created successfully")
                else:
                    return jsonify(success = False, message = "Class name already exists")
            return jsonify(success = False, message = "School ID does not match") 
            
        return jsonify(success = False, message = "Invalid role") 
        
    return jsonify(success = False, message = "User not logged in")  

@classs.route('/api/update_class@school=<school_id>-class=<class_id>', methods=['PUT'])
def update_class_api(school_id, class_id):
    print("Update class")
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please enter valid data")

    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            print("API update class")
            if school_id == user['school_id']:

                class_name = data.get('class_name')
                class_key = data.get('class_key')
                end_day = data.get('end_day')

                if update_class(school_id, class_id, class_name, class_key, end_day):
                    return jsonify(success = True, message = "Class updated successfully")
                else:
                    return jsonify(success = False, message = "Unable to update class")
            return jsonify(success = False, message = "School ID does not match")    
        return jsonify(success = False, message = "Invalid role") 
        
    return jsonify(success = False, message = "User not logged in") 


@classs.route('/api/delete_class@school=<school_id>-class=<class_id>', methods=['DELETE'])
def delete_class_api(school_id, class_id):
    print("Delete class")
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            print("API delete class")
            if school_id == user['school_id']:

                if delete_class(school_id, class_id):
                    return jsonify(success = True, message = "Class deleted successfully")
                else:
                    return jsonify(success = False, message = "Unable to delete class")
            return jsonify(success = False, message = "School ID does not match") 
        return jsonify(success = False, message = "Invalid role") 
        
    return jsonify(success = False, message = "User not logged in") 


@classs.route('/api/add_user_to_class', methods=['PUT'])
def add_user_to_class_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please enter valid data")

    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Student":
            class_id = data.get('class_id')
            class_key = data.get('class_key')

            classs = db.classs.find_one({'class_id': class_id})
            if classs:
                end_day = datetime.strptime(classs['end_day'], "%m/%d/%Y")
                if classs['school_id'] == user['school_id'] and datetime.now() < end_day:
                    if add_user_to_class(user['user_id'], class_id, class_key):
                        return jsonify(success = True, message = "Successfully joined the class")
                    else:
                        return jsonify(success = False, message = "Wrong enrollment key")
                    
                return jsonify(success = False, message = "The class has ended and you can no longer join") 
            return jsonify(success = False, message = "Class does not exist") 
        return jsonify(success = False, message = "You do not have permission to join this class")      
    return jsonify(success = False, message = "Please log in again") 


@classs.route('/api/delete_user_to_class', methods=['PUT'])
def delete_user_to_class_api():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please enter valid data")

    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        class_id = data.get('class_id')
        student_id = data.get('student_id')
        if role == "Teacher":

            classs = db.classs.find_one({'class_id': class_id})
            if classs:
                if classs['school_id'] == user['school_id']:
                    if delete_user_to_class(student_id, class_id) and delete_file_for_user(student_id, class_id) and delete_student_in_assignments(student_id, class_id):
                        return jsonify(success = True, message = "Class updated successfully")
                    else:
                        return jsonify(success = False, message = "Unable to update class")
                    
                return jsonify(success = False, message = "School ID does not match") 
            return jsonify(success = False, message = "Class does not exist") 
        if role == "Student":
            classs = db.classs.find_one({'class_id': class_id})
            if classs:
                if classs['school_id'] == user['school_id']:
                    if delete_user_to_class(user['user_id'], class_id) and delete_file_for_user(user['user_id'], class_id) and delete_student_in_assignments(student_id, class_id):
                        return jsonify(success = True, message = "Successfully updated class")
                    else:
                        return jsonify(success = False, message = "Unable to update class")
                    
                return jsonify(success = False, message = "School ID does not match") 
            return jsonify(success = False, message = "Class does not exist") 
        return jsonify(success = False, message = "Invalid role")      
    return jsonify(success = False, message = "User not logged in")
