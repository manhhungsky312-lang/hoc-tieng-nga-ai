import streamlit as st
import pandas as pd
import google.generativeai as genai
import random

# --- CẤU HÌNH GIAO DIỆN CHUẨN MOBILE ---
st.set_page_config(
    page_title="Học Tiếng Nga AI",
    page_icon="🇷🇺",
    layout="centered"
)

# CSS để giao diện đẹp và dễ bấm trên điện thoại
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        background-color: #007bff; 
        color: white; 
        font-weight: bold;
        border: none;
    }
    .stTextInput>div>div>input { 
        text-align: center; 
        font-size: 22px !important; 
        border-radius: 12px; 
        border: 2px solid #007bff;
    }
    .hint-box { 
        background-color: #fff3cd; 
        padding: 15px; 
        border-radius: 12px; 
        border-left: 6px solid #ffc107;
        color: #856404;
        margin: 10px 0;
    }
    .analysis-box { 
        background-color: #ffffff; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #dee2e6;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- CẤU HÌNH AI (LẤY TỪ SECRETS) ---
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("LỖI: Chưa cấu hình GEMINI_API_KEY trong phần Secrets của Streamlit!")
    st.stop()

# --- KHỞI TẠO BỘ NHỚ TẠM (SESSION STATE) ---
if 'data' not in st.session_state:
    st.session_state.data = None
if 'idx' not in st.session_state:
    st.session_state.idx = 0
if 'show_analysis' not in st.session_state:
    st.session_state.show_analysis = False
if 'hint_count' not in st.session_state:
    st.session_state.hint_count = 0

# --- GIAO DIỆN CHÍNH ---
st.title("🇷🇺 Russian Master AI")
st.write("Phần mềm học từ mới thông minh")

# Thanh bên (Sidebar) để tải file
with st.sidebar:
    st.header("Dữ liệu học tập")
    uploaded_file = st.file_uploader("Tải file Excel từ điện thoại", type=["xlsx"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            # Tự động chuẩn hóa tên cột
            df.columns = [c.strip().lower() for c in df.columns]
            st.session_state.data = df
            st.success("Đã nạp dữ liệu!")
        except Exception as e:
            st.error(f"Lỗi đọc file: {e}")

# --- XỬ LÝ LOGIC HỌC TẬP ---
if st.session_state.data is not None:
    df = st.session_state.data
    
    # Tìm cột Tiếng Nga và Tiếng Việt (không phân biệt hoa thường)
    col_ru = next((c for c in df.columns if 'nga' in c or 'ru' in c), None)
    col_vn = next((c for c in df.columns if 'việt' in c or 'vn' in c), None)

    if col_ru and col_vn:
        # Lấy từ hiện tại
        row = df.iloc[st.session_state.idx]
        word_vn = str(row[col_vn]).strip()
        word_ru = str(row[col_ru]).strip()

        st.info(f"Dịch từ này sang tiếng Nga:")
        st.markdown(f"<h2 style='text-align: center; color: #1f77b4;'>{word_vn}</h2>", unsafe_allow_html=True)
        
        # Ô nhập liệu cho người học
        user_input = st.text_input("Nhập kết quả:", placeholder="Gõ tiếng Nga tại đây...", key=f"input_{st.session_state.idx}")

        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Kiểm tra ✅"):
                if user_input.strip().lower() == word_ru.lower():
                    st.success("Chính xác! Đang phân tích...")
                    st.session_state.show_analysis = True
                    st.session_state.hint_count = 0
                else:
                    st.error("Chưa đúng, hãy thử lại!")
                    st.session_state.hint_count += 1

        with col2:
            if st.button("Từ tiếp theo ➡️"):
                st.session_state.idx = random.randint(0, len(df) - 1)
                st.session_state.show_analysis = False
                st.session_state.hint_count = 0
                st.rerun()

        # --- PHẦN GỢI Ý KHI GÕ SAI ---
        if st.session_state.hint_count == 1:
            hint = f"Gợi ý: Từ này bắt đầu bằng '**{word_ru[0]}**' và kết thúc bằng '**{word_ru[-1]}**'"
            st.markdown(f"<div class='hint-box'>{hint}</div>", unsafe_allow_html=True)
        elif st.session_state.hint_count >= 2:
            st.markdown(f"<div class='hint-box'><b>Đáp án đúng là: {word_ru}</b></div>", unsafe_allow_html=True)

        # --- PHẦN PHÂN TÍCH CHI TIẾT CỦA AI ---
        if st.session_state.show_analysis:
            with st.spinner("AI đang phân tích ngữ pháp và đặt câu..."):
                try:
                    prompt = f"""
                    Phân tích từ tiếng Nga: '{word_ru}' (Nghĩa tiếng Việt: {word_vn}). 
                    Yêu cầu trình bày chi tiết:
                    1. Phân tích ngữ pháp: (Giống đực/cái/trung, cách chia, cặp động từ hoàn thành/chưa hoàn thành...).
                    2. Giải thích cách dùng từ này trong đời sống.
                    3. Đặt 3 câu ví dụ chuẩn:
                       - 1 câu giao tiếp thông thường.
                       - 1 câu phức tạp hoặc thành ngữ.
                       - 1 câu liên quan đến chuyên ngành hoặc quân sự (nếu có thể).
                    Tất cả câu ví dụ phải có dịch nghĩa tiếng Việt.
                    """
                    response = model.generate_content(prompt)
                    st.markdown("---")
                    st.markdown(f"<div class='analysis-box'>{response.text}</div>", unsafe_allow_html=True)
                except Exception as e:
                    st.error("Không thể kết nối AI. Kiểm tra lại API Key trong Secrets.")
    else:
        st.error("Lỗi: File Excel của bạn phải có cột tên là 'Tiếng Việt' và 'Tiếng Nga'.")
else:
    st.warning("Vui lòng mở menu bên trái (hình 3 gạch) và tải file Excel lên.")
