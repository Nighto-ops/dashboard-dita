import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from streamlit_gsheets import GSheetsConnection  # <-- IMPORT BARU

# 1. Konfigurasi Halaman
# ==============================================================================
st.set_page_config(page_title="Keuangan pacar gipa",
                   layout="wide",
                   initial_sidebar_state="collapsed")

# Judul Utama (Milik Anda)
st.title("Rekapan Keuangan Ikhtafiaa cantekk")
st.markdown("Biar kamu ngga input manual ya sayangg.")

# Daftar Opsi (Milik Anda)
list_jenis_uang = ["BNI", "BCA", "Shopee", "Cash", "Jago", "Gopay"]
list_kategori = ["Makanan", "Minuman", "Jajan", "Utility", "Healing", "Lainnya"]
# Definisikan kolom untuk konsistensi
COLS_PEMASUKAN = ["Waktu", "Jenis Uang", "Jumlah", "Keterangan"]
COLS_PENGELUARAN = ["Waktu", "Jenis Uang", "Kategori", "Jumlah", "Keterangan"]

# 2. Koneksi ke Google Sheets
# ==============================================================================
# Ini akan membaca [connections.gsheets] dari Secrets yang akan Anda buat
conn = st.connection("gsheets", type=GSheetsConnection)

# !!! PENTING !!!
# Pastikan Anda memiliki dua "Sheet" (tab) di Google Sheets Anda
# dengan nama persis seperti ini:
NAMA_SHEET_PEMASUKAN = "Pemasukan"
NAMA_SHEET_PENGELUARAN = "Pengeluaran"

# 3. Fungsi Load Data (dari GSheets)
# ==============================================================================
def load_data(worksheet_name, columns):
    """Membaca data dari GSheet dan mengembalikannya sebagai DataFrame."""
    try:
        df = conn.read(worksheet=worksheet_name, usecols=columns, ttl=5)
        df = df.dropna(how="all") # Hapus baris kosong
        # Konversi tipe data
        if "Waktu" in df.columns:
            df["Waktu"] = pd.to_datetime(df["Waktu"], errors='coerce')
        if "Jumlah" in df.columns:
            df["Jumlah"] = pd.to_numeric(df["Jumlah"], errors='coerce')
        return df
    except Exception as e:
        # Jika sheet tidak ada atau kosong, buat DataFrame kosong
        st.warning(f"Tidak dapat menemukan sheet '{worksheet_name}'. Membuat DataFrame baru.")
        return pd.DataFrame(columns=columns)

# 4. Inisialisasi Session State (dari GSheets)
# ==============================================================================
# Ganti inisialisasi lama Anda dengan ini:
# Kita memuat data dari GSheets saat pertama kali dijalankan
if 'df_pemasukan' not in st.session_state:
    st.session_state.df_pemasukan = load_data(NAMA_SHEET_PEMASUKAN, COLS_PEMASUKAN)

if 'df_pengeluaran' not in st.session_state:
    st.session_state.df_pengeluaran = load_data(NAMA_SHEET_PENGELUARAN, COLS_PENGELUARAN)


# 5. Fungsi Pembantu (Helpers) (Kode Anda, tidak berubah)
# ==============================================================================
def format_rupiah(angka):
    """Format angka menjadi string Rupiah (Rp 1.000.000)"""
    return f"Rp {angka:,.0f}".replace(",", ".")

def hitung_neraca():
    """Menghitung saldo akhir untuk setiap jenis uang."""
    # Menggunakan 'list_jenis_uang' Anda
    neraca = pd.DataFrame(index=list_jenis_uang, columns=["Saldo"], data=0.0)
    
    if not st.session_state.df_pemasukan.empty:
        total_pemasukan_per_akun = st.session_state.df_pemasukan.groupby("Jenis Uang")["Jumlah"].sum()
        neraca["Saldo"] = neraca["Saldo"].add(total_pemasukan_per_akun, fill_value=0)
        
    if not st.session_state.df_pengeluaran.empty:
        total_pengeluaran_per_akun = st.session_state.df_pengeluaran.groupby("Jenis Uang")["Jumlah"].sum()
        neraca["Saldo"] = neraca["Saldo"].sub(total_pengeluaran_per_akun, fill_value=0)
        
    return neraca

# 6. Fungsi Callback (Update GSheets)
# ==============================================================================
# Fungsi ini sekarang akan MENULIS ke Google Sheets
def handle_submit_pemasukan():
    waktu_in = st.session_state.in_waktu
    jenis_uang_in = st.session_state.in_jenis
    jumlah_in = st.session_state.in_jml
    keterangan_in = st.session_state.in_ket
    
    if jumlah_in > 0:
        new_data = pd.DataFrame({
            "Waktu": [waktu_in],
            "Jenis Uang": [jenis_uang_in],
            "Jumlah": [jumlah_in],
            "Keterangan": [keterangan_in]
        })
        # 1. Update Session State (Lokal)
        st.session_state.df_pemasukan = pd.concat(
            [st.session_state.df_pemasukan, new_data], ignore_index=True
        )
        # 2. Update Google Sheets (Permanen)
        conn.update(worksheet=NAMA_SHEET_PEMASUKAN, data=st.session_state.df_pemasukan)
        
        st.success("Pemasukan berhasil dicatat!")
    else:
        st.error("Jumlah harus lebih besar dari 0.")

def handle_submit_pengeluaran():
    waktu_out = st.session_state.out_waktu
    jenis_uang_out = st.session_state.out_jenis
    kategori_out = st.session_state.out_kat
    jumlah_out = st.session_state.out_jml
    keterangan_out = st.session_state.out_ket
    
    if jumlah_out > 0:
        new_data = pd.DataFrame({
            "Waktu": [waktu_out],
            "Jenis Uang": [jenis_uang_out],
            "Kategori": [kategori_out],
            "Jumlah": [jumlah_out],
            "Keterangan": [keterangan_out]
        })
        # 1. Update Session State (Lokal)
        st.session_state.df_pengeluaran = pd.concat(
            [st.session_state.df_pengeluaran, new_data], ignore_index=True
        )
        # 2. Update Google Sheets (Permanen)
        conn.update(worksheet=NAMA_SHEET_PENGELUARAN, data=st.session_state.df_pengeluaran)
        
        st.success("Pengeluaran berhasil dicatat!")
    else:
        st.error("Jumlah harus lebih besar dari 0.")


# 7. Layout Aplikasi (Kode Anda, tidak berubah)
# ==============================================================================
# Menggunakan nama tab kustom Anda
tab1, tab2, tab3 = st.tabs(["Dashboard Utama", "Input Transaksi", "Edit/Hapus Data"])

# ==============================================================================
# TAB 1: DASHBOARD UTAMA (Kode Anda, tidak berubah)
# ==============================================================================
with tab1:
    st.header("Ringkasan Arus Kas Ditaaa")
    
    total_pemasukan = st.session_state.df_pemasukan['Jumlah'].sum()
    total_pengeluaran = st.session_state.df_pengeluaran['Jumlah'].sum()
    sisa_uang = total_pemasukan - total_pengeluaran

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Pemasukan", format_rupiah(total_pemasukan))
    col2.metric("Total Pengeluaran", format_rupiah(total_pengeluaran))
    col3.metric("Sisa Uang (Cash Flow)", format_rupiah(sisa_uang))
    
    st.divider()
    col_kiri, col_kanan = st.columns([2, 1])

    with col_kiri:
        st.subheader("Grafik Arus Kas Harian")
        if not st.session_state.df_pemasukan.empty or not st.session_state.df_pengeluaran.empty:
            df_grafik = pd.DataFrame()
            if not st.session_state.df_pemasukan.empty:
                df_pemasukan_copy = st.session_state.df_pemasukan.copy()
                df_pemasukan_copy["Waktu"] = pd.to_datetime(df_pemasukan_copy["Waktu"])
                pemasukan_harian = df_pemasukan_copy.set_index("Waktu").resample("D")["Jumlah"].sum().rename("Pemasukan")
                df_grafik = pd.concat([df_grafik, pemasukan_harian], axis=1)
            if not st.session_state.df_pengeluaran.empty:
                df_pengeluaran_copy = st.session_state.df_pengeluaran.copy()
                df_pengeluaran_copy["Waktu"] = pd.to_datetime(df_pengeluaran_copy["Waktu"])
                pengeluaran_harian = df_pengeluaran_copy.set_index("Waktu").resample("D")["Jumlah"].sum().rename("Pengeluaran")
                df_grafik = pd.concat([df_grafik, pengeluaran_harian], axis=1)
            st.bar_chart(df_grafik.fillna(0))
        else:
            st.info("Belum ada data transaksi untuk ditampilkan di grafik.")
        if not st.session_state.df_pengeluaran.empty:
            st.subheader("Komposisi Pengeluaran")
            df_pie = st.session_state.df_pengeluaran.groupby("Kategori")["Jumlah"].sum().reset_index()
            fig = px.pie(df_pie, values="Jumlah", names="Kategori", title="Berdasarkan Kategori")
            st.plotly_chart(fig, use_container_width=True)
            
    with col_kanan:
        st.subheader("Saldo di Setiap Akun")
        neraca = hitung_neraca()
        neraca_formatted = neraca.copy()
        neraca_formatted["Saldo"] = neraca_formatted["Saldo"].apply(format_rupiah)
        st.dataframe(neraca_formatted, use_container_width=True)

# ==============================================================================
# TAB 2: INPUT TRANSAKSI (Kode Anda, tidak berubah)
# ==============================================================================
with tab2:
    st.header("Isi Transaksi Disini Sayangg")
    
    col_pemasukan, col_pengeluaran = st.columns(2)
    with col_pemasukan:
        st.subheader("Pemasukan")
        with st.form("form_pemasukan", clear_on_submit=True):
            st.date_input("Waktu", key="in_waktu")
            st.selectbox("Jenis Uang", list_jenis_uang, key="in_jenis") # Menggunakan list Anda
            st.number_input("Jumlah (Rp)", min_value=0, step=1000, key="in_jml") 
            st.text_input("Keterangan", key="in_ket")
            st.form_submit_button("Simpan Pemasukan", on_click=handle_submit_pemasukan)
    with col_pengeluaran:
        st.subheader("Pengeluaran")
        with st.form("form_pengeluaran", clear_on_submit=True):
            st.date_input("Waktu", key="out_waktu")
            st.selectbox("Jenis Uang (Sumber)", list_jenis_uang, key="out_jenis") # Menggunakan list Anda
            st.selectbox("Kategori", list_kategori, key="out_kat") # Menggunakan list Anda
            st.number_input("Jumlah (Rp)", min_value=0, step=1000, key="out_jml")
            st.text_input("Keterangan", key="out_ket")
            st.form_submit_button("Simpan Pengeluaran", on_click=handle_submit_pengeluaran)

# ==============================================================================
# TAB 3: EDIT/HAPUS DATA (Modifikasi GSheets)
# ==============================================================================
with tab3:
    st.header("Ringkasan semuanya disini sayangg")
    st.info("Bisa edit atau hapus data yang salah input yaa sayangg.")

    # --- Panel Pemasukan ---
    st.subheader("Data Pemasukan")
    st.dataframe(st.session_state.df_pemasukan, use_container_width=True)
    if not st.session_state.df_pemasukan.empty:
        col_edit_in, col_del_in = st.columns(2)
        with col_edit_in:
            idx_to_edit_in = st.number_input(
                "Masukkan Nomor Baris Pemasukan yang mau diedit sayangg", 
                min_value=0, 
                max_value=len(st.session_state.df_pemasukan)-1, 
                step=1, 
                key="idx_edit_in"
            )
            if st.button("Buka Editor Pemasukan"):
                st.session_state.edit_index_pemasukan = idx_to_edit_in
        with col_del_in:
            idx_to_del_in = st.number_input(
                "Masukkan Nomor Baris Pemasukan yang mau dihapus sayangg", 
                min_value=0, 
                max_value=len(st.session_state.df_pemasukan)-1, 
                step=1, 
                key="idx_del_in"
            )
            if st.button("Hapus Baris Pemasukan", type="primary"):
                # 1. Update Session State
                st.session_state.df_pemasukan = st.session_state.df_pemasukan.drop(
                    index=idx_to_del_in
                ).reset_index(drop=True)
                # 2. Update Google Sheets
                conn.update(worksheet=NAMA_SHEET_PEMASUKAN, data=st.session_state.df_pemasukan)
                st.success(f"Baris {idx_to_del_in} telah dihapus.")
                st.rerun()

    st.divider()

    # --- Panel Pengeluaran ---
    st.subheader("Data Pengeluaran")
    st.dataframe(st.session_state.df_pengeluaran, use_container_width=True)
    if not st.session_state.df_pengeluaran.empty:
        col_edit_out, col_del_out = st.columns(2)
        with col_edit_out:
            idx_to_edit_out = st.number_input(
                "Masukkan Nomor Baris Pengeluaran yang mau diedit sayangg", 
                min_value=0, 
                max_value=len(st.session_state.df_pengeluaran)-1, 
                step=1, 
                key="idx_edit_out"
            )
            if st.button("Buka Editor Pengeluaran"):
                st.session_state.edit_index_pengeluaran = idx_to_edit_out
        with col_del_out:
            idx_to_del_out = st.number_input(
                "Masukkan Nomor Baris Pengeluaran yang mau dihapus sayangg", 
                min_value=0, 
                max_value=len(st.session_state.df_pengeluaran)-1, 
                step=1, 
                key="idx_del_out"
            )
            if st.button("Hapus Baris Pengeluaran", type="primary"):
                # 1. Update Session State
                st.session_state.df_pengeluaran = st.session_state.df_pengeluaran.drop(
                    index=idx_to_del_out
                ).reset_index(drop=True)
                # 2. Update Google Sheets
                conn.update(worksheet=NAMA_SHEET_PENGELUARAN, data=st.session_state.df_pengeluaran)
                st.success(f"Baris {idx_to_del_out} telah dihapus.")
                st.rerun()

# 8. Logika Modal (st.dialog) (Modifikasi GSheets)
# ==============================================================================
# --- Dialog untuk Pemasukan ---
if 'edit_index_pemasukan' in st.session_state:
    @st.dialog("Edit Transaksi Pemasukan")
    def edit_pemasukan_dialog():
        index = st.session_state.edit_index_pemasukan
        row_data = st.session_state.df_pemasukan.iloc[index]
        st.info(f"Anda sedang mengedit data baris ke-{index}")
        
        try:
            waktu_val = row_data["Waktu"].date()
        except:
            waktu_val = datetime.now().date()

        waktu = st.date_input("Waktu", value=waktu_val)
        try:
            default_index_jenis = list_jenis_uang.index(row_data["Jenis Uang"])
        except ValueError:
            default_index_jenis = 0
        jenis_uang = st.selectbox("Jenis Uang", list_jenis_uang, index=default_index_jenis) # Menggunakan list Anda
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000, value=row_data["Jumlah"])
        keterangan = st.text_input("Keterangan", value=row_data["Keterangan"])

        if st.button("Simpan Perubahan"):
            # 1. Update Session State
            st.session_state.df_pemasukan.loc[index, "Waktu"] = pd.to_datetime(waktu)
            st.session_state.df_pemasukan.loc[index, "Jenis Uang"] = jenis_uang
            st.session_state.df_pemasukan.loc[index, "Jumlah"] = jumlah
            st.session_state.df_pemasukan.loc[index, "Keterangan"] = keterangan
            
            # 2. Update Google Sheets
            conn.update(worksheet=NAMA_SHEET_PEMASUKAN, data=st.session_state.df_pemasukan)
            
            del st.session_state.edit_index_pemasukan
            st.success("Data berhasil diperbarui!")
            st.rerun()
    edit_pemasukan_dialog()

# --- Dialog untuk Pengeluaran ---
if 'edit_index_pengeluaran' in st.session_state:
    @st.dialog("Edit Transaksi Pengeluaran")
    def edit_pengeluaran_dialog():
        index = st.session_state.edit_index_pengeluaran
        row_data = st.session_state.df_pengeluaran.iloc[index]
        st.info(f"Anda sedang mengedit data baris ke-{index}")
        
        try:
            waktu_val = row_data["Waktu"].date()
        except:
            waktu_val = datetime.now().date()

        waktu = st.date_input("Waktu", value=waktu_val)
        try:
            default_index_jenis = list_jenis_uang.index(row_data["Jenis Uang"])
        except ValueError:
            default_index_jenis = 0
        try:
            default_index_kat = list_kategori.index(row_data["Kategori"])
        except ValueError:
            default_index_kat = 0
        jenis_uang = st.selectbox("Jenis Uang", list_jenis_uang, index=default_index_jenis) # Menggunakan list Anda
        kategori = st.selectbox("Kategori", list_kategori, index=default_index_kat) # Menggunakan list Anda
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000, value=row_data["Jumlah"])
        keterangan = st.text_input("Keterangan", value=row_data["Keterangan"])

        if st.button("Simpan Perubahan"):
            # 1. Update Session State
            st.session_state.df_pengeluaran.loc[index, "Waktu"] = pd.to_datetime(waktu)
            st.session_state.df_pengeluaran.loc[index, "Jenis Uang"] = jenis_uang
            st.session_state.df_pengeluaran.loc[index, "Kategori"] = kategori
            st.session_state.df_pengeluaran.loc[index, "Jumlah"] = jumlah
            st.session_state.df_pengeluaran.loc[index, "Keterangan"] = keterangan
            
            # 2. Update Google Sheets
            conn.update(worksheet=NAMA_SHEET_PENGELUARAN, data=st.session_state.df_pengeluaran)
            
            del st.session_state.edit_index_pengeluaran
            st.success("Data berhasil diperbarui!")
            st.rerun()
    edit_pengeluaran_dialog()

# --- Tombol Reset (Modifikasi GSheets) ---
if st.sidebar.button("Reset Semua Data", type="primary"):
    # 1. Hapus Session State
    st.session_state.df_pemasukan = pd.DataFrame(columns=COLS_PEMASUKAN)
    st.session_state.df_pengeluaran = pd.DataFrame(columns=COLS_PENGELUARAN)
    
    # 2. Hapus Google Sheets (Clear)
    conn.update(worksheet=NAMA_SHEET_PEMASUKAN, data=st.session_state.df_pemasukan)
    conn.update(worksheet=NAMA_SHEET_PENGELUARAN, data=st.session_state.df_pengeluaran)
    
    st.info("Semua data telah di-reset.")
    st.rerun()
