import requests
import io
import fitz  # PyMuPDF
from io import BytesIO
from docx import Document
from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
from config import Config


# Khởi tạo API Key hiện tại
# Biến toàn cục
current_api_key_index = 0
current_list = 1  

def get_current_api_key():
    """Trả về API Key hiện tại."""
    global current_list, current_api_key_index

    # Kiểm tra giá trị của current_list và trả về API Key từ danh sách tương ứng
    if current_list == 1:
        # Kiểm tra nếu còn key trong API_KEYS
        if current_api_key_index < len(Config.API_KEYS):
            return Config.API_KEYS[current_api_key_index]
    elif current_list == 2:
        # Kiểm tra nếu còn key trong API_KEYS2
        if current_api_key_index < len(Config.API_KEYS2):
            return Config.API_KEYS2[current_api_key_index]
    elif current_list == 3:
        # Kiểm tra nếu còn key trong API_KEYS3
        if current_api_key_index < len(Config.API_KEYS3):
            return Config.API_KEYS3[current_api_key_index]
    elif current_list == 4:
        # Kiểm tra nếu còn key trong API_KEYS4
        if current_api_key_index < len(Config.API_KEYS4):
            return Config.API_KEYS4[current_api_key_index]
    
    # Nếu không có key hợp lệ hoặc đã hết, trả về None
    return None

def get_next_api_key():
    """Chuyển sang API Key tiếp theo, và chuyển danh sách khi hết key."""
    global current_api_key_index, current_list
    current_api_key_index += 1

    # Kiểm tra nếu danh sách hiện tại hết API Key
    if current_list == 1 and current_api_key_index >= len(Config.API_KEYS):
        # Chuyển sang danh sách API_KEYS2
        current_list = 2
        current_api_key_index = 0  # Reset lại index cho API_KEYS2
    elif current_list == 2 and current_api_key_index >= len(Config.API_KEYS2):
        # Chuyển sang danh sách API_KEYS2
        current_list = 3
        current_api_key_index = 0  # Reset lại index cho API_KEYS2
    elif current_list == 3 and current_api_key_index >= len(Config.API_KEYS3):
        # Chuyển sang danh sách API_KEYS2
        current_list = 4
        current_api_key_index = 0  # Reset lại index cho API_KEYS2
    elif current_list == 4 and current_api_key_index >= len(Config.API_KEYS4):
        return None  # Đã dùng hết cả hai danh sách

    return get_current_api_key()



def search_google(query):
    """Tìm kiếm Google với các API Key, chuyển sang key tiếp theo khi gặp lỗi 403 hoặc 429."""
    global current_api_key_index, current_list
    while True:
        api_key = get_current_api_key()
        
        if api_key is None:
            print("Đã hết tất cả API Key.")
            return {}  # Trả về rỗng khi không còn API Key khả dụng
        
        # Chọn CX tương ứng với danh sách API
        if current_list == 1:
            cx = Config.CX
        elif current_list == 2:
            cx = Config.CX2
        elif current_list == 3:
            cx = Config.CX3
        else:
            cx = Config.CX4

        url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cx}"
        response = requests.get(url, verify=False)
        
        if response.status_code == 200:
            return response.json()  # Trả về dữ liệu khi thành công
        
        elif response.status_code in [403, 429]:
            print(f"API Key {api_key} gặp lỗi {response.status_code}. Chuyển sang key khác.")
            api_key = get_next_api_key()  # Chuyển sang API Key tiếp theo
            
            if api_key is None:
                print("Không còn API Key nào khả dụng.")
                return {}  # Trả về rỗng nếu không còn API Key
            
        else:
            print(f"Yêu cầu không thành công với API Key {api_key}. Mã lỗi: {response.status_code}")
            return {}
        
def fetch_response(url):
    try:
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        return response
    except (requests.exceptions.RequestException, TimeoutError) as e:
        print(f"Error accessing {url}: {e}")
        return None
    
def extract_text_from_pdf(response):
    try:
        pdf_source = io.BytesIO(response.content)  # Sử dụng .content để lấy dữ liệu dạng bytes
        with fitz.open(stream=pdf_source, filetype='pdf') as document:
            # Sử dụng vòng lặp đơn để xử lý từng trang
            text_parts = []
            for page in document:
                text_parts.append(page.get_text("text"))
            pdf_text = ''.join(text_parts)
    except Exception as e:
        print(f"Lỗi khi xử lý PDF: {e}")
        return ""
    return pdf_text  


def fetch_docx(response):
    try:
        doc_file = BytesIO(response.content)
        doc = Document(doc_file)
        return '\n'.join(para.text for para in doc.paragraphs)
    except Exception as e:
        print(f"Lỗi khi xử lý DOCX: {e}")
        return ""

def fetch_csv(response):
    try:
        csv_content = StringIO(response.content.decode('utf-8'))
        df = pd.read_csv(csv_content)
        return df.to_string()  # Trả về dữ liệu CSV dưới dạng chuỗi
    except Exception as e:
        print(f"Lỗi khi xử lý CSV: {e}")
        return ""   

def extract_text_from_html(response):
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        if soup.body:
            # Lấy tất cả nội dung hiển thị trên trang web từ thẻ <body>
            body_content = soup.body.get_text(separator='\n', strip=True)
        elif soup.html:  # Nếu không có <body>, thử lấy nội dung từ thẻ <html>
            body_content = soup.html.get_text(separator='\n', strip=True)
        else:
            # Nếu không có <body> hoặc <html>, trả về chuỗi rỗng hoặc thông báo lỗi
            body_content = ""
        return body_content
    except Exception as e:
        print(f"Lỗi khi xử lý HTML: {e}")
        return ""

def fetch_url(url):
    response = fetch_response(url)
    if not response:
        return ""
    
    content_type = response.headers.get('Content-Type', '').lower()

    if 'application/pdf' in content_type:
        return extract_text_from_pdf(response)
    elif 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' in content_type:
        return fetch_docx(response)
    elif 'text/csv' in content_type:
        return fetch_csv(response)
    else:
        return extract_text_from_html(response)



