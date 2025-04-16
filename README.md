# Sistem Upload dan Pengolahan Gambar

Aplikasi web untuk mengupload, mengolah, dan mengelola gambar dengan fitur:
- Upload multiple gambar sekaligus
- Preview gambar yang diupload
- Rename dan tambahkan deskripsi untuk setiap gambar
- Simpan data ke database SQLite
- Generate laporan dalam format Excel dan PDF
- Download hasil laporan

## Struktur Folder
- `temp_uploads/`: Folder sementara untuk menyimpan gambar yang diupload
- `output/`: Folder untuk menyimpan file Excel dan PDF yang dihasilkan
- `database/`: Folder untuk menyimpan database SQLite

## Cara Menjalankan

1. Install dependensi:
```bash
pip install -r requirements.txt
```

2. Jalankan aplikasi:
```bash
streamlit run app.py
```

3. Buka browser dan akses `http://localhost:8501`

## Fitur
- Upload multiple gambar (JPG, JPEG, PNG)
- Preview gambar dalam grid 3 kolom
- Form untuk rename dan deskripsi setiap gambar
- Generate laporan Excel dan PDF
- Download hasil laporan
- Reset form setelah proses selesai 