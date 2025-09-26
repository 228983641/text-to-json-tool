import streamlit as st
import json

# --- 應用程式配置 ---
st.set_page_config(
    page_title="線上書櫃",
    page_icon="📚",
    layout="wide"
)

# --- 核心邏輯 ---

# 1. 初始化 Session State，確保我們的「書櫃」存在
if 'books' not in st.session_state:
    st.session_state.books = {} # 初始化一個空的字典來存放書籍資料

# --- 使用者介面 (UI) ---

# 2. 側邊欄 (Sidebar) - 用於放置控制項
with st.sidebar:
    st.title("📚 我的書櫃")
    
    # 3. 處理上傳的 JSON 文件
    uploaded_files = st.file_uploader(
        "上傳您的 .json 書籍文件",
        type="json",
        accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            # --- 修改重點開始 ---
            # 這是我們更新後的智能錯誤處理邏輯
            try:
                # 先讀取文件的二進制內容
                file_content_bytes = uploaded_file.getvalue()
                
                # 優先嘗試用 UTF-8 解碼
                try:
                    decoded_content = file_content_bytes.decode('utf-8')
                except UnicodeDecodeError:
                    # 如果 UTF-8 失敗，再嘗試用 Big5 解碼
                    st.warning(f"文件 {uploaded_file.name} 不是 UTF-8 編碼，正在嘗試用 Big5 解碼...")
                    decoded_content = file_content_bytes.decode('big5')
                    
                # 將解碼後的字符串內容加載為 JSON
                book_data = json.loads(decoded_content)
                book_title = book_data.get("title", "無標題書籍")
                st.session_state.books[book_title] = book_data

            except Exception as e:
                st.error(f"處理文件 {uploaded_file.name} 時出錯: {e}")
            # --- 修改重點結束 ---
        
        # 提示上傳成功
        if st.session_state.books: # 確保有書被成功加載
            st.success(f"成功處理 {len(uploaded_files)} 個文件！")

    # 4. 顯示書籍列表供用戶選擇
    if not st.session_state.books:
        st.info("您的書櫃是空的，請先上傳書籍。")
    else:
        book_titles = list(st.session_state.books.keys())
        selected_title = st.selectbox("請選擇一本書來閱讀：", options=book_titles)

# 5. 主畫面 (Main Panel) - 用於顯示書籍內容
if st.session_state.books and 'selected_title' in locals():
    selected_book = st.session_state.books[selected_title]

    st.title(selected_book["title"])

    for chapter in selected_book.get("chapters", []):
        st.header(chapter["chapter"])
        
        for paragraph in chapter.get("paragraphs", []):
            st.markdown(f"> {paragraph}")
        
        st.divider()
else:
    st.title("歡迎來到您的線上書櫃")
    st.markdown("請使用左側的**上傳功能**來添加您的第一本書籍。")