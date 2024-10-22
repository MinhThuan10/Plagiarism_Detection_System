# models/assignment.py
from app.extensions import db


def load_assigment(class_id):
    assignments = db.assignments.find({"class_id": class_id})
    return assignments

def create_assignment(school_id, class_id, assignment_name, start_day, end_day):
    if db.assignments.find_one({'class_id': class_id, "assignment_name": assignment_name}):
        return False  
     
    db.assignments.insert_one({'school_id': school_id,
                        'class_id': class_id,
                         'assignment_name': assignment_name,
                         'start_day': start_day,
                         'end_day': end_day,
                         'student_ids': []
                         })
    return True


def update_assignment(school_id, class_id, assignment_id, assignment_name, start_day, end_day, student_ids):
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
                "student_ids": student_ids
            }
        }
    )
    if result.modified_count > 0:
        return True
    else:
        return False
    


def delete_assignment(school_id, assignment_id):
    assignment =  db.assignments.find_one({"_id": assignment_id})
    if not assignment:
        return False
    
    if assignment['school_id'] == school_id:
        db.assignments.delete_one({"_id": assignment_id})
        return True
    return False