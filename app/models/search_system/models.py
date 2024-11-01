from app.extensions import db

def find_file(file_id):
    files_cursor = db.files.find_one({"file_id": file_id, 'type': "raw"})
    return files_cursor

def insert_sentence(file_id,title, page_num, sentence_index, sentence, references, quotation_marks, sources):
    file_cursor = db.files.find_one({"file_id": file_id, "type": "raw"})
    result = {
                "school_id": file_cursor['school_id'],
                "class_id": file_cursor['class_id'],
                "assignment_id": file_cursor['assignment_id'],
                "file_id": file_id,
                "title": title,
                "page": page_num,
                "sentence_index": sentence_index,
                "sentence": sentence,
                "references": references,
                "quotation_marks": quotation_marks,
                "sources": sources
            }
    db.sentences.insert_one(result)

def insert_file(school_id, class_id, assignment_id, file_id,title, author_id, author_name, submit_day, page_count, word_count, plagiarism, content, storage, quick_submit, type, student_data, internet, paper, references, quotation_marks, min_word, minWordValue):
    print("insert file nè")
    result = {
        "school_id": school_id,
        "class_id": class_id,
        "assignment_id": assignment_id,
        "file_id": file_id,
        "title": title,
        "author_id": author_id,
        "author_name": author_name,
        "submit_day": submit_day,
        "page_count": page_count,
        "word_count": word_count,
        "plagiarism": plagiarism, 
        "content": content,  # Lưu PDF dưới dạng Binary
        "storage": storage,
        "quick_submit": quick_submit,
        "type": type,
        "source":{
            "student_data": student_data,
            "internet": internet,
            "paper": paper
        },
        "fillter":{
            "references": references,
            "quotation_marks": quotation_marks,
            "min_word": {
                "min_word":min_word,
                "minWordValue": minWordValue
            }
        }
    }
    db.files.insert_one(result)

def update_file(file_id, plagiarism):
    db.files.update_one({
            "file_id": file_id,
            "type": "raw"
        },
        {
            "$set": {
                "plagiarism": plagiarism
            }
        }
    )
    

def get_best_sources(file_id, type_source):
    all_documents = db.sentences.find({
        "file_id": file_id, 
        "references": {"$ne": "checked"}, 
        "quotation_marks": {"$ne": "checked"}, 
        "sources": {"$ne": None, "$ne": []}
    })

    file_doc = db.files.find_one({"file_id": file_id, "type": 'checked'})

    # Lấy minWordValue với giá trị mặc định là 3
    if file_doc and 'fillter' in file_doc:
        minWordValue = file_doc['fillter'].get('min_word', {}).get('minWordValue', 0)
    else:
        minWordValue = 3

    best_sources_list = []

    for doc in all_documents:
        sources = doc.get('sources', [])

        filtered_sources = []

        filtered_sources = [source for source in sources if source['except'] == 'no' and source['type_source'] in type_source and int(source['highlight']['word_count_sml']) >= int(minWordValue)]

        if filtered_sources:
            best_source = max(filtered_sources, key=lambda x: x['score'])

            result = {
                "page": doc.get('page', None),
 # Thông tin 'page' ở cấp ngoài cùng
                "school_id": best_source['school_id'],
                "school_name": best_source['school_name'],
                "color": best_source['color'],
                "school_stt": best_source['school_stt'],
                "file_id": best_source['file_id'],
                "type_source":best_source['type_source'],
                "best_match": best_source['best_match'],
                "score": best_source['score'],
                "highlight": best_source['highlight']
            }

            best_sources_list.append(result)

    return best_sources_list

def retrieve_pdf_from_mongodb(file_id):
    file_data = db.files.find_one({"file_id": file_id, "type": 'raw'})
    if file_data:
        return file_data['content_file']
    return None


