# models/file.py
from app.extensions import db
from bson.objectid import ObjectId
from bson import Binary


def find_assignment_id(assignment_id):
    file_cursor = db.assignments.find_one({'assignment_id':assignment_id})
    if file_cursor:
        # Chuyển ObjectId sang chuỗi (nếu có)
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file_cursor.items()}
        return file_data
    return None


def load_files(assignment_id):
    files_cursor = db.files.find({"assignment_id": assignment_id})
    list_files = []
    for file in files_cursor:
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file.items()}
        file_data.pop('content_file', None)
        list_files.append(file_data)
    return list_files

def load_files_quick_submit(school_id):
    files_cursor = db.files.find({"school_id": school_id, "quick_submit": "yes"})
    list_files = []
    for file in files_cursor:
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file.items()}
        file_data.pop('content_file', None)
        list_files.append(file_data)
    return list_files



def add_file(school_id, class_id, assignment_id, title, author_id, submit_day, file, storage_option):
    if db.files.find_one({"assignment_id": assignment_id, "author_id": author_id}):
        return False
    
    max_file = db.files.find_one(sort=[('file_id', -1)])
    max_file = max_file['file_id'] if max_file else 0 
    db.files.insert_one({
        "school_id": school_id,
        "class_id": class_id,
        'assignment_id': assignment_id,
        "file_id": str(int(max_file) + 1),
        "title": title,
        "author_id": author_id,
        "submit_day": submit_day,
        "content_file": Binary(file.read()),
        "storage": storage_option,
        "type": "raw"
    })
    return True


def add_file_quick_submit(school_id, author_name, author_id, submission_title, submit_day, file, storage_option):
    max_file = db.files.find_one(sort=[('file_id', -1)])
    max_file = max_file['file_id'] if max_file else 0 
    db.files.insert_one({
        "school_id": school_id,
        "file_id": str(int(max_file) + 1),
        "title": submission_title,
        "author_id": author_id,
        "author_name": author_name,
        "submit_day": submit_day,
        "content_file": Binary(file.read()),
        "storage": storage_option,
        "type": "raw",
        "quick_submit": "yes"
    })
    return True
def delete_file_teacher(school_id, class_id, assignment_id, student_id):
    file =  db.files.find_one({"author_id": student_id})
    if not file:
        return False
    if school_id == file['school_id'] and class_id == file['class_id'] and assignment_id == file['assignment_id']:
        db.files.delete_many({"assignment_id": assignment_id,"author_id": student_id})
        return True
    return False
    
def delete_file_student(user_id, school_id, class_id, assignment_id, student_id):
    file =  db.files.find_one({"author_id": student_id})
    if not file:
        return False
    if user_id == file['author_id'] and school_id == file['school_id'] and class_id == file['class_id'] and assignment_id == file['assignment_id']:
        db.files.delete_many({"assignment_id": assignment_id,"author_id": student_id})
        return True
    return False



def delete_file_for_user(student_id):
    if db.files.find_one({"author_id": student_id}):
        return False
    db.files.delete_many({"author_id": student_id})
    return True
    