from app.extensions import es
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError, TransportError
from app.models.search_system.models import cluster_remote

clusters = cluster_remote()
index = ''
for cluster in clusters:
    index = index + cluster[0] + ':' + cluster[1] + ','
if index.endswith(','):
    index = index[:-1] 

def search_top10_vector_elastic(vector_sentence):
    search_body = {
        "size": 10,
        "query": {
            "script_score": {
                "query": {
                    "match_all": {}
                },
                "script": {
                    "source": """
                        cosineSimilarity(params.query_vector, 'vector') + 1.0
                    """,
                    "params": {
                        "query_vector": vector_sentence
                    }
                }
            }
        }
    }


    # res = es.search(index="plagiarism_vector", body=search_body)
    res = es.search(index=index, body=search_body)

    sentence_results = [] 

    for hit in res['hits']['hits']:
        score = hit['_score']
        school_id = hit['_source']['school_id']
        school_name = hit['_source']['school_name']
        file_id = hit['_source']['file_id']
        file_name = hit['_source']['file_name']
        sentence = hit['_source']['sentence']
        type = hit['_source']['type']
        result_info = {
            'school_id': school_id,
            'school_name': school_name,
            'file_id': file_id,
            'file_name': file_name,
            'sentence': sentence,
            'score': score,
            'type':type
        }
        sentence_results.append(result_info)


    return sentence_results



def save_to_elasticsearch(ip_cluster, processed_sentences, vectors, school_id, school_name, file_id, file_name, index_name, type):
    # Kết nối tới Elasticsearch
    print(ip_cluster)
    es_school = Elasticsearch([ip_cluster], timeout=300) 
    for i, sentence in enumerate(processed_sentences):
        document = {
            'school_id': school_id,
            'school_name': school_name,
            'file_id': file_id,
            'file_name': file_name,
            'sentence': sentence,
            'vector': vectors[i],
            'type': type
        }
        # Lưu tài liệu vào Elasticsearch
        es_school.index(index=index_name, document=document)

def delete_by_file_id(ip_cluster, file_id, index_name):
    try:
        es_school = Elasticsearch([ip_cluster], timeout=10000)
        
        query = {
            "query": {
                "match": {
                    "file_id": file_id
                }
            }
        }
        
        response = es_school.delete_by_query(index=index_name, body=query)
        return response
    
    except (ConnectionError, TransportError) as e:
        print(f"Lỗi kết nối hoặc giao thức: {e}")
        return None
    except Exception as e:
        print(f"Lỗi khác: {e}")
        return None