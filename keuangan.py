import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Keuangan pacar gipa",
                   layout="wide",
                   initial_sidebar_state="collapsed")

st.title("Rekapan Keuangan Ikhtafiaa cantekk")
st.markdown("Biar kamu ngga input manual ya sayangg.")

if 'df_pemasukan' not in st.session_state:
    st.session_state.df_pemasukan = pd.DataFrame(columns=["Waktu", "Jenis Uang", "Jumlah", "Keterangan"])

if 'df_pengeluaran' not in st.session_state:
    st.session_state.df_pengeluaran = pd.DataFrame(columns=["Waktu", "Jenis Uang", "Kategori", "Jumlah", "Keterangan"])

list_jenis_uang = ["BNI", "BCA", "Shopee", "Cash", "Jago", "Gopay"]
list_kategori = ["Makanan", "Minuman", "Jajan", "Utility", "Healing", "Lainnya"]


def format_rupiah(angka):
    """Format angka menjadi string Rupiah (Rp 1.000.000)"""
    return f"Rp {angka:,.0f}".replace(",", ".")

def hitung_neraca():
    """Menghitung saldo akhir untuk setiap jenis uang."""
    neraca = pd.DataFrame(index=list_jenis_uang, columns=["Saldo"], data=0.0)
    
    if not st.session_state.df_pemasukan.empty:
        total_pemasukan_per_akun = st.session_state.df_pemasukan.groupby("Jenis Uang")["Jumlah"].sum()
        neraca["Saldo"] = neraca["Saldo"].add(total_pemasukan_per_akun, fill_value=0)
        
    if not st.session_state.df_pengeluaran.empty:
        total_pengeluaran_per_akun = st.session_state.df_pengeluaran.groupby("Jenis Uang")["Jumlah"].sum()
        neraca["Saldo"] = neraca["Saldo"].sub(total_pengeluaran_per_akun, fill_value=0)
        
    return neraca

def handle_submit_pemasukan():
    # Ambil data dari widget form menggunakan 'key'
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
        st.session_state.df_pemasukan = pd.concat(
            [st.session_state.df_pemasukan, new_data], ignore_index=True
        )
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
        st.session_state.df_pengeluaran = pd.concat(
            [st.session_state.df_pengeluaran, new_data], ignore_index=True
        )
        st.success("Pengeluaran berhasil dicatat!")
    else:
        st.error("Jumlah harus lebih besar dari 0.")


tab1, tab2, tab3 = st.tabs(["Dashboard Utama", "Input Transaksi", "Edit/Hapus Data"])

with tab1:
    st.header("Ringkasan Arus Kas Ditaaa")
    
    total_pemasukan = st.session_state.df_pemasukan['Jumlah'].sum()
    total_pengeluaran = st.session_state.df_pengeluaran['Jumlah'].sum()
    sisa_uang = total_pemasukan - total_pengeluaran

    # Tampilkan 3 metrik utama
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
# TAB 2: INPUT TRANSAKSI
# ==============================================================================
with tab2:
    st.header("Isi Transaksi Disini Sayangg")
    
    col_pemasukan, col_pengeluaran = st.columns(2)

    with col_pemasukan:
        st.subheader("Pemasukan")
        # Hubungkan form dengan 'handle_submit_pemasukan' menggunakan on_submit
        with st.form("form_pemasukan", clear_on_submit=True):
            st.date_input("Waktu", key="in_waktu")
            st.selectbox("Jenis Uang", list_jenis_uang, key="in_jenis")
            st.number_input("Jumlah (Rp)", min_value=0, step=1000, key="in_jml") 
            st.text_input("Keterangan", key="in_ket")
            
            # Tombol ini sekarang akan memicu 'handle_submit_pemasukan'
            st.form_submit_button("Simpan Pemasukan", on_click=handle_submit_pemasukan)

    with col_pengeluaran:
        st.subheader("Pengeluaran")
        # Hubungkan form dengan 'handle_submit_pengeluaran'
        with st.form("form_pengeluaran", clear_on_submit=True):
            st.date_input("Waktu", key="out_waktu")
            st.selectbox("Jenis Uang (Sumber)", list_jenis_uang, key="out_jenis")
            st.selectbox("Kategori", list_kategori, key="out_kat")
            st.number_input("Jumlah (Rp)", min_value=0, step=1000, key="out_jml")
            st.text_input("Keterangan", key="out_ket")
            
            st.form_submit_button("Simpan Pengeluaran", on_click=handle_submit_pengeluaran)

# ==============================================================================
# TAB 3: EDIT/HAPUS DATA (FITUR BARU: MODAL EDIT)
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
            # Pilih baris (index) untuk diedit
            idx_to_edit_in = st.number_input(
                "Masukkan Nomor Baris Pemasukan yang mau diedit sayangg", 
                min_value=0, 
                max_value=len(st.session_state.df_pemasukan)-1, 
                step=1, 
                key="idx_edit_in"
            )
            # Tombol ini akan menyimpan 'idx_edit_in' ke session_state untuk memicu dialog
            if st.button("Buka Editor Pemasukan"):
                st.session_state.edit_index_pemasukan = idx_to_edit_in

        with col_del_in:
            # Pilih baris (index) untuk dihapus
            idx_to_del_in = st.number_input(
                "Masukkan Nomor Baris Pemasukan yang mau dihapus sayangg", 
                min_value=0, 
                max_value=len(st.session_state.df_pemasukan)-1, 
                step=1, 
                key="idx_del_in"
            )
            if st.button("Hapus Baris Pemasukan", type="primary"):
                st.session_state.df_pemasukan = st.session_state.df_pemasukan.drop(
                    index=idx_to_del_in
                ).reset_index(drop=True)
                st.success(f"Baris {idx_to_del_in} telah dihapus.")
                st.rerun() # Muat ulang agar perubahan terlihat

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
                st.session_state.df_pengeluaran = st.session_state.df_pengeluaran.drop(
                    index=idx_to_del_out
                ).reset_index(drop=True)
                st.success(f"Baris {idx_to_del_out} telah dihapus.")
                st.rerun()

# 5. Logika Modal (st.dialog)
# ==============================================================================
# Ini adalah "jendela pop-up" yang Anda minta.
# Logika ini akan berjalan jika 'edit_index_pemasukan' ada di session_state

# --- Dialog untuk Pemasukan ---
if 'edit_index_pemasukan' in st.session_state:
    @st.dialog("Edit Transaksi Pemasukan")
    def edit_pemasukan_dialog():
        index = st.session_state.edit_index_pemasukan
        # Ambil data baris yang ada
        row_data = st.session_state.df_pemasukan.iloc[index]

        st.info(f"Anda sedang mengedit data baris ke-{index}")

        # Buat form di dalam dialog, isi dengan data yang ada
        waktu = st.date_input("Waktu", value=row_data["Waktu"])
        
        # Cari index default untuk selectbox
        try:
            default_index_jenis = list_jenis_uang.index(row_data["Jenis Uang"])
        except ValueError:
            default_index_jenis = 0 # Default jika tidak ditemukan

        jenis_uang = st.selectbox("Jenis Uang", list_jenis_uang, index=default_index_jenis)
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000, value=row_data["Jumlah"])
        keterangan = st.text_input("Keterangan", value=row_data["Keterangan"])

        if st.button("Simpan Perubahan"):
            # Update DataFrame di session_state
            st.session_state.df_pemasukan.loc[index, "Waktu"] = waktu
            st.session_state.df_pemasukan.loc[index, "Jenis Uang"] = jenis_uang
            st.session_state.df_pemasukan.loc[index, "Jumlah"] = jumlah
            st.session_state.df_pemasukan.loc[index, "Keterangan"] = keterangan
            
            # Hapus kunci session_state untuk menutup dialog
            del st.session_state.edit_index_pemasukan
            st.success("Data berhasil diperbarui!")
            st.rerun() # Muat ulang untuk melihat perubahan

    edit_pemasukan_dialog()

# --- Dialog untuk Pengeluaran ---
if 'edit_index_pengeluaran' in st.session_state:
    @st.dialog("Edit Transaksi Pengeluaran")
    def edit_pengeluaran_dialog():
        index = st.session_state.edit_index_pengeluaran
        row_data = st.session_state.df_pengeluaran.iloc[index]

        st.info(f"Anda sedang mengedit data baris ke-{index}")

        waktu = st.date_input("Waktu", value=row_data["Waktu"])
        
        try:
            default_index_jenis = list_jenis_uang.index(row_data["Jenis Uang"])
        except ValueError:
            default_index_jenis = 0
            
        try:
            default_index_kat = list_kategori.index(row_data["Kategori"])
        except ValueError:
            default_index_kat = 0

        jenis_uang = st.selectbox("Jenis Uang", list_jenis_uang, index=default_index_jenis)
        kategori = st.selectbox("Kategori", list_kategori, index=default_index_kat)
        jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000, value=row_data["Jumlah"])
        keterangan = st.text_input("Keterangan", value=row_data["Keterangan"])

        if st.button("Simpan Perubahan"):
            st.session_state.df_pengeluaran.loc[index, "Waktu"] = waktu
            st.session_state.df_pengeluaran.loc[index, "Jenis Uang"] = jenis_uang
            st.session_state.df_pengeluaran.loc[index, "Kategori"] = kategori
            st.session_state.df_pengeluaran.loc[index, "Jumlah"] = jumlah
            st.session_state.df_pengeluaran.loc[index, "Keterangan"] = keterangan
            
            del st.session_state.edit_index_pengeluaran
            st.success("Data berhasil diperbarui!")
            st.rerun()

    edit_pengeluaran_dialog()

# --- Tombol Reset ---
if st.sidebar.button("Reset Semua Data", type="primary"):
    st.session_state.df_pemasukan = pd.DataFrame(columns=["Waktu", "Jenis Uang", "Jumlah", "Keterangan"])
    st.session_state.df_pengeluaran = pd.DataFrame(columns=["Waktu", "Jenis Uang", "Kategori", "Jumlah", "Keterangan"])
    st.info("Semua data telah di-reset.")

    st.rerun()
