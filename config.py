import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Cek apakah aplikasi berjalan di Streamlit Cloud
IS_STREAMLIT_CLOUD = os.getenv('STREAMLIT_CLOUD', 'false').lower() == 'true'

if IS_STREAMLIT_CLOUD:
    # Konfigurasi untuk Streamlit Cloud (SQLite)
    DATABASE_URL = "sqlite:///app.db"
else:
    # Konfigurasi untuk local development (MySQL)
    DB_CONFIG = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'database': os.getenv('DB_NAME', 'xlsx_n_pdf_generator_db'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', 'Vadodali2245')
    }
    DATABASE_URL = f"mysql+mysqlconnector://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

# Application Configuration
APP_CONFIG = {
    'upload_folder': os.getenv('UPLOAD_FOLDER', 'temp_uploads'),
    'output_folder': os.getenv('OUTPUT_FOLDER', 'output')
}

# Create necessary directories
for folder in [APP_CONFIG['upload_folder'], APP_CONFIG['output_folder']]:
    os.makedirs(folder, exist_ok=True) 