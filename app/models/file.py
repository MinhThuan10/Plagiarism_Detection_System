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




# def doc_to_pdf(doc_path, pdf_path):
#     if doc_path:
#         comtypes.CoInitialize()
#         # Khởi tạo Word Application
#         word = comtypes.client.CreateObject('Word.Application')
#         doc = word.Documents.Open(doc_path)
        
#         # Lưu file dưới dạng PDF
#         doc.SaveAs(pdf_path, FileFormat=17)
#         doc.Close()
#         word.Quit()
#         comtypes.CoUninitialize()
#         return True
#     return False



from docx2pdf import convert



    
def get_file_type(file):
    mime_type = mimetypes.guess_type(file.filename)[0]
    if mime_type == 'application/pdf':
        file_type = 'pdf'
    # elif mime_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
    #     file_type = 'word'
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
    
    # if file_type == 'word':
    #     file.save(doc_path)
    #     time.sleep(5)
    #     try:
    #         convert(doc_path, pdf_path, keep_active=    False)
    #         with open(pdf_path, 'rb') as file_data:
    #             file = file_data.read()     
    #     except Exception as e:
    #         print("Error during conversion:", e)
    #         return False, ""
         
    if file_type == 'pdf':
        file = file.read()

    max_file = db.files.find_one(sort=[('file_id', -1)])
    max_file = max_file['file_id'] if max_file else 0 
    db.files.insert_one({
        "school_id": school_id,
        "class_id": class_id,
        'assignment_id': assignment_id,
        "file_id": str(int(max_file) + 1),
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

    return True, str(int(max_file) + 1)


def add_file_quick_submit(school_id, author_name, author_id, submission_title, submit_day, file, storage_option):
    base_dir = os.path.dirname(__file__)  
    doc_filename = "word.docx"
    pdf_filename = "change_to_pdf.pdf"
    pdf_path = os.path.join(base_dir, pdf_filename)
    doc_path = os.path.join(base_dir, doc_filename)

    file_type = get_file_type(file)
    if file_type == 'unknown':
        return False, ""
    
    if file_type == 'word':
        file.save(doc_path)
        convert(doc_path, pdf_path)
        with open(pdf_path, 'rb') as file_data:
            file = file_data.read()      
    if file_type == 'pdf':
        file = file.read()

    max_file = db.files.find_one(sort=[('file_id', -1)])
    max_file = max_file['file_id'] if max_file else 0 
    db.files.insert_one({
        "school_id": school_id,
        "class_id": "",
        'assignment_id': "",
        "file_id": str(int(max_file) + 1),
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
    return True, str(int(max_file) + 1)

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
                                            "quotation_marks": {"$ne": "checked"}, 
                                            "sources": {"$ne": None, "$ne": []}})
    if sentences_data:
        source_file   = file_data_checked.get('source')  
        minWordValue   = file_data_checked.get('fillter').get('min_word').get('minWordValue')

        type_sources = []
        if source_file['student_data'] == True:
            type_sources.append('Dữ liệu học viên')
        if source_file['internet'] == True:
            type_sources.append('Internet')
        if source_file['paper'] == True:
            type_sources.append("Ấn bản")

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
                        source.get('highlight', {}).get('word_count_sml', 0) >= int(minWordValue))
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
                            "color": color,
                            "type_source":type_source,
                            "sentences": {}  
                        }
                    school_source_off[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                    school_source_off[school_id]['sentences'][sentence_index] = {
                        "page": page,
                        "file_id": file_id,
                        "best_match": best_match,
                        "word_count_sml": highlight.get('word_count_sml', 0),
                        "paragraphs": highlight.get('paragraphs'),
                    }


                    # ON NÈ NHÉ
                    for source in filtered_no:
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
                                "color": color,
                                "type_source":type_source,
                                "sentences": {}  
                            }
                        school_source_on[school_id]['word_count'] += highlight.get('word_count_sml', 0)
                        school_source_on[school_id]['sentences'][sentence_index] = {
                            "page": page,
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
                    sentence_index = sentence.get('sentence_index', "")
                    school_name = source['school_name']
                    best_match = source['best_match']
                    source_id = source['source_id']

                    if sentence_index not in school_exclusion_text:
                        school_exclusion_text[sentence_index] = {}  # Khởi tạo nếu chưa có

                    school_exclusion_text[sentence_index][source_id] = {
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
        type_sources.append('Dữ liệu học viên')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("Ấn bản")

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
        type_sources.append('Dữ liệu học viên')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("Ấn bản")

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
        type_sources.append('Dữ liệu học viên')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("Ấn bản")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def remove_text_school(file_id, school_id, sentence_index):
    db.sentences.update_many(
        {"file_id": file_id, "sources.school_id": int(school_id), "sentence_index": int(sentence_index) ,"sources.except": "no"},
        {"$set": {"sources.$[elem].except": "text"}},
        array_filters=[{"elem.school_id": int(school_id), "elem.except": "no"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('Dữ liệu học viên')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("Ấn bản")

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
        type_sources.append('Dữ liệu học viên')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("Ấn bản")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def add_text_school(file_id, sentence_index, source_id):
    db.sentences.update_many(
        {"file_id": file_id, "sources.source_id": int(source_id), "sentence_index":  int(sentence_index) ,"sources.except": "text"},
        {"$set": {"sources.$[elem].except": "no"}},
        array_filters=[{"elem.source_id": int(source_id), "elem.except": "text"}]  
    )

    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('Dữ liệu học viên')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("Ấn bản")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

def apply_filter(file_id, studentData, internet, paper, references, curlybracket, minWord, minWordValue):
    print(studentData)
    print(internet)
    print(paper)
    print(references)
    print(curlybracket)
    print(minWord)
    print(minWordValue)
   
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
       
    file_data_checked = db.files.find_one({"file_id": file_id, "type": "checked"})
    source_file   = file_data_checked.get('source')  

    type_sources = []
    if source_file['student_data'] == True:
        type_sources.append('Dữ liệu học viên')
    if source_file['internet'] == True:
        type_sources.append('Internet')
    if source_file['paper'] == True:
        type_sources.append("Ấn bản")

    file_highlighted =  highlight(file_id, type_sources)
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))

    
