from app.extensions import db
import fitz
import io
from app.models.search_system.processing_sentence import embedding_vietnamese, preprocess_text_vietnamese, remove_sentences, split_sentences, extract_pdf_text, clean_vietnamese_sentence
from elasticsearch import Elasticsearch
from itertools import groupby

def cluster_remote():
    clusters = []
    school_cursor = db.schools.find({"school_id": {"$ne": "1"}})
    for school in school_cursor:
        clusters.append([school['school_id'], school['index_name']])

    return clusters


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
        "content_file": content,  # Lưu PDF dưới dạng Binary
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

def update_file_checked(file_id, content):
    db.files.update_one({
            "file_id": file_id,
            "type": "checked"
        },
        {
            "$set": {
                "content_file": content
            }
        }
    )

def update_file_view_all(file_id, content):
    db.files.update_one({
            "file_id": file_id,
            "type": "view_all"
        },
        {
            "$set": {
                "content_file": content
            }
        }
    )


def update_file(file_id, plagiarism):
    db.files.update_many({
            "file_id": file_id
        },
        {
            "$set": {
                "plagiarism": plagiarism
            }
        }
    )
    
def update_school_stt(file_id, type, type_sources):
    # update STT
    sentences_data = db.sentences.find({"file_id": file_id,
                                                "references": {"$ne": "checked"}, 
                                                "quotation_marks": {"$ne": "checked"}, 
                                                "sources": {"$ne": None, "$ne": []}})
    school_source = {}
    minWordValue = db.files.find_one({"file_id": file_id, "type": 'checked'})['fillter']['min_word']['minWordValue']
    word_count = db.files.find_one({"file_id": file_id, "type": 'checked'}).get('word_count', 0)

    if sentences_data:
        for sentence in sentences_data:
            sources = sentence.get('sources', [])
            # filtered_sources = [source for source in sources if (source['except'] == 'no' and source['type_source'] in type_sources)]
            filtered_sources = [
                source for source in sources 
                if (source['except'] == 'no' and 
                    source['type_source'] in type_sources and 
                    source.get('highlight', {}).get('word_count_sml', 0) > int(minWordValue))
            ]
            if filtered_sources:
                for source in filtered_sources:
                    school_id = source['school_id']
                    highlight_source = source['highlight']
                    if school_id not in school_source:
                        school_source[school_id] = {
                            "word_count": 0, 
                        }
                    school_source[school_id]['word_count'] += highlight_source.get('word_count_sml', 0)
        for school_id_source, source_data in school_source.items():
            if source_data.get('word_count', 0) < word_count/200:
                db.sentences.update_many(
                    {"file_id": file_id, "sources.school_id": school_id_source},
                    {"$set": {"sources.$[elem].except": "except"}}, 
                    array_filters=[{"elem.school_id": school_id_source}]
                )
        school_source = {} 
        sentences_data = db.sentences.find({"file_id": file_id,
                                                "references": {"$ne": "checked"}, 
                                                "quotation_marks": {"$ne": "checked"}, 
                                                "sources": {"$ne": None, "$ne": []}})   
        if type == "best_source":
            for sentence in sentences_data:
                sources = sentence.get('sources', [])
                # filtered_sources = [source for source in sources if (source['except'] == 'no' and source['type_source'] in type_sources)]
                filtered_sources = [
                    source for source in sources 
                    if (source['except'] == 'no' and 
                        source['type_source'] in type_sources and 
                        source.get('highlight', {}).get('word_count_sml', 0) > int(minWordValue))
                ]
                if filtered_sources:
                    source_max = max(filtered_sources, key=lambda x: x['score'])
                    school_id = source_max['school_id']
                    highlight_source = source_max['highlight']
                    if school_id not in school_source:
                        school_source[school_id] = {
                            "word_count": 0, 
                        }
                    school_source[school_id]['word_count'] += highlight_source.get('word_count_sml', 0)
        if type == "view_all":
            for sentence in sentences_data:
                sources = sentence.get('sources', [])
                # filtered_sources = [source for source in sources if (source['except'] == 'no' and source['type_source'] in type_sources)]
                filtered_sources = [
                    source for source in sources 
                    if (source['except'] == 'no' and 
                        source['type_source'] in type_sources and 
                        source.get('highlight', {}).get('word_count_sml', 0) > int(minWordValue))
                ]
                if filtered_sources:
                    for source in filtered_sources:
                        school_id = source['school_id']
                        highlight_source = source['highlight']
                        if school_id not in school_source:
                            school_source[school_id] = {
                                "word_count": 0, 
                            }
                        school_source[school_id]['word_count'] += highlight_source.get('word_count_sml', 0)
        school_source = sorted(school_source.items(), key=lambda x: x[1]['word_count'], reverse=True)

    word_count_sml = 0
    if school_source:
        for i, (school_id_source, source_data) in enumerate(school_source):
            db.sentences.update_many(
                {"file_id": file_id, "sources.school_id": school_id_source},
                {"$set": {"sources.$[elem].school_stt": i + 1}}, 
                array_filters=[{"elem.school_id": school_id_source}]
            )

    sentences_data = db.sentences.find({"file_id": file_id,
                                                "references": {"$ne": "checked"}, 
                                                "quotation_marks": {"$ne": "checked"}, 
                                                "sources": {"$ne": None, "$ne": []}})
    if sentences_data:
        for sentence in sentences_data:
                sources = sentence.get('sources', [])
                filtered_sources = [
                    source for source in sources 
                    if (source['except'] == 'no' and 
                        source['type_source'] in type_sources and 
                        source.get('highlight', {}).get('word_count_sml', 0) > int(minWordValue))
                ]

                if filtered_sources:
                    source_max = max(filtered_sources, key=lambda x: x['score'])
                    word_count_sml = word_count_sml +  source_max['highlight'].get('word_count_sml', 0)
    
    plagiarism = word_count_sml * 100 / word_count
    if plagiarism > 100:
        plagiarism = 100
    plagiarism = f"{plagiarism:.2f}"
    result = {
        "plagiarism": plagiarism 
    }
    db.files.update_many(
                {"file_id": file_id},  
                {"$set": result} 
            )

    return school_source

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

        filtered_sources = [source for source in sources if source['except'] == 'no' and source['type_source'] in type_source and int(source['highlight']['word_count_sml']) > int(minWordValue)]

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

def get_sources(file_id, type_source):
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

    sources_list = []
    for doc in all_documents:
        sources = doc.get('sources', [])
        sources_dict = {}
        filtered_sources = []

        filtered_sources = [source for source in sources if source['except'] == 'no' and source['type_source'] in type_source and int(source['highlight']['word_count_sml']) > int(minWordValue)]

        if filtered_sources:
            filtered_sources.sort(key=lambda x: x["school_id"])
            highest_per_school = []
            for school_id, group in groupby(filtered_sources, key=lambda x: x["school_id"]):
                highest = max(group, key=lambda x: x["score"])
                highest_per_school.append(highest)
            for source in highest_per_school:
                school_id = source['school_id']
                score = source['score']
                if school_id not in sources_dict or score > sources_dict[school_id]['score']:
                    sources_dict[school_id] = {
                        "page": doc.get('page', None),
                        "school_id": source['school_id'],
                        "school_name": source['school_name'],
                        "color": source['color'],
                        "school_stt": source['school_stt'],
                        "file_id": source['file_id'],
                        "best_match": source['best_match'],
                        "score": source['score'],
                        "highlight": source['highlight']
                    }
            sources_list.extend(sources_dict.values())

    return sources_list

def retrieve_pdf_from_mongodb(file_id):
    file_data = db.files.find_one({"file_id": file_id, "type": 'raw'})
    if file_data:
        return file_data['content_file']
    return None

def add_file_to_elasticsearch(ip_cluster, school_id, school_name, file_id, index_name, type):
    file_cursor = find_file(file_id)
    pdf_binary = file_cursor['content_file']

    pdf_document = fitz.open(stream=io.BytesIO(pdf_binary), filetype="pdf")
    text = ""
    for page_num in range(pdf_document.page_count):
        page = pdf_document.load_page(page_num)
        page_text = page.get_text("text")
        text += page_text

    if text:
        sentences = split_sentences(text)
        if sentences:
            sentences = remove_sentences(sentences)
            if sentences:
                # processed_sentences = [preprocess_text_vietnamese(sentence)[0] for sentence in sentences]
                if sentences:
                    vector_sentences = embedding_vietnamese(sentences)
                    if vector_sentences is not None and vector_sentences.any():
                        save_to_elasticsearch(ip_cluster, sentences, vector_sentences, school_id, school_name, int(file_id), file_cursor['title'], index_name, type)

def import_file_to_elastic(ip_cluster, index_name, school_id, school_name, file, title, type):
    text = extract_pdf_text(file)
    if text:
        sentences = split_sentences(text)
        if sentences:
            sentences = remove_sentences(sentences)
            if sentences:
                # processed_sentences = [preprocess_text_vietnamese(sentence)[0] for sentence in sentences]
                if sentences:
                    vector_sentences = embedding_vietnamese(sentences)
                    if vector_sentences is not None and vector_sentences.any():
                        add_to_elasticsearch(ip_cluster, sentences, vector_sentences, school_id, school_name, title, index_name, type)


from elasticsearch.helpers import bulk
def save_to_elasticsearch(ip_cluster, processed_sentences, vectors, school_id, school_name, file_id, file_name, index_name, type):
    es_school = Elasticsearch([ip_cluster], timeout=1000)
    bulk_data = []
    # Chuẩn bị dữ liệu để chèn vào Elasticsearch
    for i, sentence in enumerate(processed_sentences):
        document = {
            '_index': index_name,  
            '_source': {  
                'school_id': school_id,
                'school_name': school_name,
                'file_id': file_id,
                'file_name': file_name,
                'sentence': sentence,
                'vector': vectors[i],
                'type': type
            }
        }

        bulk_data.append(document)

    bulk(es_school, bulk_data)


def add_to_elasticsearch(ip_cluster, processed_sentences, vector_sentences, school_id, school_name, title, index_name, type):
    es_school = Elasticsearch([ip_cluster], timeout=1000)

    query = {
        "size": 1,
        "sort": [
            {"file_id": {"order": "asc"}}
        ],
        "_source": ["file_id"]  
    }

    response = es_school.search(index=index_name, body=query)
    file_id_min = 0
    if response['hits']['hits']:
        file_id_min = response['hits']['hits'][0]['_source']['file_id']

    print(file_id_min)
    bulk_data = []
    # Chuẩn bị dữ liệu để chèn vào Elasticsearch
    for i, sentence in enumerate(processed_sentences):
        document = {
            '_index': index_name,  
            '_source': {  
                'school_id': school_id,
                'school_name': school_name,
                'file_id': file_id_min - 1,
                'file_name': title,
                'sentence': sentence,
                'vector': vector_sentences[i],
                'type': type
            }
        }

        bulk_data.append(document)

    bulk(es_school, bulk_data)



def word_count_function(file_id):
    word_count = 0
    sentences = db.sentences.find({'file_id': file_id})
    for sentence in sentences:
        sentence_clean = clean_vietnamese_sentence(sentence['sentence']) 
        word_count += len(sentence_clean.split())
    return word_count
