import sqlite3


def search_drug(conn, window, event, values):
    search_text = values['-in_name-']
    c = conn.cursor()
    c.execute(f"SELECT * FROM drugs WHERE name LIKE '{search_text}%' ORDER BY name ASC")
    rows = c.fetchall()
    c.close()
    return rows

def get_all_drugs(conn, window = None, event=None, values=None):
    c = conn.cursor()
    c.execute(f"SELECT * FROM drugs ORDER BY name ASC")
    rows = c.fetchall()
    c.close()
    return rows

def display_table(window, rows=[]):
    table_viz = [row[1:] for row in rows]
    window['-list_table-'].update(values=table_viz) 