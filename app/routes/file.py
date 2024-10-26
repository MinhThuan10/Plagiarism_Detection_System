from flask import Blueprint, render_template, request, jsonify, session
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.file import  find_assignment_id, load_student_submited, load_files


file = Blueprint('file', __name__)

@file.route('/api/file@class=<class_id>-assignment=<assignment_id>', methods=['GET'])
def load_files_api(class_id, assignment_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        assignment = find_assignment_id(assignment_id)
        list_files = load_files(assignment_id)
        list_students = load_student_submited(assignment_id)
        if user['school_id'] == assignment['school_id']:
            return jsonify(success = True, assignment = assignment, list_students = list_students, list_files = list_files)
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai")