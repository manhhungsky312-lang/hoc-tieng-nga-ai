import streamlit as st
import pandas as pd
import google.generativeai as genai
import random

# --- 1. CẤU HÌNH GIAO DIỆN (DÀNH CHO ĐIỆN THOẠI) ---
st.set_page_config(page_title="Học Tiếng Nga AI", page_icon="🇷🇺", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px !important; border-radius: 10px; border: 2px solid #007bff; }
    .status-box { padding: 10px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ddd; }
    .analysis-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# --- 2. KIỂM TRA KẾT NỐI AI (BƯỚC QUAN TRỌNG) ---
st.title("🇷🇺 Russian Master AI")

# Lấy API Key từ Secrets (Đảm bảo bạn đã dán vào Secrets của Streamlit)
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ CHƯA CÓ API KEY: Hãy vào Settings -> Secrets trên Streamlit và dán GEMINI_API_KEY vào.")
    st.stop()

# Cấu hình AI
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

# Kiểm tra "Mạng" thực tế bằng một câu hỏi nhỏ
@st.cache_data(show_spinner=False)
def check_ai_connection():
    try:
        response = model.generate_content("Xin chào, bạn có online không?")
        return True, "Kết nối AI thành công! ✅"
    except Exception as e:
        return False, f"Lỗi kết nối mạng/API: {str(e)}"

is_online, status_msg = check_ai_connection()
if is_online:
    st.toast(status_msg)
else:
    st.error(f"⚠️ {status_msg}")
    st.info("Mẹo: Hãy kiểm tra lại mã API của bạn có bị thừa khoảng trắng không hoặc thử tạo mã mới trên Google AI Studio.")

# --- 3. QUẢN LÝ DỮ LIỆU ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False
if 'wrong_attempts' not in st.session_state: st.session_state.wrong_attempts = 0

with st.sidebar:
    st.header("Cài đặt")
    uploaded_file = st.file_uploader("Nạp file Excel từ máy/điện thoại", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        df.columns = [c.strip().lower() for c in df.columns]
        st.session_state.data = df
        st.success("Đã tải dữ liệu!")

# --- 4. GIAO DIỆN HỌC TẬP ---
if 'data' in st.session_state:
    df = st.session_state.data
    col_ru = next((c for c in df.columns if 'nga' in c or 'ru' in c), None)
    col_vn = next((c for c in df.columns if 'việt' in c or 'vn' in c), None)

    if col_ru and col_vn:
        row = df.iloc[st.session_state.idx]
        word_vn = str(row[col_vn]).strip()
        word_ru = str(row[col_ru]).strip()

        st.markdown(f"<h3 style='text-align: center;'>Dịch sang tiếng Nga:</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; color: #d32f2f;'>{word_vn}</h1>", unsafe_allow_html=True)

        user_input = st.text_input("Gõ từ tiếng Nga:", value="", key=f"input_{st.session_state.idx}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Kiểm tra ✅"):
                if user_input.strip().lower() == word_ru.lower():
                    st.success("Quá chuẩn! Đang phân tích...")
                    st.session_state.show_analysis = True
                    st.session_state.wrong_attempts = 0
                else:
                    st.error("Chưa đúng rồi!")
                    st.session_state.wrong_attempts += 1

        with c2:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.idx = random.randint(0, len(df)-1)
                st.session_state.show_analysis = False
                st.session_state.wrong_attempts = 0
                st.rerun()

        # Gợi ý thông minh
        if st.session_state.wrong_attempts == 1:
            st.warning(f"💡 Gợi ý: Từ này có {len(word_ru)} ký tự, bắt đầu bằng '{word_ru[0]}'")
        elif st.session_state.wrong_attempts >= 2:
            st.info(f"🔑 Đáp án đúng là: {word_ru}")

        # Phân tích chi tiết từ AI
        if st.session_state.show_analysis:
            with st.spinner("AI đang soạn bài phân tích..."):
                try:
                    prompt = f"""
                    Phân tích từ: '{word_ru}' (nghĩa: {word_vn}).
                    1. Ngữ pháp: Từ loại, cách chia, giống (nếu có).
                    2. 3 câu ví dụ Việt - Nga (1 câu giao tiếp, 1 câu chuyên sâu/quân sự).
                    Trình bày bằng Markdown đẹp mắt.
                    """
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(f"<div class='analysis-box'>{response.text}</div>", unsafe_allow_html=True)
                except Exception:
                    st.error("AI bận rồi, không phân tích được lúc này!")
    else:
        st.error("File Excel phải có cột 'Tiếng Việt' và 'Tiếng Nga'.")
else:
    st.info("Hãy bấm vào Menu bên trái (hình 3 gạch) để tải file Excel lên nhé!")
