import streamlit as st
import pandas as pd
import google.generativeai as genai
import random

# --- 1. CẤU HÌNH GIAO DIỆN (TỐI ƯU CHO ĐIỆN THOẠI) ---
st.set_page_config(page_title="Học Tiếng Nga AI", page_icon="🇷🇺", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; background-color: #007bff; color: white; font-weight: bold; }
    .stTextInput>div>div>input { text-align: center; font-size: 20px !important; border-radius: 12px; border: 2px solid #007bff; }
    .analysis-box { background-color: #ffffff; padding: 15px; border-radius: 15px; border: 1px solid #e0e0e0; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); color: #333; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CẤU HÌNH AI (SỬA LỖI 404 & KẾT NỐI) ---
st.title("🇷🇺 Russian Master AI")

# Lấy API Key từ Secrets
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("❌ CHƯA CÓ API KEY: Vui lòng vào Settings -> Secrets trên Streamlit và dán GEMINI_API_KEY vào.")
    st.stop()

# Cấu hình API
genai.configure(api_key=api_key)

# Khởi tạo Model (Sửa lỗi 404 bằng cách gọi trực tiếp model flash)
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Lỗi khởi tạo mô hình AI: {e}")
    st.stop()

# --- 3. QUẢN LÝ TRẠNG THÁI HỌC TẬP ---
if 'idx' not in st.session_state: st.session_state.idx = 0
if 'show_analysis' not in st.session_state: st.session_state.show_analysis = False
if 'wrong_attempts' not in st.session_state: st.session_state.wrong_attempts = 0
if 'data' not in st.session_state: st.session_state.data = None

# Sidebar để nạp dữ liệu
with st.sidebar:
    st.header("Dữ liệu học tập")
    uploaded_file = st.file_uploader("Chọn file Excel từ điện thoại (.xlsx)", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            # Sửa lỗi AttributeError: Chuyển tên cột thành chuỗi và làm sạch
            df.columns = [str(c).strip().lower() for c in df.columns if c is not None]
            st.session_state.data = df
            st.success("Đã nạp từ vựng thành công!")
        except Exception as e:
            st.error(f"Lỗi đọc file Excel: {e}")

# --- 4. GIAO DIỆN HÀNH ĐỘNG ---
if st.session_state.data is not None:
    df = st.session_state.data
    
    # Tìm cột Tiếng Nga và Tiếng Việt thông minh
    col_ru = next((c for c in df.columns if 'nga' in c or 'ru' in c), None)
    col_vn = next((c for c in df.columns if 'việt' in c or 'vn' in c or 'viet' in c), None)

    if col_ru and col_vn:
        # Kiểm tra giới hạn hàng
        if st.session_state.idx >= len(df):
            st.session_state.idx = 0
            
        row = df.iloc[st.session_state.idx]
        word_vn = str(row[col_vn]).strip()
        word_ru = str(row[col_ru]).strip()

        st.markdown(f"<h3 style='text-align: center;'>Dịch sang tiếng Nga:</h3>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='text-align: center; color: #d32f2f;'>{word_vn}</h1>", unsafe_allow_html=True)

        # Nhập liệu
        user_input = st.text_input("Gõ từ tiếng Nga:", value="", key=f"input_{st.session_state.idx}", placeholder="Nhập tại đây...")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Kiểm tra ✅"):
                if user_input.strip().lower() == word_ru.lower():
                    st.success("Chính xác!")
                    st.session_state.show_analysis = True
                else:
                    st.error("Chưa đúng rồi!")
                    st.session_state.wrong_attempts += 1

        with c2:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.idx = random.randint(0, len(df)-1)
                st.session_state.show_analysis = False
                st.session_state.wrong_attempts = 0
                st.rerun()

        # Gợi ý thông minh khi sai
        if st.session_state.wrong_attempts == 1:
            st.warning(f"💡 Gợi ý: Bắt đầu bằng '{word_ru[0]}', kết thúc bằng '{word_ru[-1]}'")
        elif st.session_state.wrong_attempts >= 2:
            st.info(f"🔑 Đáp án đúng là: {word_ru}")

        # Phân tích bằng AI khi gõ đúng
        if st.session_state.show_analysis:
            with st.spinner("Đang kết nối AI để phân tích..."):
                try:
                    prompt = f"""
                    Phân tích từ tiếng Nga: '{word_ru}' (nghĩa: {word_vn}).
                    Hãy giải thích:
                    1. Ngữ pháp (Giống, cách, từ loại).
                    2. Đặt 2 câu ví dụ Việt-Nga (Ưu tiên 1 câu thông dụng và 1 câu liên quan đến chuyên ngành kỹ thuật hoặc quân sự).
                    Trình bày bằng Markdown dễ nhìn.
                    """
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(f"<div class='analysis-box'>{response.text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Không thể lấy phân tích từ AI. (Lỗi mạng: {e})")
    else:
        st.error("Lỗi: File Excel của bạn phải có cột tên là 'Tiếng Việt' và 'Tiếng Nga'.")
else:
    st.info("Hãy bấm vào Menu bên trái (hình 3 gạch) và tải file Excel lên để bắt đầu học.")
