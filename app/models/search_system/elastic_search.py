from app.extensions import es

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

    res = es.search(index="plagiarism_vector", body=search_body)
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