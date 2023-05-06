
from datetime import datetime

def add_drug(conn, name, dose, units, expiration, pieces, drug_type, lote, stock=0):
    c = conn.cursor()
    c.execute('INSERT INTO drugs (name, dose, units, expiration, pieces, type, lote, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (name, dose, units, expiration, pieces, drug_type, lote, stock))
    conn.commit()
    c.close()

def add_movement(conn, date_movement, destination_origin, pieces_moved, movement_type, signature, drug_id):
    c = conn.cursor()
    c.execute('''INSERT INTO movements (date_movement, destination_origin, pieces_moved, movement_type, signature, entry_date, drug_id) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', (date_movement, destination_origin, pieces_moved, movement_type, signature, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), drug_id))
    c.close()