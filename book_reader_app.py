import streamlit as st
import json

# --- 應用程式配置 ---
st.set_page_config(
    page_title="智能線上書櫃",
    page_icon="📚",
    layout="wide"
)

# --- 核心邏輯 ---

def parse_text_to_dict(text_content):
    """
    將傳入的文本內容解析成一個 Python 字典。
    (智能升級版：能自動檢測短標題作為章節)

    Args:
        text_content (str): 從文件中讀取的完整文本內容。

    Returns:
        dict: 符合項目結構的字典。
    """
    lines = text_content.splitlines()

    if not lines:
        return {}

    # --- 修改重點開始 ---

    # 1. 第一行作為標題
    title = lines[0].strip()
    
    data = {
        "title": title,
        "chapters": []
    }

    current_chapter = None
    
    # 從第二行開始遍歷 (使用索引i方便查看下一行)
    i = 1
    while i < len(lines):
        line = lines[i].strip()
        
        # 獲取下一行的內容，如果不存在則為空
        next_line = lines[i+1].strip() if (i + 1) < len(lines) else None

        # 如果是空行，則跳過
        if not line:
            i += 1
            continue

        # 2. 判斷是否為章節標題 (兩種規則)
        is_chapter_title = False
        chapter_title_content = ""

        # 規則一：以 "章：" 開頭 (優先級最高)
        if line.startswith("章："):
            is_chapter_title = True
            chapter_title_content = line[2:].strip()
        
        # 規則二：短標題檢測 (長度小於10，且下一行有內容)
        elif len(line) < 10 and next_line:
            is_chapter_title = True
            chapter_title_content = line

        # 3. 根據判斷結果進行處理
        if is_chapter_title:
            # 如果已有正在處理的章節，先保存它
            if current_chapter:
                data["chapters"].append(current_chapter)
            
            # 創建新的章節對象
            current_chapter = {
                "chapter": chapter_title_content,
                "paragraphs": []
            }
        elif current_chapter:
            # 如果不是章節標題，就是段落內容
            current_chapter["paragraphs"].append(line)
        
        i += 1

    # 不要忘記添加最後一個章節
    if current_chapter:
        data["chapters"].append(current_chapter)
    
    # --- 修改重點結束 ---

    return data


# --- Session State 初始化 ---
if 'books' not in st.session_state:
    st.session_state.books = {}

# --- 使用者介面 (UI) ---

with st.sidebar:
    st.title("📚 智能書櫃")
    
    uploaded_files = st.file_uploader(
        "上傳 .txt 或 .json 文件",
        type=["txt", "json"],
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            
            try:
                # 判斷文件類型
                if file_name.endswith(".json"):
                    # 直接加載 JSON 文件
                    book_data = json.load(uploaded_file)
                elif file_name.endswith(".txt"):
                    # 使用我們的智能轉換工具
                    text_content = uploaded_file.getvalue().decode("utf-8", errors="ignore")
                    book_data = parse_text_to_dict(text_content)
                else:
                    st.warning(f"不支持的文件格式: {file_name}")
                    continue

                book_title = book_data.get("title", "無標題書籍")
                st.session_state.books[book_title] = book_data

            except Exception as e:
                st.error(f"處理文件 {file_name} 時出錯: {e}")
        
        if st.session_state.books:
            st.success(f"成功處理 {len(uploaded_files)} 個文件！")

    # 顯示書籍列表
    if not st.session_state.books:
        st.info("您的書櫃是空的，請先上傳書籍。")
    else:
        book_titles = list(st.session_state.books.keys())
        selected_title = st.selectbox("請選擇一本書來閱讀：", options=book_titles)

# 主畫面
if st.session_state.books and 'selected_title' in locals():
    selected_book = st.session_state.books[selected_title]
    st.title(selected_book["title"])

    for chapter in selected_book.get("chapters", []):
        st.header(chapter["chapter"])
        for paragraph in chapter.get("paragraphs", []):
            st.markdown(f"> {paragraph}")
        st.divider()
else:
    st.title("歡迎來到您的智能線上書櫃")
    st.markdown("請使用左側的上傳功能來添加您的第一本書籍。")