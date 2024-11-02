from flask import Blueprint, render_template, request, jsonify, session, send_file
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.file import  find_assignment_id, load_files, add_file, add_file_quick_submit, delete_file_teacher, delete_file_student, delete_file_quick_submit, load_files_quick_submit
from app.models.assignment import  load_student_in_class, add_student_submit, delete_student_submit
from app.models.search_system.main import main, run_concurrently

import base64
import io

file = Blueprint('file', __name__)

@file.route('/api/file@class=<class_id>-assignment=<assignment_id>', methods=['GET'])
def load_files_api(class_id, assignment_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        assignment = find_assignment_id(assignment_id)
        list_files = load_files(assignment_id)
        list_students = load_student_in_class(class_id)
        if user['school_id'] == assignment['school_id']:
            return jsonify(success = True, assignment = assignment, list_students = list_students, list_files = list_files)
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai")

@file.route('/api/quick_submit', methods=['GET'])
def load_files_quick_submit_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        school = db.schools.find_one({'school_id': user['school_id']})
        list_files = load_files_quick_submit(user['school_id'])
        return jsonify(success = True, list_files = list_files, school_name = school['school_name'], school_id = school['school_id'])
    return jsonify(success = False, message = "sai")


# @file.route('/api/upload_file@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['POST'])
# def create_file_api(school_id, class_id, assignment_id):
#     if 'user_id' not in session:
#         return render_template('login.html')
#     user = db.users.find_one({'_id': ObjectId(session['user_id'])})
#     if user:
#         if school_id == user['school_id']:
#             print("Them file")
#             student_id = request.form.get('student_id')
#             submission_title = request.form.get('submissionTitle')
#             storage_option = request.form.get('storageOption')
#             submit_day = request.form.get('submitDay')
#             file = request.files.get('file')
#             if file:
#                 if add_file(school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option) and add_student_submit(school_id, assignment_id, student_id):     
#                     return jsonify(success = True, message = "Dung")
#                 return jsonify(success = False, message = "sai") 
#             return jsonify(success = False, message = "sai") 

#         return jsonify(success = False, message = "sai") 
        
#     return jsonify(success = False, message = "sai") 


@file.route('/api/upload_file@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['POST'])
def create_file_api(school_id, class_id, assignment_id):
    
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if school_id == user['school_id']:
            if user['role'] == "Teacher":
                print("Them file")
                student_id = request.form.get('student_id')
                submission_title = request.form.get('submissionTitle')
                storage_option = request.form.get('storageOption')
                submit_day = request.form.get('submitDay')
                file = request.files.get('file')
                if file:
                    insert_file = add_file(school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option)
                    if insert_file[0] and add_student_submit(school_id, assignment_id, student_id):
                        call_test_function_async(insert_file[1])
                        print("Chạy luôn")
                        return jsonify(success = True, message = "Dung")
                    return jsonify(success = False, message = "sai") 
                return jsonify(success = False, message = "sai") 
            if user['role'] == "Student":
                print("Them file")
                student_id = user['user_id']
                uploaded_file = request.files['file']
                submission_title = uploaded_file.filename
                storage_option = request.form.get('storageOption')
                submit_day = request.form.get('submitDay')
                file = request.files.get('file')
                if file:
                    insert_file = add_file(school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option)
                    if insert_file[0] and add_student_submit(school_id, assignment_id, student_id):
                        call_test_function_async(insert_file[1])
                        print("Chạy luôn")
                        return jsonify(success = True, message = "Dung")
                    return jsonify(success = False, message = "sai") 
                return jsonify(success = False, message = "sai") 

        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 

from threading import Thread
from flask import jsonify
def call_test_function_async(file_id):
    # Khởi tạo và chạy luồng để gọi hàm main với file_id
    thread = Thread(target=run_concurrently, args=(file_id))
    thread.start()


@file.route('/api/upload_file_quick_submit@school=<school_id>', methods=['POST'])
def create_file_quick_submit_api(school_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if school_id == user['school_id']:
            print("Them file")
            author_name = request.form.get('author_name')
            submission_title = request.form.get('submissionTitle')
            storage_option = request.form.get('storageOption')
            submit_day = request.form.get('submitDay')
            file = request.files.get('file')
            author_id = user['user_id']
            if file:
                insert_file =  add_file_quick_submit(school_id, author_name, author_id, submission_title, submit_day, file, storage_option)
                if insert_file[0]: 
                    call_test_function_async(insert_file[1])
                    print("Chạy luôn")
                    return jsonify(success = True, message = "Dung")
                return jsonify(success = False, message = "sai") 
            return jsonify(success = False, message = "sai") 

        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 


@file.route('/api/delete_file@school=<school_id>-class=<class_id>-assignment=<assignment_id>-student=<student_id>', methods=['DELETE'])
def delete_file_api(school_id, class_id, assignment_id, student_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if school_id == user['school_id']:
            if user['role'] == "Teacher":
                print("Xoa file")
                if delete_file_teacher(school_id, class_id, assignment_id, student_id) and delete_student_submit(school_id, assignment_id, student_id):
                    return jsonify(success = True, message = "Dung")
                return jsonify(success = False, message = "sai") 
            if user['role'] == "Student":
                if delete_file_student(user['user_id'], school_id, class_id, assignment_id, student_id) and delete_student_submit(school_id, assignment_id, student_id):
                    return jsonify(success = True, message = "Dung")
                return jsonify(success = False, message = "sai") 
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 


@file.route('/api/delete_file@file_id=<file_id>', methods=['DELETE'])
def delete_file_quick_submit_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if user['role'] == "Teacher":
            print("Xoa file")
            if delete_file_quick_submit(user['school_id'], file_id):
                return jsonify(success = True, message = "Dung")
            return jsonify(success = False, message = "sai") 
        return jsonify(success = False, message = "sai") 
        
    return jsonify(success = False, message = "sai") 

@file.route('/api/download_pdf@school=<school_id>-class=<class_id>-assignment=<assignment_id>-student=<student_id>', methods=['GET'])
def download_pdf_raw(school_id, class_id, assignment_id, student_id):
    if 'user_id' not in session:
        return render_template('login.html')
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if school_id == user['school_id']:
            pdf_record = db.files.find_one({
                'class_id': class_id, 
                'assignment_id': assignment_id, 
                "author_id": student_id, 
                "type": "checked"
            })
            
            if user['role'] == "Teacher" and pdf_record:
                pdf_bytes = bytes(pdf_record['content'])
                pdf_io = io.BytesIO(pdf_bytes)
                file_name = pdf_record['title']
                file_name += '.pdf'
                return send_file(
                    pdf_io, 
                    download_name=file_name, 
                    as_attachment=True, 
                    mimetype='application/pdf'
                )

            if user['role'] == "Student" and pdf_record:
                if user['user_id'] == pdf_record['author_id']:
                    pdf_bytes = bytes(pdf_record['content'])
                    pdf_io = io.BytesIO(pdf_bytes)
                    file_name = pdf_record['title']
                    file_name += '.pdf'
                    return send_file(
                        pdf_io, 
                        download_name=file_name,
                        as_attachment=True, 
                        mimetype='application/pdf'
                    )
                return jsonify(success=False, message="Unauthorized access.")  # sai 1
            
            return jsonify(success=False, message="Unauthorized role.")  # sai 2
        
        return jsonify(success=False, message="Unauthorized school.")  # sai 3
    
    return jsonify(success=False, message="User not authenticated.")  # sai 4



@file.route('/api/download_pdf@file_id=<file_id>', methods=['GET'])
def download_pdf_quick_submit_raw(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        pdf_record = db.files.find_one({
            "file_id": file_id,
            "type": "raw"
        })
        if user['role'] == "Teacher" and pdf_record['school_id'] == user['school_id']:
            pdf_bytes = bytes(pdf_record['content_file'])
            pdf_io = io.BytesIO(pdf_bytes)
            file_name = pdf_record['title']
            file_name += '.pdf'
            return send_file(
                pdf_io, 
                download_name=file_name, 
                as_attachment=True, 
                mimetype='application/pdf'
            )
            
        return jsonify(success=False, message="Unauthorized school.")  # sai 3
    return jsonify(success=False, message="User not authenticated.")  # sai 4



