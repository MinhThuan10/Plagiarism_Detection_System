# models/assignment.py
from app.extensions import db
from bson.objectid import ObjectId



def find_class_id(class_id):
    classs = db.classs.find_one({'class_id': class_id})
    if classs:
        # Chuyển ObjectId sang chuỗi (nếu có)
        class_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in classs.items()}
        return class_data
    return None


def load_assigment(class_id):
    assignments_cursor = db.assignments.find({"class_id": class_id})
    list_assignments = []
    for assignment in assignments_cursor:
        class_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in assignment.items()}
        list_assignments.append(class_data)
    return list_assignments
    

def load_student_in_class(class_id):
    list_class = find_class_id(class_id)
    list_student = []
    for student in list_class['student_ids']:
        print(student)
        student_cursor = db.users.find_one({'user_id': student[0]})
        
        if student_cursor:
            student_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in student_cursor.items()}
            list_student.append(student_data)
    return list_student


def create_assignment(school_id, class_id, assignment_name, start_day, end_day, create_day):
    if db.assignments.find_one({'class_id': class_id, "assignment_name": assignment_name}):
        return False  
    
    max_assignment = db.assignments.find_one(sort=[('assignment_id', -1)])
    max_assignment = max_assignment['assignment_id'] if max_assignment else 0 

    db.assignments.insert_one({'school_id': school_id,
                        'class_id': class_id,
                        'assignment_id': str(int(max_assignment) + 1),
                         'assignment_name': assignment_name,
                         'start_day': start_day,
                         'end_day': end_day,
                         'create_day': create_day,
                         'student_ids': []
                         })
    return True


def update_assignment(school_id, class_id, assignment_id, assignment_name, start_day, end_day):
    if  db.assignments.find_one({
            '$or': [
                {'class_id': class_id, 'assignment_name': assignment_name},
            ],
            'assignment_id': {'$ne': assignment_id} 
        }):
        return False  
    
    result =  db.assignments.update_one(
        {'school_id': school_id, 'assignment_id': assignment_id},
        {
            "$set": {
                "assignment_name": assignment_name,
                "start_day": start_day,
                "end_day": end_day,
            }
        }
    )
    if result.modified_count > 0:
        return True
    else:
        return False
    


def delete_assignment(school_id, class_id, assignment_id):
    assignment =  db.assignments.find_one({"assignment_id": assignment_id})
    if not assignment:
        return False
    
    if assignment['school_id'] == school_id and assignment['class_id'] == class_id:
        db.assignments.delete_one({"assignment_id": assignment_id})
        return True
    return False