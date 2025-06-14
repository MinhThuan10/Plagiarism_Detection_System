from flask import Blueprint, render_template, request, jsonify, session, send_file
from bson import ObjectId
from bson.objectid import ObjectId
from app.extensions import db
from app.models.file import  find_assignment_id, load_files, add_file, add_file_quick_submit, delete_file_teacher, delete_file_student, delete_file_quick_submit, load_files_quick_submit, \
get_file_report , remove_source_school, add_source_school, remove_text_school, add_text_school, add_all_source_school, add_all_text_school, apply_filter, download_source
from app.models.assignment import  load_student_in_class, add_student_submit, delete_student_submit
from app.models.search_system.main import main
from app.models.search_system.models import import_file_to_elastic, update_file_view_all
from app.models.search_system.highlight import highlight_school
from bson import Binary
import io
import requests
import base64
import os

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
        return jsonify(success=False, message="Invalid school ID for the assignment.")
    
    return jsonify(success=False, message="User authentication failed.")

@file.route('/api/quick_submit', methods=['GET'])
def load_files_quick_submit_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        school = db.schools.find_one({'school_id': user['school_id']})
        list_files = load_files_quick_submit(user['school_id'])
        return jsonify(success = True, list_files = list_files, school_name = school['school_name'], school_id = school['school_id'])
    return jsonify(success=False, message="School information missing.")



@file.route('/api/upload_file@school=<school_id>-class=<class_id>-assignment=<assignment_id>', methods=['POST'])
def create_file_api(school_id, class_id, assignment_id):
    
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if school_id == user['school_id']:
            if user['role'] == "Teacher":
                student_id = request.form.get('student_id')
                submission_title = request.form.get('submissionTitle')
                storage_option = request.form.get('storageOption')
                submit_day = request.form.get('submitDay')
                file = request.files.get('file')
                if file:
                    result, file_id = add_file(user['role'], school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option)
                    if result and add_student_submit(school_id, assignment_id, student_id):
                        call_test_function_async(file_id, storage_option, school_id)
                        return jsonify(success = True, message = "File upload successful")
                    return jsonify(success = False, message = "The assignment name is duplicated.") 
                return jsonify(success = False, message = "File upload failed") 
            if user['role'] == "Student":
                student_id = user['user_id']
                uploaded_file = request.files['file']
                submission_title = uploaded_file.filename
                storage_option = request.form.get('storageOption')
                submit_day = request.form.get('submitDay')
                file = request.files.get('file')
                if file:
                    result, file_id  = add_file(user['role'], school_id, class_id, assignment_id, submission_title, student_id, submit_day, file, storage_option)
                    if result and add_student_submit(school_id, assignment_id, student_id):
                        call_test_function_async(file_id, storage_option, school_id)
                        return jsonify(success = True, message = "File upload successful")
                    return jsonify(success = False, message = "Submission deadline has passed.") 
                return jsonify(success = False, message = "Unable to upload file") 

        return jsonify(success = False, message = "You do not have the right") 
        
    return jsonify(success = False, message = "Please log in again") 

from threading import Thread
from flask import jsonify, Response
def call_test_function_async(file_id, storage_option, school_id):
    # Khởi tạo và chạy luồng để gọi hàm main với file_id
    thread = Thread(target=main, args=(file_id, storage_option, school_id))
    thread.start()



def call_test_function_mod(file_id, submission_id, submission_title, callback_url, storage_option, school_id):
    def run():
        try:
            main(file_id, storage_option, school_id)  # xử lý chính
            BASE_URL = os.getenv("BASE_URL")
            # Sau khi xử lý xong, lấy dữ liệu để gửi callback
            score = db.files.find_one({"file_id": file_id})["plagiarism"]
            file_checked_doc = db.files.find_one({"file_id": file_id, "type": "checked"})

            # file_checked = base64.b64encode(file_checked_doc["content_file"]).decode("utf-8")
            url = f"{BASE_URL}report/file_id={file_id}"

            pdf_bytes = bytes(file_checked_doc['content_file'])

            output_io = download_source(pdf_bytes, file_id)
       
            file_checked = base64.b64encode(output_io.getvalue()).decode("utf-8")


            if callback_url:
                callback_payload = {
                    "submission_id": submission_id, 
                    "submission_title": submission_title,
                    "score": score,
                    "file_checked": file_checked,
                    "url": url
                }
                headers = {'Content-Type': 'application/json'}
                res = requests.post(callback_url, json=callback_payload, headers=headers)
                print("Callback sent:", res.status_code)
        except Exception as e:
            print("Error in background thread:", str(e))

    Thread(target=run).start()




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
                    call_test_function_async(file_id, storage_option, school_id)
                    return jsonify(success = True, message = "File uploaded successfully")
                return jsonify(success = False, message = "Error occurred during file upload") 
            return jsonify(success = False, message = "No file provided") 

        return jsonify(success = False, message = "School ID does not match") 
        
    return jsonify(success = False, message = "User not logged in") 

# moodle.
@file.route('/api/check_plagiarism_moodle', methods=['POST'])
def check_plagiarism_moodle():
    
    email = request.form.get('email')
    user = db.users.find_one({"email": email})
    
    school_key = request.form.get('school_key')
    school_name = request.form.get('school_name')
    school = db.schools.find_one({'school_name': school_name})
    class_id = school["school_id"] + "_" + request.form.get('class_id')
    assignment_id = school["school_id"] + "_" + request.form.get('assignment_id')
    print(f"email: {email}, school_key: {school_key}, school_name: {school_name}, class_id: {class_id}, assignment_id: {assignment_id}")
    if user and school_key == school['school_key']:
        submission_title = request.form.get('submissionTitle')
        submission_id = request.form.get('submission_id')
        storage_option = "do_not_store"
        submit_day = request.form.get('submitDay')
        file = request.files.get('file')
        callback_url = request.form.get('callback_url')

        
        if file:
            if db.files.find_one({"assignment_id": assignment_id, "author_id": user["user_id"]}):
                delete_file_student(user['user_id'], school["school_id"], class_id, assignment_id, user["user_id"]) and delete_student_submit(school["school_id"], assignment_id, user["user_id"])
            result, file_id = add_file(user['role'], school["school_id"], class_id, assignment_id, submission_title, user["user_id"], submit_day, file, storage_option)
            if result and add_student_submit(school["school_id"], assignment_id, user["user_id"]):
                
                call_test_function_mod(file_id, submission_id, submission_title, callback_url, storage_option, school["school_id"])

                return jsonify({"success": "accepted"}), 202
            else:
                print("ko check được")
                return jsonify({"error": "Can't import file"}), 500
        else:
            print("không thấy file")

            return jsonify({"error": "not file"}), 500
    else:
        print("Sai key, ko có user")

        return jsonify({"error": "not file"}), 500
            
    

    
@file.route('/mod/api/delete_file', methods=['DELETE'])
def delete_file_api_mod():
    data = request.get_json()
    print(data)
    if not data:
        return jsonify(success = False, message = "Please enter valid data")

    email = data.get('email')
    user = db.users.find_one({"email": email})
    
    school_key = data.get('school_key')
    school_name = data.get('school_name')
    school = db.schools.find_one({'school_name': school_name})
    class_id = school["school_id"] + "_" + str(data.get('class_id'))
    assignment_id = school["school_id"] + "_" + str(data.get('assignment_id'))
    if user and school_key == school['school_key']:
        if school['school_id'] == user['school_id']:
            if user['role'] == "Teacher":
                print("Xoa file")
                print(f"school_id: {school['school_id']}, class_id: {class_id}, assignment_id: {assignment_id}, user_id: {user['user_id']}")
                if delete_file_teacher(school['school_id'], class_id, assignment_id, user["user_id"]) and delete_student_submit(school['school_id'], assignment_id, user['user_id']):
                    return jsonify(success = True, message = "File deleted successfully")
                return jsonify(success = False, message = "Error occurred during file deletion")  
            if user['role'] == "Student":
                if delete_file_student(user['user_id'], school['school_id'], class_id, assignment_id, user["user_id"]) and delete_student_submit(school['school_id'], assignment_id, user["user_id"]):
                    return jsonify(success = True, message = "File deleted successfully")
                return jsonify(success = False, message = "Error occurred during file deletion") 
        return jsonify(success = False, message = "School ID does not match") 
        
    return jsonify(success = False, message = "User not logged in") 
        


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
                    return jsonify(success = True, message = "File deleted successfully")
                return jsonify(success = False, message = "Error occurred during file deletion")  
            if user['role'] == "Student":
                if delete_file_student(user['user_id'], school_id, class_id, assignment_id, student_id) and delete_student_submit(school_id, assignment_id, student_id):
                    return jsonify(success = True, message = "File deleted successfully")
                return jsonify(success = False, message = "Error occurred during file deletion") 
        return jsonify(success = False, message = "School ID does not match") 
        
    return jsonify(success = False, message = "User not logged in") 


@file.route('/api/delete_file@file_id=<file_id>', methods=['DELETE'])
def delete_file_quick_submit_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        if user['role'] == "Teacher":
            print("Xoa file")
            if delete_file_quick_submit(user['school_id'], file_id):
                return jsonify(success = True, message = "File deleted successfully")
            return jsonify(success = False, message = "Error occurred during file deletion") 
        return jsonify(success = False, message = "Permission denied") 
        
    return jsonify(success = False, message = "User not logged in") 

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
                file_name += '_checked'
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
                    file_name += '_checked'
                    return send_file(
                        pdf_io, 
                        download_name=file_name,
                        as_attachment=True, 
                        mimetype='application/pdf'
                    )
                return jsonify(success=False, message="Unauthorized access.")  # sai 1
            
            return jsonify(success=False, message="Unauthorized role.")  # sai 2
        
        return jsonify(success=False, message="Unauthorized school.")  # sai 3
    
    return jsonify(success=False, message="User not authenticated.")  # sai 




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

            file_name = pdf_record['title'] + '_checked'
            output_io = download_source(pdf_bytes, file_id)
            return send_file(
                output_io,
                download_name=file_name,
                as_attachment=True,
                mimetype='application/pdf'
            )


        if user['role'] == "Student" and pdf_record['author_id'] == user['user_id']:
            pdf_bytes = bytes(pdf_record['content_file'])

            file_name = pdf_record['title'] + '_checked'
            output_io = download_source(pdf_bytes, file_id)
            return send_file(
                output_io,
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
        return jsonify(success = True, message = "Data loaded successfully", list_files = list_files, school_source_off = school_source_off, school_source_on = school_source_on, school_exclusion_source = school_exclusion_source, school_exclusion_text = school_exclusion_text )
    return jsonify(success = False, message = "Error occurred while loading data") 

@file.route("/api/highlight_school@file_id=<file_id>-school_id=<school_id>", methods=['POST'])
def highlight_school_api(file_id, school_id):
    if 'user_id' not in session:
        return render_template('login.html')
    file_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source = file_checked.get('source')
    type_source = []
    if source['student_data']:
        type_source.append('student_Data')
    if source['internet']:
        type_source.append('Internet')
    if source['paper']:
        type_source.append("paper")
    file_highlighted = highlight_school(file_id, school_id, type_source)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_view_all(file_id, Binary(pdf_output_stream.getvalue()))
        return jsonify(success = True, message = "Source updated successfully") 
    return jsonify(success = False, message = "Error occurred during source removal") 


@file.route("/api/remove_source_school@file_id=<file_id>-school_id=<school_id>", methods=['POST'])
def remove_source_school_api(file_id, school_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        remove_source_school(file_id, school_id)
        return jsonify(success = True, message = "Source updated successfully") 
    return jsonify(success = False, message = "Error occurred during source removal") 

@file.route("/api/add_source_school@file_id=<file_id>-school_id=<school_id>", methods=['POST'])
def add_source_school_api(file_id, school_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_source_school(file_id, school_id)
        return jsonify(success = True, message = "Updated successfully") 
    return jsonify(success = False, message = "Error occurred during update") 


@file.route("/api/remove_text_school@file_id=<file_id>-school_id=<school_id>-page=<page>-sentence=<sentence_index>", methods=['POST'])
def remove_source_school_text(file_id, school_id, page, sentence_index):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        remove_text_school(file_id, school_id, page, sentence_index)
        return jsonify(success = True, message = "Updated successfully") 
    return jsonify(success = False, message = "Error occurred during update") 
    
@file.route("/api/add_text_school@file_id=<file_id>-page=<page>-sentence=<sentence_index>-<source_id>", methods=['POST'])
def add_source_school_text(file_id, page, sentence_index, source_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_text_school(file_id, page, sentence_index, source_id)
        return jsonify(success = True, message = "Updated successfully") 
    return jsonify(success = False, message = "Error occurred during update") 

@file.route("/api/add_all_source_school@file_id=<file_id>", methods=['POST'])
def add_all_source_school_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_all_source_school(file_id)
        return jsonify(success = True, message = "Updated successfully") 
    return jsonify(success = False, message = "Error occurred during update") 

@file.route("/api/add_all_text_school@file_id=<file_id>", methods=['POST'])
def add_all_text_school_api(file_id):
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user:
        add_all_text_school(file_id)
        return jsonify(success = True, message = "Updated successfully") 
    return jsonify(success = False, message = "Error occurred during update") 

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
        return jsonify(success = True, message = "Updated successfully") 
    return jsonify(success = False, message = "Error occurred during update") 

@file.route("/api/import_file", methods=['POST'])
def import_file_api():
    if 'user_id' not in session:
        return render_template('login.html')
    user = db.users.find_one({'_id': ObjectId(session['user_id'])})
    if user['role'] == "Teacher":
        file = request.files.get('file')
        school_cursor = db.schools.find_one({'school_id': user['school_id']})
        if file:
            print(file.filename)
            import_file_to_elastic(school_cursor['ip_cluster'], school_cursor['index_name'], user['school_id'], school_cursor['school_name'], file, file.filename, "paper")
            return jsonify(success = True, message = "File upload success") 
        return jsonify(success = False, message = "Document not found") 
    return jsonify(success = False, message = "You do not have permission to submit the file.") 