from flask import Blueprint, render_template, request, jsonify, session, send_file
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.file import  find_assignment_id, load_files, add_file, add_file_quick_submit, delete_file_teacher, delete_file_student, delete_file_quick_submit, load_files_quick_submit, \
get_file_report , remove_source_school, add_source_school, remove_text_school, add_text_school, add_all_source_school, add_all_text_school, apply_filter
from app.models.assignment import  load_student_in_class, add_student_submit, delete_student_submit
from app.models.search_system.main import main, add_file_to_elasticsearch

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
                    result, file_id = add_file(user['role'], school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option)
                    if result and add_student_submit(school_id, assignment_id, student_id):
                        if storage_option == "standard_repository":
                            school_cursor = db.schools.find_one({"school_id": school_id})
                            add_file_to_elasticsearch(school_cursor["ip_cluster"], school_id, school_cursor["school_name"], file_id, school_cursor["index_name"], 'student_Data')
                        call_test_function_async(file_id)
                        return jsonify(success = True, message = "Dung")
                    return jsonify(success = False, message = "Đã bị trùng tên bài tập") 
                return jsonify(success = False, message = "Tải file lên không thành công") 
            if user['role'] == "Student":
                print("Them file")
                student_id = user['user_id']
                uploaded_file = request.files['file']
                submission_title = uploaded_file.filename
                storage_option = request.form.get('storageOption')
                submit_day = request.form.get('submitDay')
                file = request.files.get('file')
                if file:
                    result, file_id  = add_file(user['role'], school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option)
                    if result and add_student_submit(school_id, assignment_id, student_id):
                        if storage_option == "standard_repository":
                            school_cursor = db.schools.find_one({"school_id": school_id})
                            add_file_to_elasticsearch(school_cursor["ip_cluster"], school_id, school_cursor["school_name"], file_id, school_cursor["index_name"], 'student_Data')
                        call_test_function_async(file_id)
                        return jsonify(success = True, message = "Tải file lên thành công")
                    return jsonify(success = False, message = "Đã hết hạn nộp bài") 
                return jsonify(success = False, message = "Không thể tải file lên") 

        return jsonify(success = False, message = "Bạn không có quyền") 
        
    return jsonify(success = False, message = "Vui lòng đăng nhập lại") 

from threading import Thread
from flask import jsonify, Response
def call_test_function_async(file_id):
    # Khởi tạo và chạy luồng để gọi hàm main với file_id
    thread = Thread(target=main, args=(file_id))
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
                result, file_id  =  add_file_quick_submit(school_id, author_name, author_id, submission_title, submit_day, file, storage_option)
                if result:
                    if storage_option == "standard_repository":
                        school_cursor = db.schools.find_one({"school_id": school_id})
                        add_file_to_elasticsearch(school_cursor["ip_cluster"], school_id, school_cursor["school_name"], file_id, school_cursor["index_name"], 'student_Data')
                    call_test_function_async(file_id)
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
                "type": "raw"
            })
            
            if user['role'] == "Teacher" and pdf_record:
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

            if user['role'] == "Student" and pdf_record:
                if user['user_id'] == pdf_record['author_id']:
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
                return jsonify(success=False, message="Unauthorized access.")  # sai 1
            
            return jsonify(success=False, message="Unauthorized role.")  # sai 2
        
        return jsonify(success=False, message="Unauthorized school.")  # sai 3
    
    return jsonify(success=False, message="User not authenticated.")  # sai 4

@file.route('/api/download_pdf@file_id=<file_id>-type=<type>', methods=['GET'])
def download_pdf_quick_submit_raw(file_id, type):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        pdf_record = db.files.find_one({
            "file_id": file_id,
            "type": type
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
        if user['role'] == "Student" and pdf_record['author_id'] == user['user_id']:
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


@file.route('/api/load_file@file_id=<file_id>-type=<type>', methods=['GET'])
def load_file_checked(file_id, type):
    if 'user_id' not in session:
        return render_template('login.html')
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    file = db.files.find_one({'file_id': file_id, "type": type})
    if user and file:
        if file['school_id'] == user['school_id']: 
            pdf_bytes = file['content_file']    
            if user['role'] == "Teacher":
                return Response(pdf_bytes, mimetype='application/pdf')
            if user['role'] == "Student":
                return Response(pdf_bytes, mimetype='application/pdf')
            return jsonify(success=False, message="Unauthorized role.")  # sai 2
        return jsonify(success=False, message="Unauthorized school.")  # sai 3
    return jsonify(success=False, message="User not authenticated.")  # sai 4

@file.route('/report/file_id=<file_id>')
def get_file_report_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        file_data_checked = db.files.find_one({"file_id": file_id, "type": 'checked'})

        if user['role'] == "Teacher" and file_data_checked:
            if user['school_id'] == file_data_checked['school_id']:
                return render_template('report.html', file_id = file_id, user = user, user_id = user['user_id'])
            else:
                return render_template('error.html')
        if user['role'] == "Student" and file_data_checked:
            if user['school_id'] == file_data_checked['school_id'] and user['user_id'] == file_data_checked['author_id']:
                return render_template('report.html', file_id = file_id, user = user, user_id = user['user_id'])
            else:
                return render_template('error.html')
        return render_template('error.html')
    return render_template('error.html')
    
        
@file.route('/api/load_fileInfo_checked@file_id=<file_id>', methods=['GET'])
def load_fileInfo_checked(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    list_files, school_source_off, school_source_on, school_exclusion_source, school_exclusion_text = get_file_report(file_id)
    if user:
        return jsonify(success = True, message = "Dung", list_files = list_files, school_source_off = school_source_off, school_source_on = school_source_on, school_exclusion_source = school_exclusion_source, school_exclusion_text = school_exclusion_text )
    return jsonify(success = False, message = "sai") 


@file.route("/api/remove_source_school@file_id=<file_id>-school_id=<school_id>", methods=['POST'])
def remove_source_school_api(file_id, school_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        remove_source_school(file_id, school_id)
        return jsonify(success = True, message = "da cap nhat") 
    return jsonify(success = False, message = "sai") 

@file.route("/api/add_source_school@file_id=<file_id>-school_id=<school_id>", methods=['POST'])
def add_source_school_api(file_id, school_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_source_school(file_id, school_id)
        return jsonify(success = True, message = "da cap nhat") 
    return jsonify(success = False, message = "sai") 


@file.route("/api/remove_text_school@file_id=<file_id>-school_id=<school_id>-sentence=<sentence_index>", methods=['POST'])
def remove_source_school_text(file_id, school_id, sentence_index):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        remove_text_school(file_id, school_id, sentence_index)
        return jsonify(success = True, message = "da cap nhat") 
    return jsonify(success = False, message = "sai") 
    
@file.route("/api/add_text_school@file_id=<file_id>-sentence=<sentence_index>-<source_id>", methods=['POST'])
def add_source_school_text(file_id, sentence_index, source_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_text_school(file_id, sentence_index, source_id)
        return jsonify(success = True, message = "da cap nhat") 
    return jsonify(success = False, message = "sai") 


@file.route("/api/add_all_source_school@file_id=<file_id>", methods=['POST'])
def add_all_source_school_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_all_source_school(file_id)
        return jsonify(success = True, message = "da cap nhat") 
    return jsonify(success = False, message = "sai") 

@file.route("/api/add_all_text_school@file_id=<file_id>", methods=['POST'])
def add_all_text_school_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_all_text_school(file_id)
        return jsonify(success = True, message = "da cap nhat") 
    return jsonify(success = False, message = "sai") 

@file.route("/api/fillter@file_id=<file_id>", methods=['POST'])
def apply_filter_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        data = request.get_json() 
        studentData = data.get('studentData')
        internet = data.get('internet')
        paper = data.get('paper')
        references = data.get('references')
        curlybracket = data.get('curlybracket')
        minWord = data.get('minWord')
        minWordValue = data.get('minWordValue')
        apply_filter(file_id, studentData, internet, paper, references, curlybracket, minWord, minWordValue)
        return jsonify(success = True, message = "da cap nhat") 
    return jsonify(success = False, message = "sai") 