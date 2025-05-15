import re
import spacy
import torch
from sentence_transformers import SentenceTransformer
import difflib
from sklearn.metrics.pairwise import cosine_similarity
from langdetect import detect
import fitz
import tempfile
import os
from pyvi.ViTokenizer import tokenize

# Load Vietnamese spaCy model
nlp = spacy.blank("vi")
nlp.add_pipe("sentencizer")
# Tăng giới hạn max_length
nlp.max_length = 2000000

def is_vietnamese(text):
    try:
        # Phát hiện ngôn ngữ của văn bản
        return detect(text) == 'vi'
    except:
        # Nếu có lỗi (ví dụ: văn bản quá ngắn), trả về False
        return False

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = SentenceTransformer('dangvantuan/vietnamese-embedding', device = device)
tokenizer = model.tokenizer

# def split_sentences(text):
#     vietnamese_lowercase = 'aáàảãạăắằẳẵặâấầẩẫậbcdđeéèẻẽẹêếềểễệfghiíìỉĩịjklmnoóòỏõọôốồổỗộơớờởỡợpqrstuúùủũụưứừửữựvxyýỳỷỹỵ'
#     text = re.sub(rf'\n(?=[{vietnamese_lowercase}])', ' ', text)

#     text = text.replace(' \n', '. ')
#     text = text.replace('\n', ' ')
#     text = re.sub(r'[ ]{2,}', ' ', text)
#     text = text.replace(' .', '.')
#     # text = re.sub(r'\.{2,}', '.', text)


#     abbreviations = ['TS.', 'Ths.', 'THS.',  'TP.', 'Dr.', 'PhD.', 'BS.', ' Th.', 'S.', 'PGS.', 'GS']

#     for abbr in abbreviations:
#         text = text.replace(abbr, abbr.replace('.', '__DOT__'))

#     sentences = re.split(r'[.!?]\s+', text)
#     sentences = [s.replace('__DOT__', '.') for s in sentences]
#     sentences = [s.strip() for s in sentences if s.strip()]

#     return sentences

abbreviations = ['1. ', '2. ', '3. ', '4. ', '5. ', '6. ', '7. ', '8. ', '9. ', '10. ', '11. ', '12. ', '13. ', '14. ', '15. ', '16. ', '17. ', '18. ', '19. ', '20. ', 'TS. ', 'Ths.', 'THS.',  'TP.', 'Dr.', 'PhD.', 'BS.', ' Th.', 'S.', 'PGS.', 'GS.']

def split_sentences(text):
    replacements = {}

    for word in abbreviations:
        safe_word = word.replace('.', '⸱')
        text = text.replace(word, safe_word)
        replacements[safe_word] = word

    result = []
    parts = re.split(r" \n \n", text)
    
    for part in parts:
        stripped_part = part.strip()
        if stripped_part != "":
            stripped_part = re.sub(r'\.{3,}\s*\d*', '.', stripped_part)
            sentences = re.split(r'[.!?]\s+', stripped_part)
            sentences = [re.sub(r'[.!?]+$', '', s.strip()) for s in sentences if s.strip()]
            for sentence in sentences:
                sentence_strip = sentence.strip()
                if sentence_strip != "":
                    sentence_strip = sentence_strip.replace(" \n", " ")
                    sentence_strip = sentence_strip.replace("\n", " ")
                    cleaned = sentence_strip
                    for safe, original in replacements.items():
                        cleaned = cleaned.replace(safe, original)

                    result.append(cleaned)

    return result



    
# def remove_sentences(sentences):
#     filtered_sentences = []
#     for sentence in sentences:
#         # Đếm số lượng tokens trong câu
#         # processed_sentences_text = preprocess_text_vietnamese(sentence)[0]
#         tokenizer_sent = tokenize(sentence)
#         o = model[0].tokenizer(tokenizer_sent, return_attention_mask=False, return_token_type_ids=False)
#         if len(o.input_ids) > 256:
#             sentences_split = re.split(r'[;,:-]', sentence)
#             sentences_split = [s.strip() for s in sentences_split if s.strip()]
#             for sentence_split in sentences_split:
#                 # processed_sentences_text_split = preprocess_text_vietnamese(sentence_split)[0]
#                 tokenizer_sent_split = tokenize(sentence)
#                 o_split = model[0].tokenizer(tokenizer_sent_split, return_attention_mask=False, return_token_type_ids=False)
#                 if 3 < len(o_split.input_ids) <= 256 and len(sentence_split.split()) > 3:
#                     filtered_sentences.append(sentence_split)
#         if 3 < len(o.input_ids) <= 256  and len(sentence.split()) > 3:
#             filtered_sentences.append(sentence)
#     return filtered_sentences

def remove_sentences(sentences):
    filtered_sentences = []

    for sentence in sentences:
        tokenized_sentence = tokenize(sentence)
        token_count = len(tokenizer.encode(tokenized_sentence, add_special_tokens=True))
        if 10 < token_count <= 256:
            filtered_sentences.append(sentence)
        elif token_count > 256:
            # Tách câu theo dấu :, -, ;
            parts = re.split(r'[:;\-]', sentence)
            for part in parts:
                part = part.strip()
                if part:
                    tokenized_part = tokenize(part)
                    part_token_count = len(tokenizer.encode(tokenized_part, add_special_tokens=True))
                    if 10 < part_token_count <= 256:
                        filtered_sentences.append(part)

    return filtered_sentences

def preprocess_text_vietnamese(text):
    doc = nlp(text)
    tokens = [token.text.lower() for token in doc if not token.is_stop and not token.is_punct]
    processed_text = ' '.join(tokens)
    return processed_text, tokens

def initialize_model_on_cpu():
    return SentenceTransformer('dangvantuan/vietnamese-embedding', device='cpu')



def embedding_vietnamese(text):
    global model
    try:
        tokenizer_sent = [tokenize(sent) for sent in text]
        embedding = model.encode(tokenizer_sent, normalize_embeddings=True)
        return embedding
    except Exception as e:
        if "CUDA error" in str(e):
            print("CUDA error detected. Resetting CUDA and switching to CPU.")
            torch.cuda.empty_cache() 
            model = initialize_model_on_cpu() 
        else:
            print(f"Error encoding text: {e}")
        return None 

def check_type_setence(sentence):
        # Kiểm tra câu có ngoặc kép
    match = re.search(r'“(.*?)”|"(.*?)"', sentence)

    last_word = sentence.split(" ")[-1]
    match_last_word = re.match(r'\d+', last_word[1:-1])
    if match:
        return "yes"
    else:
        if last_word.startswith("[") and last_word.endswith("]") and match_last_word:
            return "yes"
    return "no"

def clean_vietnamese_sentence(sentence):
    vietnamese_char_pattern = re.compile(
        r"[a-zA-ZĂÂÊÔƠƯÁÀẢÃẠẮẰẲẴẶẤẦẨẪẬĐÉÈẺẼẸẾỀỂỄỆÍÌỈĨỊÓÒỎÕỌỐỒỔỖỘỚỜỞỠỢÚÙỦŨỤỨỪỬỮỰÝỲỶỸỴăâđêôơưáàảãạắằẳẵặấầẩẫậđéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ\d\s;,:-]"
    )
    cleaned_sentence = ''.join(vietnamese_char_pattern.findall(sentence))
    cleaned_sentence = re.sub(r'\s+', ' ', cleaned_sentence).strip()
    return cleaned_sentence


def calculate_dynamic_threshold(length, max_threshold=0.9, min_threshold=0.75):
    if length < 10:
        return max_threshold
    elif length > 40:
        return min_threshold
    else:
        scaling_factor = (max_threshold - min_threshold) / (40 - 10)
        threshold = max_threshold - (length - 10) * scaling_factor
        return threshold
    
def clean_text(text):
    return re.findall(r'\w+|\W+', text) 

def count_common_words(sentence1, sentence2):
    def preprocess(sentence):
        sentence = sentence.lower()
        sentence = re.sub(r'[^\w\s]', '', sentence) 
        return sentence.split()

    words1 = preprocess(sentence1)
    words2 = preprocess(sentence2)

    common_count = sum(1 for word in words1 if word in words2)

    return common_count


def common_ordered_words(best_match, sentence):
    
    words_best_match = clean_text(best_match)
    words_sentence = clean_text(sentence)

    seq_matcher = difflib.SequenceMatcher(None, [w.lower() for w in words_best_match], [w.lower() for w in words_sentence])

    paragraphs_best_match = []  # Các đoạn giống nhau từ câu 1
    paragraphs_sentence = []    # Các đoạn giống nhau từ câu 2
    word_count_sml = 0          # Đếm số từ giống nhau

    current_paragraph_best_match = []
    current_paragraph_sentence = []
    last_end_index_best_match = -1
    last_end_index_sentence = -1

    for match in seq_matcher.get_matching_blocks():
        if match.size > 0:
            matched_words_best_match = words_best_match[match.a: match.a + match.size]
            matched_words_sentence = words_sentence[match.b: match.b + match.size]

            if len(current_paragraph_best_match) > 0 and match.a == last_end_index_best_match + 1 and match.b == last_end_index_sentence + 1:
                current_paragraph_best_match.extend(matched_words_best_match)
                current_paragraph_sentence.extend(matched_words_sentence)
            else:
                if current_paragraph_best_match:
                    paragraphs_best_match.append("".join(current_paragraph_best_match).strip())
                    paragraphs_sentence.append("".join(current_paragraph_sentence).strip())
                current_paragraph_best_match = matched_words_best_match
                current_paragraph_sentence = matched_words_sentence

            last_end_index_best_match = match.a + match.size - 1
            last_end_index_sentence = match.b + match.size - 1
            for word in matched_words_best_match:
                if re.match(r'\w+', word): 
                    word_count_sml += 1

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
    # paragraphs_similarity = []
    # for paragraphs in paragraphs_sentence:
    #     if paragraphs in sentence:
    #         paragraphs_similarity.append(paragraphs)
    #     else:
    #         print("tách chuỗi con nè")
    #         temp = ""
    #         for char in paragraphs:
    #             if char in sentence:
    #                 temp += char  # Xây dựng chuỗi tạm nếu ký tự tồn tại trong b
    #             else:
    #                 if temp:
    #                     paragraphs_similarity.append(temp)
    #                     temp = ""
    #         # Lưu chuỗi cuối cùng nếu còn dư
    #         if temp:
    #             paragraphs_similarity.append(temp)


            


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
    # preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    # preprocessed_references = [preprocess_text_vietnamese(snippet)[0] for snippet in all_snippets]
    all_sentences = [s for s in [sentence] + all_snippets if s.strip()]
    if len(all_sentences) <= 1:
        print("Error: Not enough valid sentences for comparison.")
        return []


    embeddings = embedding_vietnamese(all_sentences)
    if embeddings is not None and embeddings.any():
        similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:])

        if similarity_scores.shape[1] == 0:
            print("Error: Similarity scores could not be computed.")
            return []

        sorted_indices = similarity_scores[0].argsort()[::-1]
        top_indices = sorted_indices[:3] 
        top_scores = similarity_scores[0][top_indices]

        top_similarities = [(top_scores[i], top_indices[i]) for i in range(len(top_indices))]
        return top_similarities
    return []



def compare_with_sentences(sentence, sentences):
    # preprocessed_query, _ = preprocess_text_vietnamese(sentence)
    # preprocessed_references = [preprocess_text_vietnamese(ref)[0] for ref in sentences]


    all_sentences = [sentence] + sentences
    if len(all_sentences) > 2:
        embeddings = embedding_vietnamese(all_sentences)
        if embeddings is not None and embeddings.any():
            similarity_scores = calculate_similarity(embeddings[0:1], embeddings[1:])

            if similarity_scores.shape[1] == 0:
                return 0, "", -1

            max_similarity_idx = similarity_scores.argmax()
            max_similarity = similarity_scores[0][max_similarity_idx]
            best_match = sentences[max_similarity_idx]
            return max_similarity, best_match, max_similarity_idx
        return 0, "", -1
    return 0, "", -1


def check_snippet_in_sentence(sentence, snippet_parts):
    return any(part in sentence for part in snippet_parts)

def extract_phrases(sentence, n=3):
    words = sentence.split()
    phrases = []
    if len(words) < n:
        return phrases
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

def extract_pdf_text(pdf_path):
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(pdf_path.read()) 
        temp_file_path = temp_file.name

    doc = fitz.open(temp_file_path)
    text = ""
    for page in doc:
        page_text = page.get_text()
        text += page_text
    doc.close()

    os.remove(temp_file_path)

    return text
