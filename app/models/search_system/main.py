import warnings
from urllib3.exceptions import InsecureRequestWarning
from pymongo import MongoClient
# Tắt cảnh báo InsecureRequestWarning
warnings.simplefilter('ignore', InsecureRequestWarning)
from urllib.parse import urlparse
from bson import Binary
import fitz
import io
import pymupdf  # import package PyMuPDF
import base64

from app.models.search_system.models import find_file, insert_sentence, insert_file, update_file, update_file_checked
from app.models.search_system.elastic_search import search_top10_vector_elastic
from app.models.search_system.search_google import search_google, fetch_url

from app.models.search_system.highlight import is_within, is_position, wrap_paragraphs_with_color, source_append, highlight

from app.models.search_system.processing_sentence import split_sentences, remove_sentences, preprocess_text_vietnamese, \
embedding_vietnamese, check_type_setence, calculate_dynamic_threshold, common_ordered_words, compare_sentences, \
split_snippet, check_snippet_in_sentence, compare_with_sentences


def main(file_id):
    print(file_id)
    file_cursor = find_file(file_id)
    pdf_binary = file_cursor['content_file']

    # Mở tài liệu PDF từ dữ liệu nhị phân
    pdf_document = fitz.open(stream=io.BytesIO(pdf_binary), filetype="pdf")

    current_school_id = 0
    school_cache = {}
    sentences_cache = {}
    word_count = 0
    word_count_similarity = 0
    sentence_index = 0
    references = False

    for page_num in range(pdf_document.page_count):
        
        page = pdf_document[page_num]
        text = page.get_text("text")

        sentences = split_sentences(text)
        sentences = remove_sentences(sentences)

        processed_sentences = [preprocess_text_vietnamese(sentence)[0] for sentence in sentences]
        if processed_sentences:
            vector_sentences = embedding_vietnamese(processed_sentences)
        else:
            continue
        if "TÀI LIỆU THAM KHẢO" in sentences[0].upper():
            references = True

        for i, sentence in enumerate(sentences):
            print(sentence)
            quotation_marks = check_type_setence(sentence)
            word_count += len(sentence.split())
            
            sources = []
            if processed_sentences[i] is None:
                insert_sentence(file_id, file_cursor['title'], page_num, sentence_index, sentence,
                                "yes" if references else "no", quotation_marks, [])
                sentence_index += 1
                continue
            
            result_sentences = search_top10_vector_elastic(vector_sentences[i])
            source_id = 0
            if result_sentences:
                query_length = len(processed_sentences[i].split())
                dynamic_threshold = calculate_dynamic_threshold(query_length)
                
                for result_sentence in result_sentences:
                    if float(result_sentence['score']) - 1.0 >= dynamic_threshold:
                        school_name = result_sentence['school_name']
                        file_id_source = result_sentence['file_name']
                        best_match = result_sentence['sentence']
                        type = result_sentence['type']
                        score = float(result_sentence['score']) - 1.0
                        
                        school_id = school_cache.get(school_name, current_school_id)
                        if school_name not in school_cache:
                            school_cache[school_name] = current_school_id
                            current_school_id += 1

                        positions = []
                        word_count_sml, paragraphs_best_math, paragraphs = common_ordered_words(best_match, sentence)
                        quads_sentence = page.search_for(sentence, quads=True)
                        
                        if word_count_sml > 3:
                            for paragraph in paragraphs:
                                quads_token = page.search_for(paragraph, quads=True)
                                for qua_s in quads_sentence:
                                    for qua_t in quads_token:
                                        if is_within(qua_t, qua_s):
                                            new_position = {
                                                "x_0": qua_t[0].x,
                                                "y_0": qua_t[0].y,
                                                "x_1": qua_t[-1].x,
                                                "y_1": qua_t[-1].y,
                                            }
                                            if not is_position(new_position, positions):
                                                positions.append(new_position)
                            
                            best_match = wrap_paragraphs_with_color(paragraphs_best_math, best_match, school_id)
                            sources = source_append(sources, source_id, school_id, school_name, file_id_source,
                                                    type, 'no', 0, best_match, score, word_count_sml,
                                                    paragraphs_best_math, positions)
                            source_id += 1

            # result = search_google(processed_sentences[i])
            # items = result.get('items', [])
            # all_snippets = [item.get('snippet', '') for item in items if item.get('snippet', '')]

            # if not all_snippets:
            #     insert_sentence(file_id, file_cursor['title'], page_num, sentence_index, sentence,
            #                     "yes" if references else "no", quotation_marks, [])
            #     sentence_index += 1
            #     continue

            # top_similarities = compare_sentences(sentence, all_snippets)
            # for _, idx in top_similarities:
            #     url = items[idx].get('link')
            #     snippet = all_snippets[idx]
            #     sentences = sentences_cache.get(url)

            #     if sentences is None:
            #         content = fetch_url(url)
            #         sentences_from_webpage = split_sentences(content)
            #         sentences = remove_sentences(sentences_from_webpage)
            #         sentences_cache[url] = sentences

            #     if sentences:
            #         snippet_parts = split_snippet(snippet)
            #         relevant_sentences = [s for s in sentences if check_snippet_in_sentence(s, snippet_parts)]
            #         if relevant_sentences:
            #             similarity_sentence, match_sentence, _ = compare_with_sentences(sentence, relevant_sentences)
            #             if similarity_sentence > dynamic_threshold:
            #                 parsed_url = urlparse(url)
            #                 domain = parsed_url.netloc.replace('www.', '')
            #                 school_id = school_cache.get(domain, current_school_id)
            #                 if domain not in school_cache:
            #                     school_cache[domain] = current_school_id
            #                     current_school_id += 1

            #                 positions = []
            #                 word_count_sml, paragraphs_best_math, paragraphs = common_ordered_words(match_sentence, sentence)

            #                 if word_count_sml > 3:
            #                     quads_sentence = page.search_for(sentence, quads=True)
            #                     for paragraph in paragraphs:
            #                         quads_token = page.search_for(paragraph, quads=True)
            #                         for qua_s in quads_sentence:
            #                             for qua_t in quads_token:
            #                                 if is_within(qua_t, qua_s):
            #                                     new_position = {
            #                                         "x_0": qua_t[0].x,
            #                                         "y_0": qua_t[0].y,
            #                                         "x_1": qua_t[-1].x,
            #                                         "y_1": qua_t[-1].y,
            #                                     }
            #                                     if not is_position(new_position, positions):
            #                                         positions.append(new_position)

            #                     best_match = wrap_paragraphs_with_color(paragraphs_best_math, match_sentence, school_id)
            #                     sources = source_append(sources, source_id, school_id, domain, url, "Internet",
            #                                             'no', 0, best_match, similarity_sentence,
            #                                             word_count_sml, paragraphs_best_math, positions)
            #                     source_id += 1

            if sources:
                best_source = max(sources, key=lambda x: x['highlight']['word_count_sml'])
                word_count_similarity += best_source['highlight']['word_count_sml']
                insert_sentence(file_id, file_cursor['title'], page_num, sentence_index, sentence,
                                "yes" if references else "no", quotation_marks, sources)
            else:
                insert_sentence(file_id, file_cursor['title'], page_num, sentence_index, sentence,
                                "yes" if references else "no", quotation_marks, [])

            sentence_index += 1
            
    plagiarism = word_count_similarity * 100 / word_count
    plagiarism = f"{plagiarism:.2f}"
    insert_file(file_cursor['school_id'], file_cursor['class_id'], file_cursor['assignment_id'],
                    file_id, file_cursor['title'], file_cursor['author_id'], "", file_cursor['submit_day'],
                    pdf_document.page_count, word_count, plagiarism, "",
                    file_cursor['storage'], file_cursor['quick_submit'], "checked", "checked", "checked",
                    "checked", "", "", "", 3)
    # Final processing for the document
    file_highlighted = highlight(file_id, ["student_Data", "Internet", "Ấn bản"])
    
    if file_highlighted:
        pdf_output_stream = io.BytesIO()
        file_highlighted.save(pdf_output_stream)
        file_highlighted.close()
        update_file_checked(file_id, Binary(pdf_output_stream.getvalue()))
        update_file(file_id, plagiarism)
        insert_file(file_cursor['school_id'], file_cursor['class_id'], file_cursor['assignment_id'],
                    file_id, file_cursor['title'], file_cursor['author_id'], "", file_cursor['submit_day'],
                    pdf_document.page_count, word_count, plagiarism, file_cursor['content_file'],
                    file_cursor['storage'], file_cursor['quick_submit'], "view_all", "", "", "", "", "", "", 0)

# import concurrent.futures
# import os
# cpu_cores = os.cpu_count()  
# # Run concurrently with multiple threads
# def run_concurrently(file_id):
#     with concurrent.futures.ThreadPoolExecutor(cpu_cores*3) as executor:
#         executor.map(main, file_id)

def run_concurrently(file_id):
    main(file_id)