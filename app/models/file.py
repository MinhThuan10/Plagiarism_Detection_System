# models/file.py
from app.extensions import db
from bson.objectid import ObjectId
from bson import Binary
import io
import mimetypes
from app.models.search_system.highlight import highlight
from app.models.search_system.models import update_file_checked
import os
from datetime import datetime
from itertools import groupby
import platform
from pymongo import DESCENDING



def find_assignment_id(assignment_id):
    file_cursor = db.assignments.find_one({'assignment_id':assignment_id})
    if file_cursor:
        # Chuyển ObjectId sang chuỗi (nếu có)
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file_cursor.items()}
        return file_data
    return None


def load_files(assignment_id):
    files_cursor = db.files.find({"assignment_id": assignment_id, "quick_submit": "no", "type": "raw"})
    list_files = []
    for file in files_cursor:
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file.items()}
        file_data.pop('content_file', None)
        list_files.append(file_data)
    return list_files

def load_files_quick_submit(school_id):
    files_cursor = db.files.find({"school_id": school_id, "quick_submit": "yes", "type": "raw"})
    list_files = []
    for file in files_cursor:
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file.items()}
        file_data.pop('content_file', None)
        list_files.append(file_data)
    return list_files


def get_file_type(file):
    mime_type = mimetypes.guess_type(file.filename)[0]
    if mime_type == 'application/pdf':
        file_type = 'pdf'
    elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
        file_type = 'word'
    else:
        file_type = 'unknown'
    return file_type


def add_file(role, school_id, class_id, assignment_id, title, author_id, submit_day, file, storage_option):
    base_dir = os.path.dirname(__file__)  
    doc_filename = "word.docx"
    pdf_filename = "change_to_pdf.pdf"
    pdf_path = os.path.join(base_dir, pdf_filename)
    doc_path = os.path.join(base_dir, doc_filename)

    if db.files.find_one({"assignment_id": assignment_id, "author_id": author_id}):
        return False, ""
    if role == "Teacher":
        if db.files.find_one({"assignment_id": assignment_id, "title": title}):
            return False, ""
    if role == "Student":
        assignment = db.assignments.find_one({"assignment_id": assignment_id})
        end_day = datetime.strptime(assignment['end_day'], "%m/%d/%Y")
        if datetime.now() > end_day:
            return False, ""
    
    file_type = get_file_type(file)
    if file_type == 'unknown':
        return False, ""

         
    if file_type == 'pdf':
        file = file.read()


    if file_type == 'word':
        if platform.system() == "Windows":
            file = word_to_pdf_windown(file)
        else:
            file = word_to_pdf_linux(file)


    pattern = f'^{school_id}_[0-9]+$'

    max_file = db.files.find_one(
        {'file_id': {'$regex': pattern}},
        sort=[(
            'file_id', DESCENDING
        )]
    )
    if max_file:
        max_file_id = int(max_file['file_id'].split('_')[1])
    else:
        max_file_id = 0

    file_id = str(school_id) + '_' + str(max_file_id + 1)

    # max_file = max(
    #     db.files.find({}, {"file_id": 1}),
    #     key=lambda x: (len(x['file_id']), int(x['file_id'])),
    #     default=None
    # )
    # max_file = max_file['file_id'] if max_file else 0 

    db.files.insert_one({
        "school_id": school_id,
        "class_id": class_id,
        'assignment_id': assignment_id,
        "file_id": file_id,
        "title": title,
        "author_id": author_id,
        "author_name": "",
        "submit_day": submit_day,
        "content_file": Binary(file),
        "storage": storage_option,
        "quick_submit": "no",
        "plagiarism": "",
        "type": "raw"
    })
    if os.path.exists(pdf_path):
        os.remove(doc_path)
        os.remove(pdf_path)

    return True, file_id


def add_file_quick_submit(school_id, author_name, author_id, submission_title, submit_day, file, storage_option):


    file_type = get_file_type(file)
    if file_type == 'unknown':
        return False, ""

    if file_type == 'pdf':
        file = file.read()

    if file_type == 'word':

        if platform.system() == "Windows":
            file = word_to_pdf_windown(file)
        else:
            file = word_to_pdf_linux(file)

    pattern = f'^{school_id}_[0-9]+$'

    max_file = db.files.find_one(
        {'file_id': {'$regex': pattern}},
        sort=[(
            'file_id', DESCENDING
        )]
    )
    if max_file:
        max_file_id = int(max_file['file_id'].split('_')[1])
    else:
        max_file_id = 0

    file_id = str(school_id) + '_' + str(max_file_id + 1)

    # max_file = max(
    #     db.files.find({}, {"file_id": 1}),
    #     key=lambda x: (len(x['file_id']), int(x['file_id'])),
    #     default=None
    # )
    # max_file = max_file['file_id'] if max_file else 0 

    db.files.insert_one({
        "school_id": school_id,
        "class_id": "",
        'assignment_id': "",
        "file_id": file_id,
        "title": submission_title,
        "author_id": author_id,
        "author_name": author_name,
        "submit_day": submit_day,
        "content_file": Binary(file),
        "storage": storage_option,
        "quick_submit": "yes",
        "plagiarism": "",
        "type": "raw",
    })
    return True, file_id

def word_to_pdf_linux(file):
    import subprocess

    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)

    word_path = os.path.join(upload_dir, 'file.docx')
    pdf_filename = 'file.pdf'
    pdf_path = os.path.join(upload_dir, pdf_filename)
    file.save(word_path)
    subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", word_path, "--outdir", upload_dir], check=True)
    
    with open(pdf_path, "rb") as pdf_file:
        file = pdf_file.read()

    if os.path.exists(word_path):
        os.remove(word_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)

    return file


def word_to_pdf_windown(file):
    import pythoncom
    import comtypes.client

    current_directory = os.getcwd()  # Lấy đường dẫn hiện tại
    word_path = os.path.join(current_directory, 'file.docx')
    pdf_path = os.path.join(current_directory, 'file.pdf')
    file.save(word_path)
    pythoncom.CoInitialize()
    try:
        # Đường dẫn tệp
        docx_path = os.path.abspath(word_path)
        pdf_path = os.path.abspath(pdf_path)

        # Tạo đối tượng Word
        word = comtypes.client.CreateObject("Word.Application")
        word.Visible = False

        # Mở và chuyển đổi tệp
        in_file = word.Documents.Open(docx_path)
        in_file.SaveAs(pdf_path, FileFormat=17)  # 17: Định dạng PDF
        in_file.Close()

        # Thoát ứng dụng Word
        word.Quit()
    finally:
        # Hủy khởi tạo COM
        pythoncom.CoUninitialize()

    with open(pdf_path, "rb") as pdf_file:
        file = pdf_file.read()

    if os.path.exists(word_path):
        os.remove(word_path)
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
   
    return file


def delete_file_teacher(school_id, class_id, assignment_id, student_id):
    file =  db.files.find_one({"assignment_id": assignment_id, "author_id": student_id, "type": "raw"})
    if not file:
        return False
    if school_id == file['school_id'] and class_id == file['class_id'] and assignment_id == file['assignment_id']:
        file_cursor = db.files.find_one({"assignment_id": assignment_id,"author_id": student_id, "type": "raw"})
        db.sentences.delete_many({"file_id": file_cursor['file_id']})
        db.files.delete_many({"assignment_id": assignment_id,"author_id": student_id})
        return True
    return False
    
def delete_file_student(user_id, school_id, class_id, assignment_id, student_id):
    file =  db.files.find_one({ "assignment_id": assignment_id, "author_id": student_id, "type": "raw"})
    if not file:
        return False
    if user_id == file['author_id'] and school_id == file['school_id'] and class_id == file['class_id'] and assignment_id == file['assignment_id']:


        file_cursor = db.files.find({"assignment_id": assignment_id,"author_id": student_id})
        for file in file_cursor:
            db.sentences.delete_many({"file_id": file['file_id']})
            
        db.files.delete_many({"assignment_id": assignment_id,"author_id": student_id})
        
        return True
    return False

def delete_file_quick_submit(school_id, file_id):
    file =  db.files.find_one({"file_id": file_id, "quick_submit": "yes", "type": "raw"})
    if not file:
        return False
    if school_id == file['school_id']:
        db.files.delete_many({"file_id": file_id})
        db.sentences.delete_many({"file_id": file_id})
        
        return True
    return False

def delete_file_for_user(student_id, class_id):
    file_cursor = db.files.find({"author_id": student_id, "class_id": class_id})
    if file_cursor:
        for file in file_cursor:
            db.sentences.delete_many({"file_id": file['file_id'], "class_id": class_id})
        db.files.delete_many({"author_id": student_id, "class_id": class_id})
    return True

def get_file_report(file_id):

    file_data_checked = db.files.find_one({"file_id": file_id, "type": 'checked'})
    
    list_files = []
    if file_data_checked:  # Check if a document is found
        # Process the document
        file_data = {key: (str(value) if isinstance(value, ObjectId) else value) for key, value in file_data_checked.items()}
        file_data.pop('content_file', None)
        list_files.append(file_data)
    sentences_data = db.sentences.find({"file_id": file_id,
                                            "references": {"$ne": "checked"}, 
                                            "quotation_ marks": {"$ne": "checked"}, 
                                            "sources": {"$ne": None, "$ne": []}})
    if sentences_data:
        source_file   = file_data_checked.get('source')  
        minWordValue   = file_data_checked.get('fillter').get('min_word').get('minWordValue')

        type_sources = []
        if source_file['student_data'] == True:
            type_sources.append('student_Data')
        if source_file['internet'] == True:
            type_sources.append('Internet')
        if source_file['paper'] == True:
            type_sources.append("paper")

        school_source_off = {}
        school_source_on = {}
        school_exclusion_source = {}
        school_exclusion_text = {}
        

        for sentence in sentences_data:
            sources = sentence.get('sources', [])
            page = sentence.get('page', None)
            sentence_index = sentence.get('sentence_index', None)

            if sources:
                    # OFF
                filtered_no = [
                    source for source in sources 
                    if (source['except'] == 'no' and 
                        source['type_source'] in type_sources and 
                        source.get('highlight', {}).get('word_count_sml', 0) > int(minWordValue))
                ]
    
                if filtered_no:
                    best_source = max(filtered_no, key=lambda x: x['score'])
                    school_id = best_source['school_id']
                    school_name = best_source['school_name']
                    color = best_source['color']
                    type_source = best_source['type_source']
                    file_id = best_source['file_id']
                    best_match = best_source['best_match']
                    highlight = best_source['highlight']

                    if school_id not in school_source_off:
                        school_source_off[school_id] = {
                            "school_name": school_name,
                            "word_count": 0,
                            "word_count_detail": {
                                "student_Data": 0,
                                "Internet": 0,
                                "paper": 0
                            },
                            "color": color,
                            "type_source":[type_source],
                            "sentences": {}  
                        }
                    # update
                    else:
                        if type_source not in school_source_off[school_id]['type_source']:
                            school_source_off[school_id]['type_source'].append(type_source)

                    # 
                    school_source_off[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                    school_source_off[school_id]['word_count_detail'][type_source] += highlight.get('word_count_sml', 0)

                    if page not in school_source_off[school_id]['sentences']:
                        school_source_off[school_id]['sentences'][page] = {}
                    school_source_off[school_id]['sentences'][page][sentence_index] = {
                        "file_id": file_id,
                        "best_match": best_match,
                        "word_count_sml": highlight.get('word_count_sml', 0),
                        "paragraphs": highlight.get('paragraphs'),
                    }


                    # ON NÈ NHÉ
                    filtered_no.sort(key=lambda x: x["school_id"])
                    highest_per_school = []
                    for school_id, group in groupby(filtered_no, key=lambda x: x["school_id"]):
                        highest = max(group, key=lambda x: x["score"])
                        highest_per_school.append(highest)
                    for source in highest_per_school:
                        
                        school_id = source['school_id']
                        school_name = source['school_name']
                        color = source['color']
                        type_source = source['type_source']
                        file_id = source['file_id']
                        best_match = source['best_match']
                        highlight = source['highlight']

                    
                        if school_id not in school_source_on:
                            school_source_on[school_id] = {
                                "school_name": school_name,
                                "word_count": 0,
                                "word_count_detail": {
                                    "student_Data": 0,
                                    "Internet": 0,
                                    "paper": 0
                                },
                                "color": color,
                                "type_source":[type_source],
                                "sentences": {}  
                            }
                            # update
                        else:
                            if type_source not in school_source_on[school_id]['type_source']:
                                school_source_on[school_id]['type_source'].append(type_source)
                            
                        school_source_on[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                        school_source_on[school_id]['word_count_detail'][type_source] += highlight.get('word_count_sml', 0)

                        if page not in school_source_on[school_id]['sentences']:
                            school_source_on[school_id]['sentences'][page] = {}
                        school_source_on[school_id]['sentences'][page][sentence_index] = {
                            "file_id": file_id,
                            "best_match": best_match,
                            "word_count_sml": highlight.get('word_count_sml', 0),
                            "paragraphs": highlight.get('paragraphs'),
                        }


            filtered_sources = [source for source in sources if (source['except'] == 'source')]
            if filtered_sources:
                for source in filtered_sources:
                    school_id = source['school_id']
                    school_name = source['school_name']
                    if school_id not in school_exclusion_source:
                        school_exclusion_source[school_id] = {
                            "school_name": school_name,
                        }

            filtered_text = [source for source in sources if (source['except'] == 'text')]
            if filtered_text :
                for source in filtered_text :
                    page = sentence.get('page')
                    sentence_index = sentence.get('sentence_index')
                    school_name = source['school_name']
                    best_match = source['best_match']
                    source_id = source['source_id']
                    if page not in school_exclusion_text:
                        school_exclusion_text[page] = {}
                    if sentence_index not in school_exclusion_text[page]:
                        school_exclusion_text[page][sentence_index] = {}  # Khởi tạo nếu chưa có

                    school_exclusion_text[page][sentence_index][source_id] = {
                        "school_name": school_name,
                        "best_match": best_match,
                    }

        school_source_off = sorted(school_source_off.items(), key=lambda x: x[1]['word_count'], reverse=True)
        school_source_on = sorted(school_source_on.items(), key=lambda x: x[1]['word_count'], reverse=True)

        return list_files, school_source_off, school_source_on, school_exclusion_source, school_exclusion_text
    
def remove_source_school(file_id, school_id):
    db.sentences.update_many(
        {"file_id": file_id, "sources.school_id": int(school_id), "sources.except": "no"},
        {"$set": {"sources.$[elem].except": "source"}},
        array_filters=[{"elem.school_id": int(school_id), "elem.except": "no"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('student_Data')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("paper")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def add_source_school(file_id, school_id):
    db.sentences.update_many(
        {"file_id": file_id, "sources.school_id": int(school_id), "sources.except": "source"},
        {"$set": {"sources.$[elem].except": "no"}},
        array_filters=[{"elem.school_id": int(school_id), "elem.except": "source"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('student_Data')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("paper")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def add_all_source_school(file_id):
    db.sentences.update_many(
        {"file_id": file_id, "sources.except": "source"},
        {"$set": {"sources.$[elem].except": "no"}},
        array_filters=[{"elem.except": "source"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('student_Data')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("paper")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def remove_text_school(file_id, school_id, page, sentence_index):
    db.sentences.update_many(
        {"file_id": file_id, "sources.school_id": int(school_id), "page": int(page), "sentence_index": int(sentence_index) ,"sources.except": "no"},
        {"$set": {"sources.$[elem].except": "text"}},
        array_filters=[{"elem.school_id": int(school_id), "elem.except": "no"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('student_Data')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("paper")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def add_all_text_school(file_id):
    db.sentences.update_many(
        {"file_id": file_id, "sources.except": "text"},
        {"$set": {"sources.$[elem].except": "no"}},
        array_filters=[{"elem.except": "text"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('student_Data')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("paper")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def add_text_school(file_id, page, sentence_index, source_id):
    print(page, sentence_index, source_id)
    db.sentences.update_many(
        {"file_id": file_id, "page": int(page), "sentence_index":  int(sentence_index) , "sources.source_id":  int(source_id), "sources.except": "text"},
        {"$set": {"sources.$[elem].except": "no"}},
        array_filters=[{"elem.source_id": int(source_id), "elem.except": "text"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('student_Data')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("paper")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def apply_filter(file_id, studentData, internet, paper, references, curlybracket, minWord, minWordValue):   
    if minWord == True:
        result = {
            "source.student_data": studentData,
            "source.internet": internet,
            "source.paper": paper,
            "fillter.references": references,
            "fillter.quotation_marks": curlybracket,
            "fillter.min_word.min_word": minWord,
            "fillter.min_word.minWordValue": minWordValue
        }
        
    else:
        result = {
            "source.student_data": studentData,
            "source.internet": internet,
            "source.paper": paper,
            "fillter.references": references,
            "fillter.quotation_marks": curlybracket,
            "fillter.min_word.min_word": minWord,
            "fillter.min_word.minWordValue": 3
        }


    db.files.update_one(
                {"file_id": file_id, "type": "checked"},  
                {"$set": result} 
            )
       
    if references == True:
        db.sentences.update_many(
            {"file_id": file_id, "references": "yes"},
            {"$set": {"references": "checked"}}
        )

    else:
        db.sentences.update_many(
            {"file_id": file_id, "references": "checked"},
            {"$set": {"references": "yes"}}
        )

    if curlybracket == True:
        db.sentences.update_many(
            {"file_id": file_id, "quotation_marks": "yes"},
            {"$set": {"quotation_marks": "checked"}}
        )
    else:
        db.sentences.update_many(
            {"file_id": file_id, "quotation_marks": "checked"},
            {"$set": {"quotation_marks": "yes"}}
        )

    
    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('student_Data')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("paper")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from PyPDF2 import PdfMerger
import os

def draw_turnitin_style(canvas, width, height, name, word_count, source_data):
    canvas.setFont("Helvetica-Bold", 16)
    canvas.drawString(30, height - 40, name)

    # Vẽ dòng kẻ mỏng màu xám nhạt
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.5)  # độ dày rất mỏng
    canvas.line(30, height - 50, width - 30, height - 50)

    canvas.setFillColor(colors.red)  # đổi màu chữ thành đỏ
    canvas.setFont("Helvetica", 8)
    canvas.drawString(40, height - 70, "ORIGINALITY REPORT")

    # Vẽ dòng kẻ mỏng màu xám nhạt
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.3)  # độ dày rất mỏng
    canvas.line(30, height - 80, width - 30, height - 80)

    # Tổng điểm đạo văn
    word_count_plagiarism = sum(school[1]['word_count'] for school in source_data)
    total_similarity = (word_count_plagiarism / word_count) * 100
    total_similarity = round(total_similarity, 2)
    canvas.setFont("Helvetica-Bold", 36 )
    canvas.setFillColor(colors.red)
    canvas.drawString(40, height - 110, f"{total_similarity}%")

    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(40, height - 130, "SIMILARITY INDEX")


    # Tính nhóm loại nguồn
    group_stats = {"Internet Source": 0, "Publications": 0, "Student Paper": 0}
    for school in source_data:
        details = school[1]

        source_type = details["type_source"]
        if "Internet" in source_type:
            group_stats["Internet Source"] += details['word_count_detail']['Internet']
        if "paper" in source_type:
            group_stats["Publications"] += details['word_count_detail']['paper']
        if "student_Data" in source_type:
            group_stats["Student Paper"] += details['word_count_detail']['student_Data']

    group_stats["Internet Source"] = round(group_stats["Internet Source"]/word_count * 100, 2)
    group_stats["Publications"] = round(group_stats["Publications"]/word_count * 100, 2)
    group_stats["Student Paper"] = round(group_stats["Student Paper"]/word_count * 100, 2)

    canvas.setFont("Helvetica-Bold", 30 )
    canvas.setFillColor(colors.black)
    canvas.drawString(180, height - 110, f"{group_stats['Internet Source']}%")
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(180, height - 130, "Internet Source")

    canvas.setFont("Helvetica-Bold", 30 )
    canvas.setFillColor(colors.black)
    canvas.drawString(310, height - 110, f"{group_stats['Publications']}%")
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(310, height - 130, "Publications")

    canvas.setFont("Helvetica-Bold", 30 )
    canvas.setFillColor(colors.black)
    canvas.drawString(440, height - 110, f"{group_stats['Student Paper']}%")
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(colors.black)
    canvas.drawString(440, height - 130, "Student Paper")


    # Vẽ dòng kẻ mỏng màu xám nhạt
    canvas.setStrokeColor(colors.lightgrey)
    canvas.setLineWidth(0.3)  # độ dày rất mỏng
    canvas.line(30, height - 150, width - 30, height - 150)

    # Primary Sources
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(colors.red)
    canvas.drawString(40, height - 170, "PRIMARY SOURCES")

    y = height - 200

    for idx, school in enumerate(source_data, 1):
        details = school[1]
        
        color = details['color']
        canvas.setFillColor(color)
        canvas.rect(30, y - 5, 15, 15, fill=1)

        canvas.setFillColor(colors.black)
        canvas.setFont("Helvetica-Bold", 12)
        canvas.drawString(50, y, f"{idx}. {details['school_name']}")

        canvas.setFont("Helvetica", 10)
        type_source_str = (
            ", ".join(details['type_source'])
            if isinstance(details['type_source'], list)
            else str(details['type_source'])
        )

        canvas.drawString(50, y - 15, type_source_str)


        percent = round(details['word_count']/word_count * 100, 0)

        canvas.setFont("Helvetica-Bold", 14)
        canvas.drawString(500, y, f"{percent}%")
        
        y -= 40
        if y < 80:
            canvas.showPage()
            y = height - 50

from io import BytesIO
from PyPDF2 import PdfMerger, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from PyPDF2 import PdfReader, PdfWriter

def download_source(pdf_bytes, file_id):

    original_pdf_io = BytesIO(pdf_bytes)
    reader = PdfReader(original_pdf_io)

    writer = PdfWriter()

    # Copy tất cả các trang cũ
    for page in reader.pages:
        writer.add_page(page)

    # Lấy kích thước trang gốc (nếu có), fallback về A4
    if reader.pages:
        page0 = reader.pages[0]
        width = float(page0.mediabox.width)
        height = float(page0.mediabox.height)
    else:
        width, height = A4  # fallback

    file =  db.files.find_one({"file_id": file_id, "type": "checked"})
    file_name = file['title']
    word_count = file['word_count']
    
    # Tạo trang Turnitin dạng PDF bytes
    turnitin_io = BytesIO()
    c = canvas.Canvas(turnitin_io,pagesize=[width, height])

    _, school_source_off, *_ = get_file_report(file_id)

    draw_turnitin_style(c, width, height, file_name, word_count, school_source_off)

    c.save()
    turnitin_io.seek(0)

    # Merge PDF gốc với trang Turnitin
    merger = PdfMerger()
    merger.append(PdfReader(original_pdf_io))
    merger.append(PdfReader(turnitin_io))

    final_io = BytesIO()
    merger.write(final_io)
    merger.close()
    final_io.seek(0)
    return final_io