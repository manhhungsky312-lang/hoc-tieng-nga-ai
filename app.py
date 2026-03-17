import streamlit as st
import pandas as pd
import google.generativeai as genai
import random

st.set_page_config(page_title="Học Tiếng Nga AI", layout="centered")

# Cấu hình AI
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("Thiếu API KEY trong Secrets")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

if 'idx' not in st.session_state: st.session_state.idx = 0
if 'data' not in st.session_state: st.session_state.data = None

# Sidebar nạp file
with st.sidebar:
    uploaded_file = st.file_uploader("Nạp file Excel từ vựng", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [str(c).strip().lower() for c in df.columns]
        st.session_state.data = df
        st.success("Đã nạp file!")

# Hiển thị và học
if st.session_state.data is not None:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if 'nga' in c or 'ru' in c), None)
    col_vn = next((c for c in df.columns if 'việt' in c or 'vn' in c or 'viet' in c), None)

    if col_ru and col_vn:
        row = df.iloc[st.session_state.idx]
        word_vn = str(row[col_vn]).strip()
        word_ru = str(row[col_ru]).strip()

        st.subheader(f"Dịch sang tiếng Nga: {word_vn}")
        user_input = st.text_input("Nhập đáp án:", key=f"in_{st.session_state.idx}")

        if st.button("Kiểm tra & Phân tích"):
            if user_input.strip().lower() == word_ru.lower():
                st.success(f"Đúng! Đáp án: {word_ru}")
            else:
                st.error(f"Sai! Đáp án đúng: {word_ru}")
            
            with st.spinner("AI đang giải thích ngữ pháp..."):
                try:
                    prompt = f"Phân tích từ '{word_ru}' (nghĩa: {word_vn}). Giải thích ngữ pháp ngắn gọn và đặt 1 ví dụ quân sự/kỹ thuật Nga-Việt."
                    response = model.generate_content(prompt)
                    st.info(response.text)
                except Exception as e:
                    st.error(f"Lỗi AI: {e}")

        if st.button("Từ tiếp theo"):
            st.session_state.idx = random.randint(0, len(df)-1)
            st.rerun()
