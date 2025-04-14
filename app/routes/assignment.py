from flask import Blueprint, render_template, request, jsonify, session
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.assignment import  find_class_id, load_assigment, load_student_in_class, create_assignment, update_assignment, delete_assignment, load_file_in_class

assignment = Blueprint('assignment', __name__)



@assignment.route('/api/assignments@class=<class_id>', methods=['GET'])
def load_assignments_api(class_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if user['role'] == "Teacher":
            classs = find_class_id(class_id)
            assignments = load_assigment(class_id)
            list_students = load_student_in_class(class_id)
            if user['school_id'] == classs['school_id']:
                return jsonify(success = True, classs = classs, list_students = list_students, assignments = assignments)
            return jsonify(success = False, message = "School ID does not match") 
        if user['role'] == "Student":
            classs = find_class_id(class_id)
            assignments = load_file_in_class(class_id, user['user_id'])
            if user['school_id'] == classs['school_id']:
                return jsonify(success = True, classs = classs, assignments = assignments)
            return jsonify(success = False, message = "School ID does not match") 
    return jsonify(success = False, message = "User not logged in")



@assignment.route('/class=<class_id>/assignment=<assignment_id>')
def render_page_assignment(class_id, assignment_id):
    if 'user_id' not in session:
        return render_template('login.html')
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    clas = db.classs.find_one({'class_id': class_id})
    assignment = db.assignments.find_one({'assignment_id': assignment_id})

    if user and clas and assignment:
        if user['school_id'] == clas['school_id']:
            role = user['role']
            if role == 'Teacher':
                return render_template('assignment_detail_teacher.html', user = user)
            elif role == 'Student' and user['school_id'] in clas['student_ids']:
                return render_template('assignment_detail_student.html', user = user)
            else:
                return render_template('error.html')
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')
    

@assignment.route('/quick_submit')
def render_page_quick_submit():
    if 'user_id' not in session:
        return render_template('login.html')
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})

    if user:
        role = user['role']
        if role == 'Teacher':
            return render_template('quick_submit.html', user = user)
        else:
            return render_template('error.html')
    else:
        return render_template('error.html')

@assignment.route('/api/create_assignment@school=<school_id>-class=<class_id>', methods=['POST'])
def create_assignment_api(school_id, class_id):
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please re-enter the data")
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        role = user['role']
        if role == "Teacher":
            if school_id == user['school_id']:
                assignment_name = data.get('assignmentName')
                start_day = data.get('startDay')
                end_day = data.get('dueDay')
                create_day = data.get('createDay')

                if create_assignment(school_id, class_id, assignment_name, start_day, end_day, create_day):
                    return jsonify(success = True, message = "Successfully created a new assignment")
                else:
                    return jsonify(success = False, message = "Assignment name already exists")
            return jsonify(success = False, message = "Invalid school ID")
            
        return jsonify(success = False, message = "Unauthorized role") 
        
    return jsonify(success = False, message = "User not logged in")



@assignment.route('/api/update_assignment@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['PUT'])
def update_assignment_api(school_id, class_id, assignment_id):
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please re-enter the data")
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

                if update_assignment(school_id, class_id, assignment_id, assignment_name, start_day, end_day):
                    return jsonify(success = True, message = "Successfully updated the assignment")
                else:
                    return jsonify(success = False, message = "Update failed")
            return jsonify(success = False, message = "Invalid school ID")
            
        return jsonify(success = False, message = "Unauthorized role")
        
    return jsonify(success = False, message = "User not logged in")



@assignment.route('/api/delete_assignment@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['DELETE'])
def delete_assignment_api(school_id, class_id, assignment_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:

        role = user['role']
        if role == "Teacher":
            if school_id == user['school_id']:
                if delete_assignment(school_id, class_id, assignment_id):
                    return jsonify(success = True, message = "Successfully deleted the assignment")
                else:
                    return jsonify(success = False, message = "Failed to delete the assignment")
            return jsonify(success = False, message = "Invalid school ID") 
            
        return jsonify(success = False, message = "Unauthorized role") 
        
    return jsonify(success = False, message = "User not logged in")


@assignment.route('/mod/api/create_assignment', methods=['POST'])
def create_assignment_api_mod():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please re-enter the data")
    
    school_key = data.get('school_key')
    school_name = data.get('school_name')
    school = db.schools.find_one({'school_name': school_name})
    
    class_id = data.get('class_id')
    classs = db.classs.find_one({"class_id": class_id})

    if school_key == school['school_key'] and classs:
        assignment_name = data.get('assignmentName')
        start_day = data.get('startDay')
        end_day = data.get('dueDay')
        create_day = data.get('createDay')

        if create_assignment(school['school_id'], class_id, assignment_name, start_day, end_day, create_day):
            return jsonify(success = True, message = "Successfully created a new assignment")
        else:
            return jsonify(success = False, message = "Assignment name already exists")
            
    return jsonify(success = False, message = "Not valid")


@assignment.route('/mod/api/update_assignmen', methods=['PUT'])
def update_assignment_api_mod():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please re-enter the data")
    
    school_key = data.get('school_key')
    school_name = data.get('school_name')
    school = db.schools.find_one({'school_name': school_name})
    
    class_id = data.get('class_id')
    classs = db.classs.find_one({"class_id": class_id})

    if school_key == school['school_key'] and classs:
        assignment_name = data.get('assignmentName')
        start_day = data.get('startDay')
        end_day = data.get('dueDay')
        assignment_id = data.get('assignment_id')

        if update_assignment(school["school_id"], class_id, assignment_id, assignment_name, start_day, end_day):
            return jsonify(success = True, message = "Successfully updated the assignment")
        else:
            return jsonify(success = False, message = "Update failed")
            
    return jsonify(success = False, message = "Not valid")


@assignment.route('/mod/api/delete_assignment', methods=['DELETE'])
def delete_assignment_api_mod():
    data = request.get_json()
    if not data:
        return jsonify(success = False, message = "Please re-enter the data")
    
    school_key = data.get('school_key')
    school_name = data.get('school_name')
    school = db.schools.find_one({'school_name': school_name})
    
    class_id = data.get('class_id')
    classs = db.classs.find_one({"class_id": class_id})

    if school_key == school['school_key'] and classs:
        assignment_id = data.get('assignment_id')

        if delete_assignment(school["school_id"], class_id, assignment_id):
            return jsonify(success = True, message = "Successfully deleted the assignment")
        else:
            return jsonify(success = False, message = "Failed to delete the assignment")
            
    return jsonify(success = False, message = "Not valid")