import fitz
from app.models.search_system.models import retrieve_pdf_from_mongodb, get_best_sources, update_school_stt, get_sources

def is_within(qua_t, qua_s):
    if (qua_t[0].x >= qua_s[0].x and qua_t[0].y == qua_s[0].y and qua_t[-1].x <= qua_s[-1].x and qua_t[-1].y == qua_s[-1].y):
        return True
    else:
        return False
    
def is_position(new_position, positions):
    for position in positions:
        if (new_position['y_0'] >= position['y_0'] - 5 and new_position['y_1'] <= position['y_1'] + 5):
            if (new_position['x_0'] <= position['x_0'] and new_position['x_1'] >= position['x_1']):
                position['x_0'] = new_position['x_0']
                position['x_1'] = new_position['x_1']
                return True
            if (new_position['x_0'] <= position['x_0'] and new_position['x_1'] >= position['x_0'] - 15): #1
                position['x_0'] = new_position['x_0']
                return True
 
            if (new_position['x_0'] >= position['x_0'] - 5 and new_position['x_1'] <= position['x_1'] + 5): #2
                return True

            if (new_position['x_0'] >= position['x_0'] and new_position['x_0'] <= position['x_1'] + 15): #3
                position['x_1'] = new_position['x_1']
                return True
    
    # if (new_position['x_0'] + 20 >= new_position['x_1']):
    #     return True

    return False
def should_merge(pos1, pos2):
    # Check if positions overlap or are adjacent on the x-axis
    return not (pos1["x_1"] < pos2["x_0"] or pos1["x_0"] > pos2["x_1"])


color_hex = [
    '#FFE8EA', '#E0E0E0', '#D0C2FF', '#96EEF6', '#FFF5C4'
]

color_rbg = [(1, 0.91, 0.92), (0.88, 0.88, 0.88), (0.82, 0.76, 1), (0.59, 0.93, 0.96), (1, 0.96, 0.77)]

def wrap_paragraphs_with_color(paragraphs, best_match, school_id):
    color_index = school_id % len(color_hex)
    color = color_hex[color_index]

    highlighted_text = best_match
    for paragraph in paragraphs:
        highlighted_text = highlighted_text.replace(paragraph, f'<span style="background-color:{color};">{paragraph}</span>')

    return highlighted_text

def source_append(sources, source_id, school_id, school_name, file_id_source, type, excepted, school_stt, best_match, score, word_count_sml, paragraphs_best_math, positions):
    color_index = school_id % len(color_hex)
    sources.append({
                "source_id":source_id,
                "school_id": school_id,
                "school_name": school_name,
                "file_id": file_id_source,
                "type_source": type, 
                "except": excepted,
                "color": color_hex[color_index],
                "school_stt": school_stt,
                "best_match": best_match,
                "score": float(score),
                "highlight": {
                    "word_count_sml": word_count_sml,
                    "paragraphs": paragraphs_best_math,
                    "position": positions
                }
            })
    return sources

                
def add_highlight_to_page(page, x0, y0, x1, y1, color, school_stt, highlighted_positions, page_num):
    """
    Thêm chú thích nổi bật vào trang PDF tại vùng xác định bởi các tọa độ với màu sắc cụ thể.
    
    Args:
    page (fitz.Page): Đối tượng trang PDF.
    x0 (float): Tọa độ x của góc trên bên trái.
    y0 (float): Tọa độ y của góc trên bên trái.
    x1 (float): Tọa độ x của góc dưới bên phải.
    y1 (float): Tọa độ y của góc dưới bên phải.
    color (tuple): Màu sắc dưới dạng (R, G, B).
    """
    
from collections import defaultdict
import fitz  # PyMuPDF

def highlight(file_id, type_source):
    # Khởi tạo defaultdict với 'highlighted' là set và 'text' là dict
    highlighted_positions = defaultdict(lambda: {'highlighted': set(), 'text': {}})

    update_school_stt(file_id, "best_source", type_source)
    best_sources = get_best_sources(file_id, type_source)
    pdf_binary = retrieve_pdf_from_mongodb(file_id)

    if pdf_binary is None:
        print("Không tìm thấy file PDF trong MongoDB.")
        return

    # Mở file PDF từ dữ liệu nhị phân
    pdf_stream = fitz.open(stream=pdf_binary, filetype='pdf')
    
    for source in best_sources:
        page_num = source.get('page', None)
        positions = source['highlight'].get('position', None)
        school_id = source['school_id']
        school_stt = source['school_stt']
        
        color_index = school_id % len(color_rbg)  
        color = color_rbg[color_index]

        if page_num is not None and positions:
            page = pdf_stream.load_page(page_num)

            for position in positions:
                x_0 = position.get('x_0')
                y_0 = position.get('y_0')
                x_1 = position.get('x_1')
                y_1 = position.get('y_1')
                
                # Chuyển vùng đánh dấu thành tuple để sử dụng làm key trong dictionary
                position_tuple = (x_0, y_0, x_1, y_1)
                
                # Kiểm tra nếu vùng đã được đánh dấu chưa
                if position_tuple not in highlighted_positions[page_num]['highlighted']:
                    try:
                        highlight = page.add_highlight_annot(fitz.Rect(x_0, y_0, x_1, y_1))
                        highlight.set_colors(stroke=color)
                        highlight.update()
                        
                        text_position = (10, y_0 + 10)
                        text = str(school_stt)
                        font_size = 12

                        # Kiểm tra nếu vị trí chưa có văn bản nào
                        if text_position not in highlighted_positions[page_num]['text']:
                            page.insert_text(text_position, text, fontsize=font_size, fontname="helv", color=color)
                            highlighted_positions[page_num]['text'][text_position] = [text]
                        else:
                            # Kiểm tra nếu văn bản đã tồn tại trong danh sách tại vị trí này
                            if text not in highlighted_positions[page_num]['text'][text_position]:
                                new_x_position = text_position[0] + len(" ".join(highlighted_positions[page_num]['text'][text_position])) * font_size * 0.5
                                new_text_position = (new_x_position, text_position[1])
                                page.insert_text(new_text_position, text, fontsize=font_size, fontname="helv", color=color)
                                highlighted_positions[page_num]['text'][new_text_position] = [text]

                        # Ghi nhận vùng đã đánh dấu
                        highlighted_positions[page_num]['highlighted'].add(position_tuple)
                    except ValueError as e:
                        print(f"Lỗi khi thêm highlight: {e}, tọa độ: {x_0}, {y_0}, {x_1}, {y_1}")
                        print(page_num)
                        print(source['best_match'])


    return pdf_stream

def highlight_school(file_id, school_id, type_source):
    # Khởi tạo defaultdict với 'highlighted' là set và 'text' là dict
    highlighted_positions = defaultdict(lambda: {'highlighted': set(), 'text': {}})

    update_school_stt(file_id, "view_all", type_source)
    best_sources = get_sources(file_id, type_source)
    pdf_binary = retrieve_pdf_from_mongodb(file_id)

    if pdf_binary is None:
        print("Không tìm thấy file PDF trong MongoDB.")
        return
    # Mở file PDF từ dữ liệu nhị phân
    pdf_stream = fitz.open(stream=pdf_binary, filetype='pdf')
    for source in best_sources:
        if source['school_id'] == int(school_id):
            page_num = source['page']
            positions = source['highlight']['position']
            school_id = source['school_id']
            school_stt = source['school_stt']
            
            color_index = school_id % len(color_rbg)  
            color = color_rbg[color_index]

            if page_num is not None and positions:
                page = pdf_stream.load_page(page_num)

                for position in positions:
                    x_0 = position.get('x_0')
                    y_0 = position.get('y_0')
                    x_1 = position.get('x_1')
                    y_1 = position.get('y_1')
                    
                    # Chuyển vùng đánh dấu thành tuple để sử dụng làm key trong dictionary
                    position_tuple = (x_0, y_0, x_1, y_1)
                    
                    # Kiểm tra nếu vùng đã được đánh dấu chưa
                    if position_tuple not in highlighted_positions[page_num]['highlighted']:
                        try:
                            highlight = page.add_highlight_annot(fitz.Rect(x_0, y_0, x_1, y_1))
                            highlight.set_colors(stroke=color)
                            highlight.update()
                            
                            text_position = (10, y_0 + 10)
                            text = str(school_stt)
                            font_size = 12

                            # Kiểm tra nếu vị trí chưa có văn bản nào
                            if text_position not in highlighted_positions[page_num]['text']:
                                page.insert_text(text_position, text, fontsize=font_size, fontname="helv", color=color)
                                highlighted_positions[page_num]['text'][text_position] = [text]
                            else:
                                # Kiểm tra nếu văn bản đã tồn tại trong danh sách tại vị trí này
                                if text not in highlighted_positions[page_num]['text'][text_position]:
                                    new_x_position = text_position[0] + len(" ".join(highlighted_positions[page_num]['text'][text_position])) * font_size * 0.5
                                    new_text_position = (new_x_position, text_position[1])
                                    page.insert_text(new_text_position, text, fontsize=font_size, fontname="helv", color=color)
                                    highlighted_positions[page_num]['text'][new_text_position] = [text]

                            # Ghi nhận vùng đã đánh dấu
                            highlighted_positions[page_num]['highlighted'].add(position_tuple)
                        except ValueError as e:
                            print(f"Lỗi khi thêm highlight: {e}, tọa độ: {x_0}, {y_0}, {x_1}, {y_1}")
                            print(page_num)
                            print(source['best_match'])


    return pdf_stream