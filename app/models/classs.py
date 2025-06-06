# models/class.py
from app.extensions import db
from bson.objectid import ObjectId
from datetime import datetime
from pymongo import DESCENDING

def load_school_id(school_id):
    school = db.schools.find_one({'school_id': school_id})
    if school:
        # Chuyển ObjectId sang chuỗi (nếu có)
        school_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in school.items()}
        return school_data
    return None



def load_class_teacher(school_id):
    classs_cursor = db.classs.find({"school_id":school_id})
    list_classs = []
    for classs in classs_cursor:
        class_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in classs.items()}
        list_classs.append(class_data)
    return list_classs 

def load_class_student(student_id):
    classs_cursor = db.classs.find({"student_ids": {"$elemMatch": {"0": student_id}}})
    list_classs = []
    for classs in classs_cursor:
        teacher_cursor = db.users.find_one({"user_id": classs['teacher_id']})
        class_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in classs.items()}
        class_data['teacher_name'] = teacher_cursor['first_name'] + " " + teacher_cursor['last_name']
        list_classs.append(class_data)
    return list_classs

def create_class(school_id, class_name, class_key, teacher_id, start_day, end_day):
    if db.classs.find_one({'school_id': school_id, "class_name": class_name}):
        return False, None   
    
    pattern = f'^{school_id}_[0-9]+$'

    # max_class = db.classs.find_one(sort=[('class_id', -1)])
    # max_class = max_class['class_id'] if max_class else 0 
    
    max_class = db.classs.find_one(
        {'class_id': {'$regex': pattern}},
        sort=[(
            'class_id', DESCENDING
        )]
    )
    if max_class:
        max_class_id = int(max_class['class_id'].split('_')[1])
    else:
        max_class_id = 0
    class_id = str(school_id) + '_' + str(max_class_id + 1)
    db.classs.insert_one({'school_id': school_id,
                        'class_id': class_id,
                         'class_name': class_name,
                         'class_key': class_key,
                         'teacher_id': teacher_id,
                         'start_day': start_day,
                         'end_day': end_day,
                         'student_ids': []
                         })
    return True, class_id

def update_class(school_id, class_id, class_name, class_key, end_day):
    if  db.classs.find_one({
            '$or': [
                {'school_id': school_id, 'class_name': class_name},
            ],
            'class_id': {'$ne': class_id} 
        }):
        return False  
    
    result =  db.classs.update_one(
        {'school_id': school_id, 'class_id': class_id},
        {
            "$set": {
                "class_name": class_name,
                "class_key": class_key,
                "end_day": end_day
            }
        }
    )
    if result.modified_count > 0:
        return True
    else:
        return False

def add_user_to_class(user_id, class_id, class_key):
    classs =  db.classs.find_one({'class_id': class_id})
    if not classs:
        return False
        
    if class_key == classs['class_key']:
        day = datetime.now().strftime('%m/%d/%Y')
        classs['student_ids'].append([user_id, day])
        db.classs.update_one({'class_id': class_id}, {'$set': {'student_ids': classs['student_ids']}})
        return True

    return False


def add_user_to_class_mod(user_id, class_id):
    classs =  db.classs.find_one({'class_id': class_id})
    if not classs:
        return False
        
    day = datetime.now().strftime('%m/%d/%Y')
    classs['student_ids'].append([user_id, day])
    db.classs.update_one({'class_id': class_id}, {'$set': {'student_ids': classs['student_ids']}})
    return True



def delete_user_to_class(user_id, class_id):
    classs = db.classs.find_one({'class_id': class_id})
    if not classs:
        return False
    
    if any(student[0] == user_id for student in classs['student_ids']):
        classs['student_ids'] = [student for student in classs['student_ids'] if student[0] != user_id]
        db.classs.update_one({'class_id': class_id}, {'$set': {'student_ids': classs['student_ids']}})
        return True
    
    return False


def delete_class(school_id, class_id):
    classs =  db.classs.find_one({"class_id": class_id})
    if not classs:
        return False
    if classs['school_id'] == school_id:
        db.classs.delete_one({"class_id": class_id})
        db.assignments.delete_many({"class_id": class_id})
        db.files.delete_many({"class_id": class_id})
        db.sentences.delete_many({"class_id": class_id})

        return True
    return False


# Moodle

def create_class_mod(school_id, class_id, class_name, class_key, teacher_id, start_day, end_day):
    if db.classs.find_one({'school_id': school_id, "class_id": class_id}):
        return False  
    db.classs.insert_one({'school_id': school_id,
                        'class_id': class_id,
                         'class_name': class_name,
                         'class_key': class_key,
                         'teacher_id': teacher_id,
                         'start_day': start_day,
                         'end_day': end_day,
                         'student_ids': []
                         })
    return True