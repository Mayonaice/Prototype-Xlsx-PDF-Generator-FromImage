import mysql.connector
from config import DB_CONFIG

def setup_database():
    try:
        # Connect to MySQL server
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                original_name VARCHAR(255),
                new_name VARCHAR(255),
                upload_date DATETIME,
                description TEXT
            )
        """)
        
        print("Database setup completed successfully!")
        
    except Exception as e:
        print(f"Error setting up database: {str(e)}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    setup_database() 