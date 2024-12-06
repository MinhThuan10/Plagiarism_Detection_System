import re

sentence = "This is a test sentence [1]"

# Kiểm tra phần tử cuối cùng có phải là "[x]" và x là số hay không
last_word = sentence.split(" ")[-1]
match = re.match(r'\d+', last_word[1:-1])  # Tìm số trong dấu ngoặc vuông

if last_word.startswith("[") and last_word.endswith("]") and match:
    print("Đúng, phần tử cuối cùng là '[x]' và x là một số.")
else:
    print("Sai, phần tử cuối cùng không phải là '[x]' hoặc x không phải là một số.")
