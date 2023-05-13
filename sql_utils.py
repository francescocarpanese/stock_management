
from datetime import datetime, date

def add_drug(conn, name, dose, units, expiration, pieces_per_box, drug_type, lote, stock=0):
    c = conn.cursor()
    c.execute('INSERT INTO drugs (name, dose, units, expiration, pieces_per_box, type, lote, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (name, dose, units, expiration, pieces_per_box, drug_type, lote, stock))
    c.close()
    conn.commit()
    
def update_drug(conn, drug_id, name, dose, units, expiration, pieces_per_box, drug_type, lote, stock=0, last_inventory_date=date(1990,1,1)):
    print(f'printing_last_inventory{last_inventory_date}')
    c = conn.cursor()
    c.execute('UPDATE drugs SET  name=?, dose=?, units=?, expiration=?, pieces_per_box=?, type=?, lote=?, stock=?, last_inventory_date=? WHERE id=?', (name, dose, units, expiration, pieces_per_box, drug_type, lote, stock, last_inventory_date, drug_id))
    c.close()
    conn.commit()

def add_movement(conn, date_movement, destination_origin, pieces_moved, movement_type, signature, drug_id):
    c = conn.cursor()
    c.execute('''INSERT INTO movements (date_movement, destination_origin, pieces_moved, movement_type, signature, entry_date, drug_id) 
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', (date_movement, destination_origin, pieces_moved, movement_type, signature, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), drug_id))
    c.close()

def get_first_row_id(conn, table_name):
    c = conn.cursor()
    c.execute('SELECT id FROM {} LIMIT 1'.format(table_name))
    row = c.fetchone()
    c.close()
    if row is not None:
        return row[0]
    else:
        return None

def get_last_row_id(conn, table_name):
    c = conn.cursor()
    c.execute(f"SELECT MAX(id) FROM {table_name}")
    row = c.fetchone()[0]
    c.close()
    return row

def get_table_col_names(conn, table_name):
    # Get the column names of the "drugs" table
    c = conn.cursor()
    c.execute("PRAGMA table_info({})".format(table_name))
    columns = [row[1] for row in c.fetchall()]
    c.close()
    return columns


def get_row(conn, table_name, id):
    c = conn.cursor()
    c.execute(f'SELECT * FROM {table_name} WHERE id = ?', (id,))
    row = c.fetchone()
    c.close()
    return row

def row_to_dict(row, columns):
    row_dict = dict(zip(columns, row))
    row_dict['expiration']= datetime.strptime(row_dict['expiration'], '%Y-%m-%d').date()
    row_dict['last_inventory_date']= datetime.strptime(row_dict['last_inventory_date'], '%Y-%m-%d').date()
    return row_dict

def parse_drug(conn, table_name, row):
    columns = get_table_col_names(conn, table_name)
    return row_to_dict(row, columns)
    