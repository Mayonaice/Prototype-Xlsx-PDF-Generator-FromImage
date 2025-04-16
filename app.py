import streamlit as st
import os
import shutil
from datetime import datetime
import pandas as pd
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Image as ReportLabImage
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import uuid
from io import BytesIO
import openpyxl

UPLOAD_FOLDER = 'temp_uploads'
OUTPUT_FOLDER = 'output'

# Buat folder jika belum ada
for folder in [UPLOAD_FOLDER, OUTPUT_FOLDER]:
    os.makedirs(folder, exist_ok=True)

# Konfigurasi MySQL
MYSQL_USERNAME = 'root'
MYSQL_PASSWORD = 'Vadodali2245'
MYSQL_HOST = 'localhost'
MYSQL_DATABASE = 'xlsx_n_pdf_generator_db'

# Setup database MySQL
DATABASE_URL = f"mysql+mysqlconnector://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}/{MYSQL_DATABASE}"
engine = create_engine(DATABASE_URL)

Base = declarative_base()

class ImageRecord(Base):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, autoincrement=True)
    original_name = Column(String(255))
    new_name = Column(String(255))
    upload_date = Column(DateTime)
    description = Column(String(1000))

# Buat tabel jika belum ada
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def generate_excel(records, image_paths):
    # Buat Excel writer
    excel_path = os.path.join(OUTPUT_FOLDER, f'image_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx')
    writer = pd.ExcelWriter(excel_path, engine='openpyxl')
    
    # Buat DataFrame untuk data
    df = pd.DataFrame([{
        'ID': record.id,
        'Original Name': record.original_name,
        'New Name': record.new_name,
        'Upload Date': record.upload_date,
        'Description': record.description
    } for record in records])
    
    # Simpan data ke sheet pertama
    df.to_excel(writer, sheet_name='Data', index=False)
    
    # Buat sheet untuk gambar
    workbook = writer.book
    worksheet = workbook.create_sheet('Images')
    
    # Atur lebar kolom dan tinggi baris
    worksheet.column_dimensions['A'].width = 30
    worksheet.column_dimensions['B'].width = 30
    row_height = 150  # Tinggi baris dalam pixel
    
    # Tambahkan gambar ke Excel
    for idx, (record, img_path) in enumerate(zip(records, image_paths)):
        if os.path.exists(img_path):
            # Atur tinggi baris
            worksheet.row_dimensions[idx * 10 + 2].height = row_height
            
            # Buka dan resize gambar
            img = Image.open(img_path)
            # Resize gambar agar sesuai dengan Excel (200x200 pixels)
            img.thumbnail((200, 200))
            
            # Simpan gambar ke BytesIO
            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='PNG')
            img_byte_arr = img_byte_arr.getvalue()
            
            # Buat gambar untuk Excel
            img = openpyxl.drawing.image.Image(BytesIO(img_byte_arr))
            
            # Atur posisi gambar
            cell = f'A{idx * 10 + 2}'
            img.anchor = cell
            
            # Tambahkan gambar ke worksheet
            worksheet.add_image(img)
            
            # Tambahkan informasi di sebelah gambar
            info_cell = f'B{idx * 10 + 2}'
            worksheet[info_cell] = f"Original Name: {record.original_name}"
            worksheet[f'B{idx * 10 + 3}'] = f"New Name: {record.new_name}"
            worksheet[f'B{idx * 10 + 4}'] = f"Description: {record.description}"
    
    # Simpan file Excel
    writer.close()
    return excel_path

def generate_pdf(records, image_paths):
    pdf_path = os.path.join(OUTPUT_FOLDER, f'image_records_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    
    for record, img_path in zip(records, image_paths):
        if os.path.exists(img_path):
            # Buka gambar
            img = Image.open(img_path)
            img_width, img_height = img.size
            
            # Hitung rasio aspek
            aspect_ratio = img_width / img_height
            
            # Tentukan ukuran maksimum yang diizinkan
            max_width = width - 100  # 50px margin di kiri dan kanan
            max_height = height - 200  # 100px margin di atas dan bawah
            
            # Hitung ukuran baru yang mempertahankan rasio aspek
            if img_width > max_width or img_height > max_height:
                if aspect_ratio > 1:  # Lebar > tinggi
                    new_width = max_width
                    new_height = new_width / aspect_ratio
                else:  # Tinggi >= lebar
                    new_height = max_height
                    new_width = new_height * aspect_ratio
            else:
                new_width = img_width
                new_height = img_height
            
            # Hitung posisi untuk memusatkan gambar
            x = (width - new_width) / 2
            y = height - new_height - 50  # 50px dari atas
            
            # Simpan gambar ke temporary file
            img_temp = "temp_img.png"
            img.save(img_temp)
            
            # Gambar gambar di PDF
            c.drawImage(img_temp, x, y, width=new_width, height=new_height, preserveAspectRatio=True)
            os.remove(img_temp)  # Hapus file temporary
            
            # Tambahkan informasi di bawah gambar
            y -= 30  # Jarak antara gambar dan teks
            c.setFont("Helvetica-Bold", 12)
            
            # Hitung lebar teks untuk memusatkan
            text_width = c.stringWidth("Image Information", "Helvetica-Bold", 12)
            c.drawString((width - text_width) / 2, y, "Image Information")
            y -= 20
            
            c.setFont("Helvetica", 10)
            info_lines = [
                f"Original Name: {record.original_name}",
                f"New Name: {record.new_name}",
                f"Upload Date: {record.upload_date}",
                f"Description: {record.description}"
            ]
            
            for line in info_lines:
                text_width = c.stringWidth(line, "Helvetica", 10)
                c.drawString((width - text_width) / 2, y, line)
                y -= 15
            
            c.showPage()
    
    c.save()
    return pdf_path

def main():
    st.title("Image Upload and Processing System")
    
    # Upload multiple files
    uploaded_files = st.file_uploader("Upload Images", type=['jpg', 'jpeg', 'png'], accept_multiple_files=True)
    
    if uploaded_files:
        # Tampilkan preview gambar
        st.subheader("Uploaded Images")
        cols = st.columns(3)
        for idx, uploaded_file in enumerate(uploaded_files):
            with cols[idx % 3]:
                st.image(uploaded_file, caption=uploaded_file.name, use_column_width=True)
        
        # Form untuk rename dan deskripsi
        st.subheader("Image Details")
        records = []
        image_paths = []
        
        # Buat multiselect untuk memilih gambar yang akan diproses
        selected_files = st.multiselect(
            "Select images to process",
            [file.name for file in uploaded_files],
            default=[file.name for file in uploaded_files]
        )
        
        for uploaded_file in uploaded_files:
            if uploaded_file.name in selected_files:
                with st.expander(f"Details for {uploaded_file.name}"):
                    new_name = st.text_input(f"New name for {uploaded_file.name}", key=f"name_{uploaded_file.name}")
                    description = st.text_area(f"Description for {uploaded_file.name}", key=f"desc_{uploaded_file.name}")
                    
                    if new_name:
                        # Simpan file ke folder sementara
                        temp_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Simpan path gambar
                        image_paths.append(temp_path)
                        
                        # Buat record untuk database
                        records.append({
                            'original_name': uploaded_file.name,
                            'new_name': new_name,
                            'description': description
                        })
        
        if st.button("Process Images") and records:
            session = Session()
            try:
                db_records = []
                for record in records:
                    # Simpan ke database
                    db_record = ImageRecord(
                        original_name=record['original_name'],
                        new_name=record['new_name'],
                        upload_date=datetime.now(),
                        description=record['description']
                    )
                    session.add(db_record)
                    db_records.append(db_record)
                
                session.commit()
                
                # Generate Excel dan PDF
                excel_path = generate_excel(db_records, image_paths)
                pdf_path = generate_pdf(db_records, image_paths)
                
                st.success("Processing completed!")
                
                # Tampilkan tombol download
                col1, col2 = st.columns(2)
                with col1:
                    with open(excel_path, 'rb') as f:
                        st.download_button(
                            "Download Excel",
                            f,
                            file_name=os.path.basename(excel_path),
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                with col2:
                    with open(pdf_path, 'rb') as f:
                        st.download_button(
                            "Download PDF",
                            f,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf"
                        )
                
                # Kosongkan folder sementara
                shutil.rmtree(UPLOAD_FOLDER)
                os.makedirs(UPLOAD_FOLDER)
                
                st.experimental_rerun()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")
                session.rollback()
            finally:
                session.close()

if __name__ == "__main__":
    main() 