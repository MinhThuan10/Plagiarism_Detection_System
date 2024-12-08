import re

def count_common_words(sentence1, sentence2):
    def preprocess(sentence):
        sentence = sentence.lower()
        sentence = re.sub(r'[^\w\s]', '', sentence) 
        return sentence.split()

    words1 = preprocess(sentence1)
    words2 = preprocess(sentence2)

    common_count = sum(1 for word in words1 if word in words2)

    return common_count

# Ví dụ sử dụng
sentence1 = "Bộ chuyển đổi là một loại kiến trúc mạng nơ-ron có khả năng biến đổi hoặc thay đổi một trình tự đầu vào thành một trình tự đầu ra"
sentence2 = "Transformer là một loại kiến trúc mạng nơ-ron có khả năng biến đổi hoặc thay đổi một trình tự đầu vào thành một trình tự đầu ra"

sentences = [
    
]
result = count_common_words(sentence1, sentence2)
sentence1_word_count = len(re.findall(r'\w+', sentence1))
similarity_ratio = result / sentence1_word_count

print(f"Số từ giống nhau: {result}")
print(f"Số từ trong câu: {sentence1_word_count}")
print(f"Tỉ lệ: {similarity_ratio}")
