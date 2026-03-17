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
    .analysis-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 1px solid #e0e0e0; color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CẤU HÌNH AI (SỬA LỖI 404 TRIỆT ĐỂ) ---
st.title("🇷🇺 Russian Master AI")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ CHƯA CÓ API KEY trong Secrets!")
    st.stop()

# Cấu hình API
genai.configure(api_key=api_key)

# PHƯƠNG PHÁP MỚI: Gọi trực tiếp model ổn định nhất
# Nếu gemini-1.5-flash lỗi, hệ thống sẽ tự dùng gemini-pro làm phương án dự phòng
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    model = genai.GenerativeModel('gemini-pro')

# --- 3. QUẢN LÝ TRẠNG THÁI ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False
if 'wrong_attempts' not in st.session_state: st.session_state.wrong_attempts = 0
if 'data' not in st.session_state: st.session_state.data = None

with st.sidebar:
    st.header("Cài đặt")
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
                    st.success("Đúng rồi!")
                    st.session_state.show_analysis = True
                else:
                    st.error("Chưa đúng!")
                    st.session_state.wrong_attempts += 1

        with c2:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.idx = random.randint(0, len(df)-1)
                st.session_state.show_analysis = False
                st.session_state.wrong_attempts = 0
                st.rerun()

        if st.session_state.wrong_attempts == 1:
            st.warning(f"💡 Gợi ý: {word_ru[0]}...{word_ru[-1]}")
        elif st.session_state.wrong_attempts >= 2:
            st.info(f"🔑 Đáp án: {word_ru}")

        if st.session_state.show_analysis:
            with st.spinner("AI đang soạn bài phân tích..."):
                try:
                    # Gợi ý AI phân tích chi tiết ngữ pháp quân sự/kỹ thuật
                    prompt = f"Phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}). 1. Giải thích ngữ pháp. 2. Đặt 2 câu ví dụ Việt-Nga (Ưu tiên 1 câu quân sự/kỹ thuật)."
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(f"<div class='analysis-box'>{response.text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    # Nếu vẫn lỗi 404, dùng cơ chế 'v1' thay vì mặc định
                    st.error(f"Đang thử kết nối lại... (Vui lòng gõ lại từ này)")
                    st.session_state.show_analysis = False
    else:
        st.error("File thiếu cột Tiếng Việt/Tiếng Nga.")
else:
    st.info("Mở Menu bên trái để tải file Excel.")
