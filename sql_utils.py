
from datetime import datetime, date
import pandas as pd

def add_drug(conn, name, dose, units, expiration, pieces_per_box, drug_type, lote, stock=0):
    c = conn.cursor()
    c.execute('INSERT INTO drugs (name, dose, units, expiration, pieces_per_box, type, lote, stock) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (name, dose, units, expiration, pieces_per_box, drug_type, lote, stock))
    c.close()
    conn.commit()
    
def update_drug(conn, drug_id, name, dose, units, expiration, pieces_per_box, drug_type, lote, stock=0, last_inventory_date=date(1990,1,1)):
    c = conn.cursor()
    c.execute('UPDATE drugs SET  name=?, dose=?, units=?, expiration=?, pieces_per_box=?, type=?, lote=?, stock=?, last_inventory_date=? WHERE id=?',
               (name, dose, units, expiration, pieces_per_box, drug_type, lote, stock, last_inventory_date, drug_id))
    c.close()
    conn.commit()

def add_movement(conn, date_movement, destination_origin, pieces_moved, movement_type, signature, drug_id):
    c = conn.cursor()
    c.execute('''INSERT INTO movements (date_movement, destination_origin, pieces_moved, movement_type, signature, drug_id) 
                 VALUES (?, ?, ?, ?, ?, ?)''', (date_movement, destination_origin, pieces_moved, movement_type, signature, drug_id))
    c.close()
    conn.commit()

def update_movement(conn, date_movement, destination_origin, pieces_moved, movement_type, signature, mov_id):
    c = conn.cursor()
    c.execute('UPDATE movements SET date_movement=?, destination_origin=?, pieces_moved=?, movement_type=?, signature=? WHERE id=?',
                (date_movement, destination_origin, pieces_moved, movement_type, signature, mov_id))
    c.close()
    conn.commit()

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

def movement_row_to_dict(row, columns):
    row_dict = dict(zip(columns, row))
    row_dict['date_movement'] = datetime.strptime(row_dict['date_movement'], '%Y-%m-%d').date()
    row_dict['entry_datetime'] = datetime.strptime(row_dict['entry_datetime'], '%Y-%m-%d %H:%M:%S')
    return row_dict

def parse_movement(conn,table_name,row):
    columns = get_table_col_names(conn, table_name)
    return movement_row_to_dict(row, columns)

def drug_row_to_dict(row, columns):
    row_dict = dict(zip(columns, row))
    row_dict['expiration']= datetime.strptime(row_dict['expiration'], '%Y-%m-%d').date()
    row_dict['last_inventory_date']= datetime.strptime(row_dict['last_inventory_date'], '%Y-%m-%d').date()
    return row_dict

def parse_drug(conn, table_name, row):
    columns = get_table_col_names(conn, table_name)
    return drug_row_to_dict(row, columns)

def get_all_rows(conn, table_name):
    c = conn.cursor()
    c.execute('SELECT * FROM {}'.format(table_name))
    rows = c.fetchall()
    c.close()
    return rows

def get_all_drugs_df(conn):
    drugs = get_all_rows(conn, 'drugs')
    columns = get_table_col_names(conn, 'drugs')
    df =  pd.DataFrame(drugs, columns=columns)
    df.set_index('id', inplace=True)
    df['expiration'] = df['expiration'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    df['last_inventory_date'] = df['last_inventory_date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    return df

def get_all_movements_df(conn):
    movements = get_all_rows(conn, 'movements')
    columns = get_table_col_names(conn, 'movements')
    df =  pd.DataFrame(movements, columns=columns)
    df.set_index('id', inplace=True)
    df['date_movement'] = df['date_movement'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
    df['entry_datetime'] = df['entry_datetime'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S'))
    return df


