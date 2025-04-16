import sqlite3
from datetime import datetime
import pandas as pd

def check_sqlite_database():
    try:
        # Connect to SQLite database
        conn = sqlite3.connect('app.db')
        
        # Get table information
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\n=== Database Tables ===")
        for table in tables:
            print(f"\nTable: {table[0]}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print("\nColumns:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            # Get table data
            cursor.execute(f"SELECT * FROM {table[0]};")
            rows = cursor.fetchall()
            print(f"\nTotal rows: {len(rows)}")
            
            if rows:
                print("\nSample data:")
                # Convert to DataFrame for better display
                df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
                print(df.head())
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_sqlite_database() 