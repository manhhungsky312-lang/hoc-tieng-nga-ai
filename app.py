import streamlit as st
import pandas as pd
import os

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ thống Quản lý Từ vựng", layout="wide")

# Đường dẫn file dữ liệu (có thể đổi thành file Excel nếu muốn)
DB_FILE = "data_tu_vung.csv"

# --- CÁC HÀM XỬ LÝ DỮ LIỆU ---
def load_data():
    """Tải dữ liệu từ file CSV, nếu không có thì tạo mới"""
    if os.path.exists(DB_FILE):
        try:
            return pd.read_csv(DB_FILE)
        except:
            return pd.DataFrame(columns=["Từ gốc", "Loại từ", "Nghĩa tiếng Việt", "Ví dụ/Ghi chú"])
    else:
        return pd.DataFrame(columns=["Từ gốc", "Loại từ", "Nghĩa tiếng Việt", "Ví dụ/Ghi chú"])

def save_data(df):
    """Lưu DataFrame vào file CSV với encoding phù hợp tiếng Việt/Nga"""
    df.to_csv(DB_FILE, index=False, encoding="utf-8-sig")

# Khởi tạo dữ liệu vào Session State để ứng dụng chạy mượt
if "df" not in st.session_state:
    st.session_state.df = load_data()

# --- GIAO DIỆN CHÍNH ---
st.title("📚 Quản lý & Học Từ vựng")

# Chia cột: Cột trái nhập liệu, Cột phải hiển thị
col_input, col_display = st.columns([1, 2])

with col_input:
    st.subheader("➕ Thêm từ mới")
    with st.form("input_form", clear_on_submit=True):
        word = st.text_input("Từ gốc (Tiếng Nga/Anh...)")
        word_type = st.selectbox("Loại từ", ["Danh từ", "Động từ", "Tính từ", "Trạng từ", "Cụm từ"])
        meaning = st.text_input("Nghĩa tiếng Việt")
        example = st.text_area("Ví dụ hoặc ghi chú ngữ pháp")
        
        submitted = st.form_submit_button("Lưu vào danh sách")
        if submitted:
            if word and meaning:
                new_data = pd.DataFrame([[word, word_type, meaning, example]], 
                                        columns=st.session_state.df.columns)
                st.session_state.df = pd.concat([st.session_state.df, new_data], ignore_index=True)
                save_data(st.session_state.df)
                st.success(f"Đã thêm: {word}")
                st.rerun()
            else:
                st.warning("Vui lòng nhập từ và nghĩa!")

with col_display:
    st.subheader("🔍 Danh sách từ vựng")
    
    # Bộ lọc tìm kiếm
    search = st.text_input("Tìm kiếm nhanh...", placeholder="Nhập từ hoặc nghĩa cần tìm")
    
    df_to_show = st.session_state.df
    if search:
        df_to_show = df_to_show[
            df_to_show['Từ gốc'].str.contains(search, case=False, na=False) |
            df_to_show['Nghĩa tiếng Việt'].str.contains(search, case=False, na=False)
        ]

    # Hiển thị bảng
    st.dataframe(df_to_show, use_container_width=True, hide_index=False)

    # Nút xóa dòng cuối hoặc xóa dữ liệu lỗi
    if not st.session_state.df.empty:
        if st.button("🗑️ Xóa dòng cuối cùng"):
            st.session_state.df = st.session_state.df.drop(st.session_state.df.index[-1])
            save_data(st.session_state.df)
            st.rerun()

# --- TIỆN ÍCH XUẤT FILE ---
st.divider()
st.write("### Xuất dữ liệu")
csv_data = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
st.download_button(
    label="📥 Tải về file CSV (Dùng được cho Excel)",
    data=csv_data,
    file_name="danh_sach_tu_vung.csv",
    mime="text/csv"
)
