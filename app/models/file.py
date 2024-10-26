# models/file.py
from app.extensions import db
from bson.objectid import ObjectId


def find_assignment_id(assignment_id):
    file_cursor = db.assignments.find_one({'assignment_id':assignment_id})
    for file in file_cursor:
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file.items()}
        return file_data
    return []
    

def load_files(assignment_id):
    files_cursor = db.files.find({"assignment_id": assignment_id})
    list_files = []
    for file in files_cursor:
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file.items()}
        list_files.append(file_data)
    return list_files


def load_student_submited(assignment_id):
    assignment = find_assignment_id(assignment_id)
    list_student_submit = []
    for student_id in assignment['student_id_submited']:
        student_cursor = db.users.find_one({'user_id': student_id})
        
        for student in student_cursor:
            student_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in student.items()}
            list_student_submit.append(student_data)
    return list_student_submit
    