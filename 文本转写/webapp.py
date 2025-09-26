import streamlit as st
import json

def parse_text_to_dict(text_content):
    """
    将传入的文本内容解析成一个 Python 字典。
    这是我们工具的核心逻辑。

    Args:
        text_content (str): 从文件中读取的完整文本内容。

    Returns:
        dict: 符合项目结构的字典。
    """
    lines = text_content.splitlines()

    if not lines:
        return {}

    # 第一行作为标题
    title = lines[0].strip()
    
    # 最终的 JSON 结构
    data = {
        "title": title,
        "chapters": []
    }

    current_chapter = None
    
    # 从第二行开始遍历，识别章节和段落
    for line in lines[1:]:
        line = line.strip()

        if not line:
            continue

        if line.startswith("章："):
            if current_chapter:
                data["chapters"].append(current_chapter)
            
            current_chapter = {
                "chapter": line[2:].strip(),
                "paragraphs": []
            }
        elif current_chapter:
            current_chapter["paragraphs"].append(line)

    if current_chapter:
        data["chapters"].append(current_chapter)

    return data

# --- Streamlit 网页界面 ---

# 1. 设置网页标题
st.title("文本自动转换 JSON 工具")
st.write("请上传一个遵循预定格式的 .txt 文件，工具将自动将其转换为可用于 'chinese-philosophy' 项目的 JSON 格式。")

# 2. 创建文件上传控件
# 'type="txt"' 限制用户只能上传 .txt 文件
uploaded_file = st.file_uploader("选择一个 .txt 文件", type="txt")

# 3. 检查是否有文件被上传
if uploaded_file is not None:
    # 为了读取中文，使用 utf-8 解码
    try:
        text_content = uploaded_file.getvalue().decode("utf-8")
        st.subheader("文件内容预览")
        # st.text_area 创建一个文本框，方便预览
        st.text_area("Content", text_content, height=250)

        # 4. 执行转换
        st.subheader("转换结果")
        structured_data = parse_text_to_dict(text_content)
        
        if not structured_data:
            st.warning("无法解析文件或文件为空。")
        else:
            # 在网页上显示 JSON 数据
            st.json(structured_data)

            # 5. 提供下载按钮
            # 先将字典转为 JSON 格式的字符串
            json_string = json.dumps(structured_data, ensure_ascii=False, indent=2)
            
            # 从上传的文件名生成下载文件名 (例如 a.txt -> a.json)
            download_filename = uploaded_file.name.split('.')[0] + '.json'

            st.download_button(
                label="📥 下载 JSON 文件",
                data=json_string,
                file_name=download_filename,
                mime="application/json",
            )
    except Exception as e:
        st.error(f"处理文件时发生错误: {e}")