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
        "storage": storage_option
    })
    return True