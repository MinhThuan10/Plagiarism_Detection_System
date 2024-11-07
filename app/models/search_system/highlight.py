import fitz
from app.models.search_system.models import retrieve_pdf_from_mongodb, get_best_sources, update_school_stt

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
   
    return False
def should_merge(pos1, pos2):
    # Check if positions overlap or are adjacent on the x-axis
    return not (pos1["x_1"] < pos2["x_0"] or pos1["x_0"] > pos2["x_1"])


color_hex = [
    '#FFB3BA', '#FF677D', '#D4A5A5', '#392F5A', '#31A2AC',
    '#61C0BF', '#6B4226', '#D9BF77', '#ACD8AA', '#FFE156',
    '#6B5B95', '#AB83A1', '#FF6F61', '#F5B041', '#F8CBA6',
    '#FFEBB0', '#EAB8E4', '#BBE4E7', '#F3C6C4', '#F9AFAF',
    '#FFB2D1', '#FBBF8A', '#D8E9A8', '#A4D7E1', '#D5AAFF',
    '#FFC3A0', '#B9FBC0', '#D9BF77', '#D7C9BF', '#A2A2F4',
    '#F5CBA1', '#D1C6E7', '#B6E3F4', '#B3D4FF', '#F1B6C1',
    '#B7E4C7', '#D7D5FF', '#FFB3E6', '#A6B6D4', '#F4D5C4',
    '#F5B941', '#EAE2B7', '#FFD166', '#00BFFF', '#E2E2D5',
    '#FFC4D6', '#A3D9FF', '#C3DA2D', '#FF7B00', '#F7B2A2',
    '#D2B2C3', '#F4D6A0', '#C2C2D6', '#FF758F', '#B6F5A2',
    '#C3C5C1', '#FFD6E8', '#FFE4B5', '#A9DAD6', '#D8A7D7',
    '#FFE156', '#F0EBD8', '#FF686B', '#C9C9FF', '#F2C8E6',
    '#FFBAC0', '#F1B6D1', '#FFB5D8', '#C8B5B5', '#E8CFCF',
    '#C1C2B8', '#C2E2D5', '#F7F5A0', '#F7B0D9', '#F8B9A8',
    '#FFCEFF', '#A1D5E4', '#B1B1E2', '#F8A3C6', '#F9FBB2',
    '#FFE156', '#F3D08A', '#FFC3C5', '#DAE1E7', '#BFDCE5',
    '#FFD5B5', '#F5D6D2', '#D6D5C9', '#E4D8DB', '#D1D5DA',
    '#B6E5B2', '#F4D8A5', '#F7C0D4', '#FFACB7', '#F8A7D2',
    '#FFC1A8', '#F8BCE9', '#D6A1B8', '#FFB3B3', '#FFC9B1',
    '#D4F0C8', '#B6A5D1', '#D6C6C1', '#F7A0B5', '#D6E6D5',
    '#D6A4E5', '#F1D9BF', '#F8A0A1', '#B3D1B7', '#D6C6C6',
    '#FFCB85', '#FFCDA2', '#FFD1C0', '#B1E9E1', '#F8F4A7',
    '#FFB3B3', '#D9D0D0', '#B8E8C3', '#F8B8B8', '#B9A6F5',
]

color_rbg = [(1.0, 0.7019607843137254, 0.7294117647058823), (1.0, 0.403921568627451, 0.49019607843137253), (0.8313725490196079, 0.6470588235294118, 0.6470588235294118), (0.2235294117647059, 0.1843137254901961, 0.35294117647058826), (0.19215686274509805, 0.6352941176470588, 0.6745098039215687), (0.3803921568627451, 0.7529411764705882, 0.7490196078431373), (0.4196078431372549, 0.25882352941176473, 0.14901960784313725), (0.8509803921568627, 0.7490196078431373, 0.4666666666666667), 
             (0.6745098039215687, 0.8470588235294118, 0.6666666666666666), (1.0, 0.8823529411764706, 0.33725490196078434), (0.4196078431372549, 0.3568627450980392, 0.5843137254901961), (0.6705882352941176, 0.5137254901960784, 0.6313725490196078), (1.0, 0.43529411764705883, 0.3803921568627451), (0.9607843137254902, 0.6901960784313725, 0.2549019607843137), (0.9725490196078431, 0.796078431372549, 0.6509803921568628), (1.0, 0.9215686274509803, 0.6901960784313725),
            (0.9176470588235294, 0.7215686274509804, 0.8941176470588236), (0.7333333333333333, 0.8941176470588236, 0.9058823529411765), (0.9529411764705882, 0.7764705882352941, 0.7686274509803922), (0.9764705882352941, 0.6862745098039216, 0.6862745098039216), (1.0, 0.6980392156862745, 0.8196078431372549), (0.984313725490196, 0.7490196078431373, 0.5411764705882353), (0.8470588235294118, 0.9137254901960784, 0.6588235294117647), 
            (0.6431372549019608, 0.8431372549019608, 0.8823529411764706), (0.8352941176470589, 0.6666666666666666, 1.0), (1.0, 0.7647058823529411, 0.6274509803921569), (0.7254901960784313, 0.984313725490196, 0.7529411764705882), (0.8509803921568627, 0.7490196078431373, 0.4666666666666667), (0.8431372549019608, 0.788235294117647, 0.7490196078431373), (0.6352941176470588, 0.6352941176470588, 0.9568627450980393), (0.9607843137254902, 0.796078431372549, 0.6313725490196078),
            (0.8196078431372549, 0.7764705882352941, 0.9058823529411765), (0.7137254901960784, 0.8901960784313725, 0.9568627450980393), (0.7019607843137254, 0.8313725490196079, 1.0), (0.9450980392156862, 0.7137254901960784, 0.7568627450980392), (0.7176470588235294, 0.8941176470588236, 0.7803921568627451), (0.8431372549019608, 0.8352941176470589, 1.0), (1.0, 0.7019607843137254, 0.9019607843137255), (0.6509803921568628, 0.7137254901960784, 0.8313725490196079),
                   (0.9568627450980393, 0.8352941176470589, 0.7686274509803922), (0.9607843137254902, 0.7254901960784313, 0.2549019607843137), (0.9176470588235294, 0.8862745098039215, 0.7176470588235294), (1.0, 0.8196078431372549, 0.4), (0.0, 0.7490196078431373, 1.0), (0.8862745098039215, 0.8862745098039215, 0.8352941176470589), (1.0, 0.7686274509803922, 0.8392156862745098), (0.6392156862745098, 0.8509803921568627, 1.0),
                     (0.7647058823529411, 0.8549019607843137, 0.17647058823529413), (1.0, 0.4823529411764706, 0.0), (0.9686274509803922, 0.6980392156862745, 0.6352941176470588), (0.8235294117647058, 0.6980392156862745, 0.7647058823529411), (0.9568627450980393, 0.8392156862745098, 0.6274509803921569), (0.7607843137254902, 0.7607843137254902, 0.8392156862745098), (1.0, 0.4588235294117647, 0.5607843137254902), 
                     (0.7137254901960784, 0.9607843137254902, 0.6352941176470588), (0.7647058823529411, 0.7725490196078432, 0.7568627450980392), (1.0, 0.8392156862745098, 0.9098039215686274), (1.0, 0.8941176470588236, 0.7098039215686275), (0.6627450980392157, 0.8549019607843137, 0.8392156862745098), (0.8470588235294118, 0.6549019607843137, 0.8431372549019608), (1.0, 0.8823529411764706, 0.33725490196078434), 
                     (0.9411764705882353, 0.9215686274509803, 0.8470588235294118), (1.0, 0.40784313725490196, 0.4196078431372549), (0.788235294117647, 0.788235294117647, 1.0), (0.9490196078431372, 0.7843137254901961, 0.9019607843137255), (1.0, 0.7294117647058823, 0.7529411764705882), (0.9450980392156862, 0.7137254901960784, 0.8196078431372549), (1.0, 0.7098039215686275, 0.8470588235294118), 
                     (0.7843137254901961, 0.7098039215686275, 0.7098039215686275), (0.9098039215686274, 0.8117647058823529, 0.8117647058823529), (0.7568627450980392, 0.7607843137254902, 0.7215686274509804), (0.7607843137254902, 0.8862745098039215, 0.8352941176470589), (0.9686274509803922, 0.9607843137254902, 0.6274509803921569), (0.9686274509803922, 0.6901960784313725, 0.8509803921568627), 
                     (0.9725490196078431, 0.7254901960784313, 0.6588235294117647), (1.0, 0.807843137254902, 1.0), (0.6313725490196078, 0.8352941176470589, 0.8941176470588236), (0.6941176470588235, 0.6941176470588235, 0.8862745098039215), (0.9725490196078431, 0.6392156862745098, 0.7764705882352941), (0.9764705882352941, 0.984313725490196, 0.6980392156862745), 
                     (1.0, 0.8823529411764706, 0.33725490196078434), (0.9529411764705882, 0.8156862745098039, 0.5411764705882353), (1.0, 0.7647058823529411, 0.7725490196078432), (0.8549019607843137, 0.8823529411764706, 0.9058823529411765), (0.7490196078431373, 0.8627450980392157, 0.8980392156862745), (1.0, 0.8352941176470589, 0.7098039215686275), 
                     (0.9607843137254902, 0.8392156862745098, 0.8235294117647058), (0.8392156862745098, 0.8352941176470589, 0.788235294117647), (0.8941176470588236, 0.8470588235294118, 0.8588235294117647), (0.8196078431372549, 0.8352941176470589, 0.8549019607843137), (0.7137254901960784, 0.8980392156862745, 0.6980392156862745), (0.9568627450980393, 0.8470588235294118, 0.6470588235294118), 
                     (0.9686274509803922, 0.7529411764705882, 0.8313725490196079), (1.0, 0.6745098039215687, 0.7176470588235294), (0.9725490196078431, 0.6549019607843137, 0.8235294117647058), (1.0, 0.7568627450980392, 0.6588235294117647), (0.9725490196078431, 0.7372549019607844, 0.9137254901960784), (0.8392156862745098, 0.6313725490196078, 0.7215686274509804), 
                     (1.0, 0.7019607843137254, 0.7019607843137254), (1.0, 0.788235294117647, 0.6941176470588235), (0.8313725490196079, 0.9411764705882353, 0.7843137254901961), (0.7137254901960784, 0.6470588235294118, 0.8196078431372549), (0.8392156862745098, 0.7764705882352941, 0.7568627450980392), (0.9686274509803922, 0.6274509803921569, 0.7098039215686275), 
                     (0.8392156862745098, 0.9019607843137255, 0.8352941176470589), (0.8392156862745098, 0.6431372549019608, 0.8980392156862745), (0.9450980392156862, 0.8509803921568627, 0.7490196078431373), (0.9725490196078431, 0.6274509803921569, 0.6313725490196078), (0.7019607843137254, 0.8196078431372549, 0.7176470588235294), 
                     (0.8392156862745098, 0.7764705882352941, 0.7764705882352941), (1.0, 0.796078431372549, 0.5215686274509804), (1.0, 0.803921568627451, 0.6352941176470588), (1.0, 0.8196078431372549, 0.7529411764705882), (0.6941176470588235, 0.9137254901960784, 0.8823529411764706), (0.9725490196078431, 0.9568627450980393, 0.6549019607843137), 
                     (1.0, 0.7019607843137254, 0.7019607843137254), (0.8509803921568627, 0.8156862745098039, 0.8156862745098039), (0.7215686274509804, 0.9098039215686274, 0.7647058823529411), (0.9725490196078431, 0.7215686274509804, 0.7215686274509804), (0.7254901960784313, 0.6509803921568628, 0.9607843137254902)]

def wrap_paragraphs_with_color(paragraphs, best_match, school_id):
    color_index = school_id % len(color_hex)
    color = color_hex[color_index]

    highlighted_text = best_match
    for paragraph in paragraphs:
        highlighted_text = highlighted_text.replace(paragraph, f'<span style="background-color:{color};">{paragraph}</span>')

    return highlighted_text

def source_append(sources, source_id, school_id, school_name, file_id_source, type, excepted, school_stt, best_match, score, word_count_sml, paragraphs_best_math, positions):
    sources.append({
                "source_id":source_id,
                "school_id": school_id,
                "school_name": school_name,
                "file_id": file_id_source,
                "type_source": type, 
                "except": excepted,
                "color": color_hex[school_id],
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

    return pdf_stream

