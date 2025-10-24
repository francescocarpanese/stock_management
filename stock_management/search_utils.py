"""
Drug search and formatting utilities - shared business logic
Extracted from tkinter_main_win_utils.py for use across different UIs
"""
import sqlite3
import stock_management.sql_utils as sql_utils
from stock_management.common_utils import add_1k_separator


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


def search_drug(conn, search_text, chx_expired, chx_out_stock, chx_present):
    """
    Search for drugs based on filters
    
    Args:
        conn: database connection
        search_text: text to search in drug names
        chx_expired: include expired drugs
        chx_out_stock: include out of stock drugs
        chx_present: include drugs with stock
    
    Returns:
        list of rows matching the search criteria
    """
    c = conn.cursor()

    filters = []
    if search_text:
        filters += [query_name_str(search_text)]
        
    # Filter out expired drugs
    if not chx_expired:
        filters += [query_not_expired()]

    # Select present and out of stock
    if not chx_out_stock and chx_present:
        filters += [query_present()]
    elif chx_out_stock and not chx_present:
        filters += [query_out_stock()]
    elif not chx_out_stock and not chx_present:
        filters += [query_invalid()]

    # Join filters
    if filters:
        filters_str = " AND ".join(filters)
        query_str = " ".join(
            [query_base(), "WHERE", filters_str, query_order_by_name()]
        )
    else:
        query_str = " ".join([query_base(), query_order_by_name()])

    print(query_str)

    c.execute(query_str)
    rows = c.fetchall()
    c.close()
    return rows


def get_all_drugs(conn):
    """Get all drugs from the database ordered by name"""
    c = conn.cursor()
    c.execute(f"SELECT * FROM drugs ORDER BY name ASC")
    rows = c.fetchall()
    c.close()
    return rows


def format_table_rows(rows):
    """
    Format rows for display in the table
    Adds 1k separator to the stock column (last visible column)
    """
    # Former than last is the total stock.
    # Format the string to add 1k separator.
    # In portughese the 1k separator is the "."
    table_viz = [row[1:-2] + (add_1k_separator(str(row[-2])),) for row in rows]
    return table_viz
