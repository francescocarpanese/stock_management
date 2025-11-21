import sqlite3
import os
from stock_management.create_tables import create_all_tables
from stock_management.common_utils import parse_dose_units

DB_PATH = "stock_management.db"
INPUT_FILE = "assets/drug_list.txt"

def init_db():
    
    # Create tables
    create_all_tables(DB_PATH)
    print(f"Created tables in: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Read raw drug list
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Input file not found at {INPUT_FILE}")
        return

    unique_names = set()
    
    print("Processing drug list...")
    for line in lines:
        line = line.strip()
        if not line:
            continue
        unique_names.add(line)
    
    print(f"Found {len(unique_names)} unique drug names from {len(lines)} lines.")
    
    # Insert into drug_names table
    count = 0
    for name in unique_names:
        try:
            cursor.execute("INSERT INTO drug_names (name) VALUES (?)", (name,))
            count += 1
        except sqlite3.IntegrityError:
            # Should not happen given we used a set, but good practice
            print(f"Duplicate skipped: {name}")
            
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} entries into 'drug_names' table.")

if __name__ == "__main__":
    init_db()
