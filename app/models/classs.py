# models/class.py
from app.extensions import db
from bson.objectid import ObjectId



def load_school_id(school_id):
    school_cursor = db.schools.find({'school_id':school_id})
    list_school = []
    for school in school_cursor:
        class_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in school.items()}
        list_school.append(class_data)
    return list_school


def load_class_teacher(school_id):
    classs = db.classs.find({"school_id":school_id})
    return classs 

def load_class_student(student_id):
    classs = db.classs.find({"student_ids": {"$in": [student_id]}})
    return classs


def create_class(school_id, class_name, class_key, teacher_id, start_day, end_day):
    if db.classs.find_one({'school_id': school_id, "class_name": class_name}):
        return False   
    
    max_class = db.classs.find_one(sort=[('class_id', -1)])
    max_class = max_class['class_id'] if max_class else 0 
    
    db.classs.insert_one({'school_id': school_id,
                        'class_id': str(int(max_class) + 1),
                         'class_name': class_name,
                         'class_key': class_key,
                         'teacher_id': teacher_id,
                         'start_day': start_day,
                         'end_day': end_day,
                         'student_ids': []
                         })
    return True

def update_class(school_id, class_id, class_name, class_key, start_day, end_day, student_ids):
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
                "start_day": start_day,
                "end_day": end_day,
                "student_ids": student_ids
            }
        }
    )
    if result.modified_count > 0:
        return True
    else:
        return False

def delete_school(school_id, class_id):
    classs =  db.classs.find_one({"class_id": class_id})
    if not classs:
        return False
    if classs['school_id'] == school_id:
        db.classs.delete_one({"class_id": class_id})
        return True
    return False