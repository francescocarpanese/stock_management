import sqlite3
import os
from stock_management.create_tables import create_all_tables
from stock_management.common_utils import parse_dose_units

DB_PATH = "stock_management.db"
INPUT_FILE = "assets/drug_list.txt"
DESTINATION_ORIGIN_FILE = "assets/destination_origin.txt"


def init_db():
    # Create tables
    create_all_tables(DB_PATH)
    print(f"Created tables in: {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Read raw drug list
    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
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

    # Read destination_origin list
    try:
        with open(DESTINATION_ORIGIN_FILE, "r", encoding="utf-8") as f:
            dest_lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: Destination origin file not found at {DESTINATION_ORIGIN_FILE}")
        conn.commit()
        conn.close()
        return

    unique_destinations = set()

    print("Processing destination origin list...")
    for line in dest_lines:
        line = line.strip()
        if not line:
            continue
        unique_destinations.add(line)

    print(
        f"Found {len(unique_destinations)} unique destination origins from {len(dest_lines)} lines."
    )

    # Insert into destination_origin table
    dest_count = 0
    for dest in unique_destinations:
        try:
            cursor.execute("INSERT INTO origin_destination (name) VALUES (?)", (dest,))
            dest_count += 1
        except sqlite3.IntegrityError:
            print(f"Duplicate skipped: {dest}")

    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} entries into 'drug_names' table.")
    print(
        f"Successfully inserted {dest_count} entries into 'origin_destination' table."
    )


if __name__ == "__main__":
    init_db()
