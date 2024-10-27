from flask import Blueprint, render_template, request, jsonify, session
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.file import  find_assignment_id, load_files, add_file
from app.models.assignment import  load_student_in_class, add_student_submit



file = Blueprint('file', __name__)

@file.route('/api/file@class=<class_id>-assignment=<assignment_id>', methods=['GET'])
def load_files_api(class_id, assignment_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        assignment = find_assignment_id(assignment_id)
        list_files = load_files(assignment_id)
        list_students = load_student_in_class(class_id)
        if user['school_id'] == assignment['school_id']:
            return jsonify(success = True, assignment = assignment, list_students = list_students, list_files = list_files)
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai")

@file.route('/api/upload_file@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['POST'])
def create_file_api(school_id, class_id, assignment_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if school_id == user['school_id']:
            print("Them file")
            student_id = request.form.get('student_id')
            submission_title = request.form.get('submissionTitle')
            storage_option = request.form.get('storageOption')
            submit_day = request.form.get('submitDay')
            file = request.files.get('file')
            if file:
                if add_file(school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option) and add_student_submit(school_id, assignment_id, student_id):     
                    return jsonify(success = True, message = "Dung")
                return jsonify(success = False, message = "sai") 
            return jsonify(success = False, message = "sai") 

        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 