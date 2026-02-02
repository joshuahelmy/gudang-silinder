import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# --- KONEKSI DATABASE ---
# Kita tidak menggunakan URL di sini agar sistem membaca dari Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Streamlit akan otomatis mengambil URL dari Secrets yang baru saja Anda simpan
    return conn.read(ttl=0)

import gspread

# Ganti fungsi add_data lama dengan ini
def add_data(new_row):
    # Link ke Google Sheets kamu
    SHEET_URL = "https://docs.google.com/spreadsheets/d/1_PnbYxjwbb_ElF9tgsdGu9_2zqh_AqZ37z5mwMP90ME/edit"
    
    # Menggunakan gspread untuk menulis data secara publik
    # (Pastikan Sheet tetap 'Anyone with the link can EDITOR')
    gc = gspread.public_api()
    sh = gc.open_by_url(SHEET_URL)
    worksheet = sh.get_worksheet(0) # Ambil sheet pertama
    
    # Mengubah dictionary ke list sesuai urutan kolom: 
    # ID, Nama, Stok, Lokasi, Terakhir_Update
    row_to_add = [
        new_row["ID_Barang"], 
        new_row["Nama_Barang"], 
        new_row["Stok"], 
        new_row["Lokasi_Rak"], 
        new_row["Terakhir_Update"]
    ]
    
    worksheet.append_row(row_to_add)

# --- 3. SISTEM LOGIN ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if not st.session_state["password_correct"]:
        st.markdown("## 🏭 Login Gudang")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        
        if st.button("Masuk"):
            if user == "admin" and pwd == "gudang123":
                st.session_state["password_correct"] = True
                st.session_state["user"] = user
                st.rerun()
            else:
                st.error("User atau Password salah.")
        return False
    return True

# --- 4. APLIKASI UTAMA ---
if check_password():
    # Sidebar untuk Logout
    st.sidebar.success(f"Login: {st.session_state['user']}")
    if st.sidebar.button("Logout"):
        st.session_state["password_correct"] = False
        st.rerun()

    st.title("📦 Sistem Manajemen Gudang Online")

    # Ambil Data Terbaru
    try:
        df = get_data()
        df = df.dropna(how="all") # Hapus baris kosong
        if 'Stok' in df.columns:
            df['Stok'] = pd.to_numeric(df['Stok'], errors='coerce').fillna(0)
    except Exception as e:
        st.error(f"Koneksi Gagal. Pastikan Sheet 'Share as Editor'. Error: {e}")
        st.stop()

    tab1, tab2, tab3 = st.tabs(["🔍 Monitoring Stok", "➕ Tambah Barang", "⚙️ Pengaturan"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Item", len(df))
        c2.metric("Total Stok", int(df['Stok'].sum()) if 'Stok' in df.columns else 0)
        
        search = st.text_input("Cari Barang...")
        if search:
            df_display = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]
        else:
            df_display = df
        
        st.dataframe(df_display, use_container_width=True)

    with tab2:
        st.subheader("Input Barang Baru")
        with st.form("input_form"):
            c_a, c_b = st.columns(2)
            id_brg = c_a.text_input("ID Barang")
            nama_brg = c_b.text_input("Nama Barang")
            stok = c_a.number_input("Jumlah", min_value=0)
            lokasi = c_b.text_input("Lokasi Rak")
            
            if st.form_submit_button("Simpan"):
                if id_brg and nama_brg:
                    new_data = {
                        "ID_Barang": id_brg,
                        "Nama_Barang": nama_brg,
                        "Stok": stok,
                        "Lokasi_Rak": lokasi,
                        "Terakhir_Update": datetime.now().strftime("%Y-%m-%d")
                    }
                    add_data(new_data)
                    st.success("Berhasil disimpan!")
                    st.rerun()
                else:
                    st.warning("Isi ID dan Nama!")

    with tab3:
        st.subheader("Pengaturan Database")
        st.info("Fitur Edit/Hapus tersedia jika Anda menggunakan Google Sheets secara langsung.")
        st.write("Akses Database Langsung:")
        st.link_button("Buka Google Sheets", "https://docs.google.com/spreadsheets/d/1_PnbYxjwbb_ElF9tgsdGu9_2zqh_AqZ37z5mwMP90ME/edit")





