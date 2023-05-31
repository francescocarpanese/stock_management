import sqlite3

def query_name_str(search_text):
    return f"name LIKE '{search_text}%'"

def query_order_by_name():
    return f"ORDER BY name ASC"

def query_expired():
    return f"expiration < date('now')"

def query_not_expired():
    return f"expiration >= date('now')"

def query_out_stock():
    return f"current_stock = 0"

def query_present():
    return f"current_stock > 0"

def query_base():
    return f"SELECT * FROM drugs"

def query_and():
    return f"AND"

def query_invalid():
    return f"1 = 0"

def search_drug(conn, window, event, values):
    c = conn.cursor()

    search_text = values['-in_name-']

    filters = []
    if search_text:
        filters += [query_name_str(search_text)]
        pass
    # Filter out expired drugs
    if not values['-chx_expired-']:
        filters += [query_not_expired()]

    # Select present and out of stock
    if not values['-chx_out_stock-'] and values['-chx_present-']:
        filters += [query_present()]
    elif values['-chx_out_stock-'] and not values['-chx_present-']:
        filters += [query_out_stock()]
    elif not values['-chx_out_stock-'] and not values['-chx_present-']:
        filters += [query_invalid()]
    
    # Join filters
    if filters:
        filters_str = " AND ".join(filters)
        query_str = " ".join([query_base(),"WHERE",filters_str,query_order_by_name()])
    else:
        query_str = " ".join([query_base(),query_order_by_name()])

    print(query_str)

    c.execute(query_str)
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