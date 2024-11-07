import re
import spacy
import torch
from sentence_transformers import SentenceTransformer
import difflib
from sklearn.metrics.pairwise import cosine_similarity

# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
nlp.add_pipe("sentencizer")
# Tăng giới hạn max_length
nlp.max_length = 2000000


def split_sentences(text):
    combined_sentences = []
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', '', text)
    text = text.replace('. ', '.\n')
    
    lines = text.split('\n')
    for line in lines:
        sentences = re.split(r'[.?!]\s+', line)
        for sentence in sentences:
            sentence = sentence.strip()
            sentences = [s.strip() for s in sentences if s.strip()]
            if sentence:
                combined_sentences.append(sentence)

    return combined_sentences

def remove_sentences(sentences):
    return [sentence for sentence in sentences if(len(sentence.split()) > 2 and len(sentence.split()) < 100)]

def preprocess_text_vietnamese(text):
    # Process text with spaCy pipeline
    doc = nlp(text)
    # Filter out stopwords and punctuation, and convert to lowercase
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    # Join tokens back into a single string
    processed_text = ' '.join(tokens)
    return processed_text, tokens


device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# Tải mô hình và chuyển sang GPU (nếu có)
model = SentenceTransformer('dangvantuan/vietnamese-embedding', device = device)
def embedding_vietnamese(text):
    embedding = model.encode(text)
    return embedding


def check_type_setence(sentence):
        # Kiểm tra câu có ngoặc kép
    match = re.search(r'“(.*?)”|"(.*?)"', sentence)
    if match:
        return "yes"
    
    return "no"

def calculate_dynamic_threshold(length, max_threshold=0.8, min_threshold=0.6):
    if length < 10:
        return max_threshold
    elif length > 40:
        return min_threshold
    else:
        scaling_factor = (max_threshold - min_threshold) / (40 - 10)
        threshold = max_threshold - (length - 10) * scaling_factor
        return threshold
    

def common_ordered_words(best_match, sentence):
    # Tách từ và ký tự đặc biệt nhưng giữ nguyên khoảng trắng và dấu câu
    def clean_text(text):
        return re.findall(r'\w+|\W+', text)  # Giữ dấu câu và khoảng trắng

    words_best_match = clean_text(best_match)
    words_sentence = clean_text(sentence)

    # Tạo SequenceMatcher để tìm các đoạn từ giống nhau (không phân biệt chữ hoa, chữ thường)
    seq_matcher = difflib.SequenceMatcher(None, [w.lower() for w in words_best_match], [w.lower() for w in words_sentence])

    paragraphs_best_match = []  # Các đoạn giống nhau từ câu 1
    paragraphs_sentence = []    # Các đoạn giống nhau từ câu 2
    word_count_sml = 0          # Đếm số từ giống nhau

    current_paragraph_best_match = []
    current_paragraph_sentence = []
    last_end_index_best_match = -1
    last_end_index_sentence = -1

    # Duyệt qua các khối trùng khớp (matching blocks)
    for match in seq_matcher.get_matching_blocks():
        if match.size > 0:
            # Lấy các từ trùng khớp từ hai câu
            matched_words_best_match = words_best_match[match.a: match.a + match.size]
            matched_words_sentence = words_sentence[match.b: match.b + match.size]

            # Kiểm tra xem các từ có liền kề nhau không
            if len(current_paragraph_best_match) > 0 and match.a == last_end_index_best_match + 1 and match.b == last_end_index_sentence + 1:
                # Nếu từ khớp là liên tiếp, nối thêm vào đoạn hiện tại
                current_paragraph_best_match.extend(matched_words_best_match)
                current_paragraph_sentence.extend(matched_words_sentence)
            else:
                # Nếu không liên tiếp, lưu đoạn hiện tại và bắt đầu một đoạn mới
                if current_paragraph_best_match:
                    paragraphs_best_match.append("".join(current_paragraph_best_match).strip())
                    paragraphs_sentence.append("".join(current_paragraph_sentence).strip())
                current_paragraph_best_match = matched_words_best_match
                current_paragraph_sentence = matched_words_sentence

            # Cập nhật chỉ số và đếm số từ thực sự trùng khớp (bỏ qua dấu câu)
            last_end_index_best_match = match.a + match.size - 1
            last_end_index_sentence = match.b + match.size - 1
            for word in matched_words_best_match:
                if re.match(r'\w+', word):  # Chỉ đếm từ thực sự (bỏ qua dấu câu)
                    word_count_sml += 1

    # Thêm đoạn cuối cùng vào kết quả
    if current_paragraph_best_match:
        paragraphs_best_match.append("".join(current_paragraph_best_match).strip())
        paragraphs_sentence.append("".join(current_paragraph_sentence).strip())
    
    unique_paragraphs_best_match = set()
    unique_paragraphs_sentence = set()
    paragraphs_best_match = [
        p for p in paragraphs_best_match 
        if p and re.search(r'\w', p) and p not in unique_paragraphs_best_match and not unique_paragraphs_best_match.add(p)
    ]

    paragraphs_sentence = [
        p for p in paragraphs_sentence 
        if p and re.search(r'\w', p) and p not in unique_paragraphs_sentence and not unique_paragraphs_sentence.add(p)
    ]

    return word_count_sml, paragraphs_best_match, paragraphs_sentence

def calculate_similarity(query_features, reference_features):
    if query_features.shape[1] != reference_features.shape[1]:
        reference_features = reference_features.T
    
    if query_features.shape[1] != reference_features.shape[1]:
        raise ValueError("Incompatible dimensions for query and reference features")
    
    similarity_scores = cosine_similarity(query_features, reference_features)
    return similarity_scores

def calculate_similarity(query_features, reference_features):
    if query_features.shape[1] != reference_features.shape[1]:
        reference_features = reference_features.T
    
    if query_features.shape[1] != reference_features.shape[1]:
        raise ValueError("Incompatible dimensions for query and reference features")
    
    similarity_scores = cosine_similarity(query_features, reference_features)
    return similarity_scores

def compare_sentences(sentence, all_snippets):
    # Tiền xử lý câu và các snippet
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(snippet)[0] for snippet in all_snippets]  
    all_sentences = [preprocessed_query] + preprocessed_references
    embeddings = embedding_vietnamese(all_sentences) 
    # Tính toán độ tương đồng cosine giữa câu và các snippet
    similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:]) 
    # Sắp xếp điểm số tương đồng và chỉ số của các snippet
    sorted_indices = similarity_scores[0].argsort()[::-1]
    top_indices = sorted_indices[:3]
    top_scores = similarity_scores[0][top_indices]
    # Trả về ba điểm số độ tương đồng cao nhất và các chỉ số tương ứng
    top_similarities = [(top_scores[i], top_indices[i]) for i in range(len(top_indices))]
    return top_similarities

def compare_with_sentences(sentence, sentences):
    preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences]

    all_sentences = [preprocessed_query] + preprocessed_references
    embeddings = embedding_vietnamese(all_sentences) 
    # Tính toán độ tương đồng cosine giữa câu và các snippet
    similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:]) 
    
    if similarity_scores.shape[1] == 0:
        return 0, "", -1
    
    max_similarity_idx = similarity_scores.argmax()
    max_similarity = similarity_scores[0][max_similarity_idx]
    best_match = sentences[max_similarity_idx]
    return max_similarity, best_match, max_similarity_idx


def check_snippet_in_sentence(sentence, snippet_parts):
    # Kiểm tra xem câu có chứa bất kỳ phần nào của snippet hay không
    return any(part in sentence for part in snippet_parts)

def extract_phrases(sentence, n=3):
    # Tách câu thành các từ
    words = sentence.split()
    # Danh sách để lưu các cụm từ
    phrases = []
    
    # Nếu số từ ít hơn n, không thể tạo cụm từ
    if len(words) < n:
        return phrases
    
    # Tạo các cụm từ với khoảng n từ
    for i in range(0, len(words), n):
        phrase = ' '.join(words[i:i + n])
        phrases.append(phrase)
    
    return phrases

def split_snippet(text):
    combined_sentences = []
    vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', ' ', text)
    text = re.sub(r'[^\w\s.,;?:!]', ' ', text)
    text = re.sub(r'\.{2,}', '.', text)
    text = re.sub(r'\ {2,}', ' ', text)
    text = re.sub(r' \r', '', text)
    text = text.replace('. ', '.\n')
    
    lines = text.split('\n')
    for line in lines:
            sentences = re.split(r'[.?!]\s+', line)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence:
                    # Tách câu thành các cụm từ
                    phrases = extract_phrases(sentence, n=2)
                    for phrase in phrases:
                        if len(phrase.split()) > 1:
                            combined_sentences.append(phrase)

    return combined_sentences

