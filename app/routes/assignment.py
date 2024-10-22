from flask import Blueprint, render_template, request, jsonify, session
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.assignment import  load_assigment, create_assignment, update_assignment, delete_assignment

assignment = Blueprint('assignment', __name__)



@assignment.route('/api/assignments=<class_id>', methods=['GET'])
def load_assignments_api(class_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        school_id = user['school_id']
        assignments = load_assigment(class_id)
        list_assignments = []
        for assignment in assignments:
            assignment_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in assignment.items()}
            list_assignments.append(assignment_data)
        return jsonify(success = True, list_assignments = list_assignments)
        
    return jsonify(success = False, message = "sai") 