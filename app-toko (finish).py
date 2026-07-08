import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#import sqlalchemy as sa
from sqlalchemy import create_engine, insert, MetaData, Table, text

# Mari kita buat fungsi untuk menyambungkan koneksi antara Database di SQL dengan Python
def buat_koneksi():
    """Membuat koneksi ke database MySQL tanpa password"""
    try:
        # Menggunakan format user@host tanpa password
        connection_string = 'mysql+mysqlconnector://root:Mysqlopenifl00!@localhost/toko'
        engine = create_engine(connection_string)
        
        # Test koneksi
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        print("Koneksi ke database berhasil")
        return engine
    except Exception as e:
        print(f"Terjadi error koneksi: '{e}'")
        return None

# Di sini kita tulis fungsi untuk menampilkan data dari Database SQL menggunakan Pandas Dataframe
def tampilkan_dataframe(engine):
    try:
        # Ambil koneksi murni (raw connection)
        conn = engine.raw_connection()
        try:
            query = "SELECT * FROM barang ORDER BY id ASC"
            df = pd.read_sql(query, conn)
            
            print("\n===================== DATA BARANG ======================")
            print(df.to_string(index=False))
            return df
        finally:
            # Pastikan koneksi ditutup secara manual agar data tidak bocor
            conn.close()
            
    except Exception as e:
        print(f"Terjadi error: {e}")
        return None

# Di sini mari kita lengkapi fitur agar bisa menambahkan data baru ke dalam Database SQL
def tambah_produk_baru(engine):
    """Menambahkan data produk baru dengan SQLAlchemy 2.0 Core"""
    print("\n=== TAMBAH PRODUK BARU ===")
    try:
        nama = input("Masukkan nama barang: ")
        kategori = input("Masukkan kategori barang: ")
        harga = int(input("Masukkan harga (Rp): "))
        stok = int(input("Masukkan jumlah stok: "))
        ketersediaan = input("Masukkan status ketersediaan: ")
        
        metadata = MetaData()
        # Menggunakan engine untuk autoload tabel
        toko = Table('barang', metadata, autoload_with=engine)
        
        with engine.begin() as conn: # engine.begin() otomatis melakukan commit
            # Di sini kita membuat variabel bernama "penyesuaian" untuk menambahkan kalau ada data tentang produk baru
            penyesuaian = insert(toko).values(
                nama=nama,
                kategori=kategori,
                harga=harga,
                stok=stok,
                ketersediaan=ketersediaan
            )
            result = conn.execute(penyesuaian)
            print(f"\n '{nama}' berhasil ditambahkan!")
            
    except ValueError:
        print("Error: Harga dan stok harus berupa angka")
    except Exception as e:
        print(f"Terjadi error database: {e}")

# Ini fungsi untuk menghitung rata-rata menggunakan Pandas
def hitung_mean(engine):
    """Menghitung nilai mean/rata-rata menggunakan raw_connection"""
    try:
        conn = engine.raw_connection()
        try:
            query = "SELECT * FROM barang"
            df = pd.read_sql(query, conn)
        finally:
            conn.close()
            
        kolom_numerik = df.select_dtypes(include=['int64', 'float64']).columns
        
        print("\nKolom numerik yang tersedia:")
        for i, kolom in enumerate(kolom_numerik[1:], 1):
            print(f"{i}. {kolom}")
            
        pilihan = input("Pilih kolom untuk menghitung mean (masukkan angka): ")
        
        try:
            kolom_terpilih = kolom_numerik[int(pilihan)]
            nilai_mean = df[kolom_terpilih].mean()
            print(f"\nNilai rata-rata dari kolom '{kolom_terpilih}': {nilai_mean:.2f}")
        except (IndexError, ValueError):
            print("Pilihan tidak valid!")
            
    except Exception as e:
        print(f"Terjadi error: '{e}'")

# Biar seru, mari kita lihat data dan angka yang kita punya dalam grafik visualisasi!!
def tampilkan_visualisasi(engine):
    """Menampilkan visualisasi data menggunakan raw_connection"""
    try:
        conn = engine.raw_connection()
        try:
            query = "SELECT * FROM barang"
            df = pd.read_sql(query, conn)
        finally:
            conn.close()
        
        print("\nKolom yang tersedia:")
        for i, kolom in enumerate(df.columns[1:], 1):  # Skip kolom id ya, karena kolom id tidak perlu~
            print(f"{i}. {kolom}")
            
        pilihan = input("Pilih kolom untuk visualisasi (masukkan angka): ")
        
        try:
            kolom_terpilih = df.columns[1:][int(pilihan)-1]
            
            plt.figure(figsize=(10, 6))
            kolom_kategorikal = ['nama', 'kategori', 'ketersediaan'] 
            if kolom_terpilih.lower() in kolom_kategorikal:

                print(f"\nProporsi Kategori pada Kolom '{kolom_terpilih}'")
            
                # Hitung jumlah tiap kategori
                counts = df[kolom_terpilih].value_counts()
                            
                plt.pie(
                    counts.values,
                    labels=counts.index,
                    autopct='%1.1f%%',     # Menampilkan persentase
                    startangle=90,         # Memutar pie agar lebih rapi
                    counterclock=False,    # Urutan searah jarum jam
                    wedgeprops={'edgecolor': 'white'}
                )
            
                plt.title(f'Proporsi {kolom_terpilih}')
                plt.axis('equal')          # Membuat pie berbentuk lingkaran sempurna
                
            else:
                # Nah, kalau untuk data berupa angka, kita pakai histogram ya~
                print(f"\nDistribusi Nilai pada Kolom '{kolom_terpilih}'")
                sns.histplot(df[kolom_terpilih], kde=True)
                plt.title(f'Distribusi {kolom_terpilih}')
                
            plt.tight_layout()
            plt.show()
        except (IndexError, ValueError):
            print("Pilihan tidak valid!")
            
    except Exception as e:
        print(f"Terjadi error: '{e}'")

# Ini adalah fungsi utama ketika Python dijalankan, yaitu berupa menu untuk dipilih~
def main():
    engine = buat_koneksi()
    if not engine: return
    
    try:
        while True:
            # Fungsi ini untuk mengecek pemilihan menu oleh user, serta menjalankan menu
            # sesuai pilihannya menggunakan fungsi-fungsi yang sudah kita persiapkan di atas!
            print("\n1. Lihat Data | 2. Tambah | 3. Rata-rata | 4. Grafik | 5. Keluar")
            menu = input("Pilih menu: ")
            if menu == "1": tampilkan_dataframe(engine)
            elif menu == "2": tambah_produk_baru(engine)
            elif menu == "3": hitung_mean(engine)
            elif menu == "4": tampilkan_visualisasi(engine)
            elif menu == "5": break
    finally:
        engine.dispose()

# Menentukan fungsi yang dijalankan pertama kali ketika Python diakses/dijalankan
if __name__ == "__main__":
    main()