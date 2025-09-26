import streamlit as st
import json
import re

# --- 應用程式配置 ---
st.set_page_config(
    page_title="專業線上書櫃",
    page_icon="📚",
    layout="wide"
)

# --- 核心邏輯 ---

# 解析器 1: 處理簡單格式的 txt 文件 (我們最早的版本)
def parse_simple_text_to_dict(text_content):
    lines = text_content.splitlines()
    if not lines: return {}
    title = lines[0].strip()
    data = {"title": title, "chapters": []}
    current_chapter = None
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        next_line = lines[i+1].strip() if (i + 1) < len(lines) else None
        if not line:
            i += 1
            continue
        is_chapter_title = False
        chapter_title_content = ""
        if line.startswith("章："):
            is_chapter_title = True
            chapter_title_content = line[2:].strip()
        elif len(line) < 10 and next_line:
            is_chapter_title = True
            chapter_title_content = line
        if is_chapter_title:
            if current_chapter: data["chapters"].append(current_chapter)
            current_chapter = {"chapter": chapter_title_content, "paragraphs": []}
        elif current_chapter:
            current_chapter["paragraphs"].append(line)
        i += 1
    if current_chapter: data["chapters"].append(current_chapter)
    return data

# 解析器 2: 處理我們新的富文本格式 (專業版)
def parse_rich_text_to_json(text_content):
    lines = text_content.splitlines()
    metadata = {}
    content_start_index = 0
    for i, line in enumerate(lines):
        if ":" in line and i < 5: # 只檢查前5行是否為元數據
            key, value = line.split(":", 1)
            metadata[key.strip()] = value.strip()
            content_start_index = i + 1
        elif line.strip() and ":" not in line:
            break
    if 'hasZhushu' in metadata: metadata['hasZhushu'] = metadata['hasZhushu'].lower() == 'true'
    if 'loadChapterCount' in metadata: metadata['loadChapterCount'] = int(metadata['loadChapterCount'])
    final_json = metadata
    final_json["chapters"] = []
    current_chapter = None
    pattern = re.compile(r'([^【\[]+)(?:【(.*?)】)?(?:\[(T\d+)\])?')
    for line in lines[content_start_index:]:
        line = line.strip()
        if not line: continue
        if line.startswith("章："):
            if current_chapter: final_json["chapters"].append(current_chapter)
            current_chapter = {"name": line[2:].strip(), "paragraphs": []}
            continue
        if not current_chapter: continue
        matches = pattern.finditer(line)
        for match in matches:
            paragraph_text = match.group(1).strip() if match.group(1) else ""
            zhushu_text = match.group(2).strip() if match.group(2) else ""
            type_tag = match.group(3).strip() if match.group(3) else ""
            if not paragraph_text: continue
            para_obj = {"paragraph": paragraph_text, "zhushu": zhushu_text}
            if type_tag == "T1": para_obj["type"] = 1
            elif type_tag == "T2": para_obj["type"] = 2
            current_chapter["paragraphs"].append(para_obj)
    if current_chapter: final_json["chapters"].append(current_chapter)
    # 為了兼容舊的顯示邏輯，我們統一一下key的名稱
    if 'name' in final_json: final_json['title'] = final_json.pop('name')
    return final_json

# --- Session State 初始化 ---
if 'books' not in st.session_state:
    st.session_state.books = {}

# --- 使用者介面 (UI) ---

with st.sidebar:
    st.title("📚 專業書櫃")
    uploaded_files = st.file_uploader("上傳 .txt 或 .json 文件", type=["txt", "json"], accept_multiple_files=True)
    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            try:
                book_data = {}
                if file_name.endswith(".json"):
                    book_data = json.load(uploaded_file)
                elif file_name.endswith(".txt"):
                    content_bytes = uploaded_file.getvalue()
                    try:
                        text_content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        text_content = content_bytes.decode('big5')
                    
                    # --- 智能判斷調用哪個解析器 ---
                    if re.match(r'^\w+:\s*.*', text_content): # 如果第一行看起來像 "key: value"
                        book_data = parse_rich_text_to_json(text_content)
                    else:
                        book_data = parse_simple_text_to_dict(text_content)

                book_title = book_data.get("title", "無標題書籍")
                st.session_state.books[book_title] = book_data
            except Exception as e:
                st.error(f"處理文件 {file_name} 時出錯: {e}")
        st.success("文件處理完成！")

    if st.session_state.books:
        book_titles = list(st.session_state.books.keys())
        selected_title = st.selectbox("請選擇一本書來閱讀：", options=book_titles)
    else:
        st.info("您的書櫃是空的。")

# --- 主畫面 ---
if 'selected_title' in locals() and selected_title:
    selected_book = st.session_state.books[selected_title]
    
    st.title(selected_book.get("title", "無標題"))
    if "author" in selected_book:
        st.caption(f"作者：{selected_book['author']}")
    st.divider()

    for chapter in selected_book.get("chapters", []):
        # 兼容兩種章節標題key: 'name' 和 'chapter'
        chapter_name = chapter.get("name", chapter.get("chapter", "未知章節"))
        st.header(chapter_name)
        
        paragraphs_data = chapter.get("paragraphs", [])
        for p_data in paragraphs_data:
            # --- 智能判斷顯示簡單格式還是複雜格式 ---
            if isinstance(p_data, str):
                # 舊的簡單格式，直接顯示
                st.markdown(f"> {p_data}")
            elif isinstance(p_data, dict):
                # 新的富文本格式
                st.markdown(f"### {p_data.get('paragraph', '')}")
                if p_data.get('zhushu'):
                    # 用不同顏色或樣式顯示注疏
                    st.markdown(f"<p style='color:grey; font-size: 0.9em;'>注：{p_data['zhushu']}</p>", unsafe_allow_html=True)
else:
    st.title("歡迎來到您的專業線上書櫃")
    st.markdown("請使用左側的上傳功能來添加您的書籍。")