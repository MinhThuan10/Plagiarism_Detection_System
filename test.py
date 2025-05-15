from sentence_transformers import SentenceTransformer
from pyvi.ViTokenizer import tokenize

# Câu đầu vào
# Tách từ bằng ViTokenizer

# Load model và tokenizer
model = SentenceTransformer('dangvantuan/vietnamese-embedding')
tokenizer = model.tokenizer

for n in range(100, 550, 2):
    dummy_sentence = "từ " * n
    tokenized = tokenize(dummy_sentence)
    tokens = tokenizer.encode(tokenized, add_special_tokens=True)
    try:
        emb = model.encode(tokenized)
        print(f"{n} từ → {len(tokens)} token → OK")
    except Exception as e:
        print(f"{n} từ → {len(tokens)} token → LỖI: {e}")
