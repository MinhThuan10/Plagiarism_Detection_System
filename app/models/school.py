# models/school.py
from app.extensions import db


def load_school():
    schools = db.schools.find({})
    return schools 

def create_school(name, email, key):
    if db.schools.find_one({'school_email': email}) or db.schools.find_one({'school_name': name}):
        return False   
    
    max_school = db.schools.find_one(sort=[('school_id', -1)])
    max_school = max_school['school_id'] if max_school else 0 
    
    db.schools.insert_one({'school_id':str(int(max_school) + 1),
                        'school_name': name, 
                         'school_email': email,
                         'school_key': key,
                         })
    return True


def update_school(school_id, name, email, key):
    if  db.schools.find_one({
            '$or': [
                {'school_email': email},
                {'school_name': name}
            ],
            'school_id': {'$ne': school_id} 
        }):
        return False  
    
    result = db.schools.update_one(
        {'school_id': school_id},
        {
            "$set": {
                "school_name": name,
                "school_email": email,
                "school_key": key
            }
        }
    )
    if result.modified_count > 0:
        return True
    else:
        return False

def delete_school(school_id):
    if not db.schools.find_one({"school_id": school_id}):
        return False
    db.schools.delete_one({"school_id":school_id})
    return True
    