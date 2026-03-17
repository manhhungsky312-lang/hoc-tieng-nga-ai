import streamlit as st
import pandas as pd
import google.generativeai as genai
from google.generativeai.types import RequestOptions
import random

# --- 1. CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Học Tiếng Nga AI", page_icon="🇷🇺", layout="centered")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px !important; border-radius: 12px; border: 2px solid #007bff; }
    .analysis-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 1px solid #e0e0e0; color: #333; }
    </style>
    """, unsafe_allow_html=True)

st.title("🇷🇺 Russian Master AI")

# --- 2. CẤU HÌNH AI (ÉP PHIÊN BẢN V1) ---
api_key = st.secrets.get("GEMINI_API_KEY")
if not api_key:
    st.error("❌ Thiếu GEMINI_API_KEY trong Secrets!")
    st.stop()

genai.configure(api_key=api_key)

# Giải pháp mạnh: Ép sử dụng API phiên bản v1 để tránh lỗi 404 v1beta
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

        with c2:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.idx = random.randint(0, len(df)-1)
                st.session_state.show_analysis = False
                st.rerun()

        if st.session_state.show_analysis:
            with st.spinner("AI đang soạn bài phân tích..."):
                try:
                    # SỬA LỖI 404: Ép phiên bản API v1 thông qua RequestOptions
                    prompt = f"Phân tích từ tiếng Nga '{word_ru}' (nghĩa: {word_vn}). Giải thích ngữ pháp ngắn gọn và đặt 2 câu ví dụ Việt-Nga (1 câu chuyên ngành quân sự/kỹ thuật)."
                    response = model.generate_content(
                        prompt,
                        request_options=RequestOptions(api_version='v1')
                    )
                    st.markdown("---")
                    st.markdown(f"<div class='analysis-box'>{response.text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Lỗi kết nối AI: {e}")
                    st.info("Hãy thử nhấn 'Kiểm tra' lại lần nữa sau khi ứng dụng đã Reboot xong.")
    else:
        st.error("File thiếu cột Tiếng Việt/Tiếng Nga.")
else:
    st.info("Mở Menu bên trái để tải file Excel.")
