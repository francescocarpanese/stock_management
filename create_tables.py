import sqlite3


def create_all_tables(path_to_database):
    # Connect to the database
    conn = sqlite3.connect(path_to_database)
    c = conn.cursor()

    # Create a table and insert some data
    c.execute('''CREATE TABLE drugs 
        (
            id INTEGER PRIMARY KEY,
            name TEXT,
            dose TEXT,
            units TEXT,
            expiration DATE,
            pieces_per_box INTEGER,
            type TEXT,
            lote TEXT,
            current_stock INTEGER DEFAULT 0,
            last_inventory_date DATE DEFAULT '1990-01-01'
            )
        ''')

    c.execute('''CREATE TABLE movements 
        (
            id INTEGER PRIMARY KEY,
            date_movement DATE,
            destination_origin TEXT,
            pieces_moved INTEGER,
            movement_type TEXT CHECK(movement_type IN ('entry', 'exit', 'inventory')),
            signature TEXT,
            entry_datetime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            drug_id INTEGER,
            FOREIGN KEY (drug_id) REFERENCES drugs(id)
            )
        ''')

    # Store the timestamp of the modification of an entry
    c.execute('''CREATE TRIGGER update_movements_entry_datetime
                    AFTER UPDATE ON movements
                    FOR EACH ROW
                    WHEN OLD.entry_datetime <> CURRENT_TIMESTAMP
                    BEGIN
                    UPDATE movements SET entry_datetime = CURRENT_TIMESTAMP WHERE id = OLD.id;
                    END;
        ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    path_to_database = 'test.db'
    create_all_tables(path_to_database)
