import streamlit as st
import pandas as pd
import google.generativeai as genai
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Học Tiếng Nga AI", page_icon="🇷🇺", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px !important; border-radius: 12px; border: 2px solid #007bff; }
    .analysis-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 1px solid #e0e0e0; color: #333; line-height: 1.6; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇷🇺 Russian Master AI")

# --- 2. CẤU HÌNH AI ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ Thiếu GEMINI_API_KEY trong Secrets!")
    st.stop()

genai.configure(api_key=api_key)

# Sử dụng model gemini-1.5-flash (ổn định và nhanh nhất hiện tại)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 3. QUẢN LÝ TRẠNG THÁI ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False
if 'data' not in st.session_state: st.session_state.data = None

with st.sidebar:
    st.header("Dữ liệu")
    uploaded_file = st.file_uploader("Nạp file Excel", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            df.columns = [str(c).strip().lower() for c in df.columns if c is not None]
            st.session_state.data = df
            st.success("Đã nạp dữ liệu!")
        except Exception as e:
            st.error(f"Lỗi file: {e}")

# --- 4. GIAO DIỆN HÀNH ĐỘNG ---
if st.session_state.data is not None:
    df = st.session_state.data
    # Tìm cột Tiếng Nga và Tiếng Việt
    col_ru = next((c for c in df.columns if 'nga' in c or 'ru' in c), None)
    col_vn = next((c for c in df.columns if 'việt' in c or 'vn' in c or 'viet' in c), None)

    if col_ru and col_vn:
        if st.session_state.idx >= len(df): st.session_state.idx = 0
        row = df.iloc[st.session_state.idx]
        word_vn = str(row[col_vn]).strip()
        word_ru = str(row[col_ru]).strip()

        st.markdown(f"<h3 style='text-align: center;'>Dịch sang tiếng Nga:</h3><h1 style='text-align: center; color: #d32f2f;'>{word_vn}</h1>", unsafe_allow_html=True)

        user_input = st.text_input("Gõ từ tiếng Nga:", value="", key=f"input_{st.session_state.idx}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Kiểm tra ✅"):
                if user_input.strip().lower() == word_ru.lower():
                    st.success("Chính xác!")
                    st.session_state.show_analysis = True
                else:
                    st.error(f"Chưa đúng! Đáp án: {word_ru}")
                    st.session_state.show_analysis = True # Vẫn hiện phân tích để học từ đúng

        with c2:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.idx = random.randint(0, len(df)-1)
                st.session_state.show_analysis = False
                st.rerun()

        if st.session_state.show_analysis:
            with st.spinner("AI đang soạn bài phân tích..."):
                try:
                    prompt = (f"Phân tích từ tiếng Nga '{word_ru}' (nghĩa: {word_vn}). "
                              f"Giải thích ngữ pháp ngắn gọn về biến cách hoặc cấu tạo từ. "
                              f"Đặt 2 câu ví dụ Việt-Nga, trong đó có 1 câu về chuyên ngành quân sự hoặc kỹ thuật.")
                    
                    # Gọi trực tiếp không qua RequestOptions để tránh lỗi phiên bản thư viện
                    response = model.generate_content(prompt)
                    
                    st.markdown("---")
                    st.markdown(f"<div class='analysis-box'>{response.text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")
    else:
        st.error("File Excel cần có cột tên 'Tiếng Nga' và 'Tiếng Việt'.")
else:
    st.info("Mở Menu bên trái để tải file Excel chứa từ vựng của bạn.")
