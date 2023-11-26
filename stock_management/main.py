import PySimpleGUI as sg
from stock_management.layouts import (
    get_main_layout,
    get_new_drug_layout,
    get_new_movement_layout,
    get_test_layout,
)
import sqlite3
import stock_management.sql_utils as sql_utils
import stock_management.main_win_utils as main_win_utils
import stock_management.drugs_win_utils as drugs_win_utils
import stock_management.movement_win_utils as movement_win_utils
import stock_management.report_win_utils as report_win_utils
import stock_management.tmp_win_utils as tmp_win_utils
import os
from stock_management.create_tables import create_all_tables

# Create database if not existing
path_to_database = "database.db"
if not os.path.exists(path_to_database):
    # Fresh create the tables
    create_all_tables(path_to_database)

layout = get_main_layout()

# Connect to the database
conn = sqlite3.connect(path_to_database)

window = sg.Window("Main", layout)
window.finalize()

rows = main_win_utils.get_all_drugs(conn)
main_win_utils.display_table(window, rows)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif (
        event == "-in_name-"
        or event == "-chx_expired-"
        or event == "-chx_out_stock-"
        or event == "-chx_present-"
    ):
        rows = main_win_utils.search_drug(conn, window, event, values)
        main_win_utils.display_table(window, rows)
    elif event == "-but_new_drug-":
        drugs_win_utils.drug_session(conn)
        main_win_utils.diplay_last_drug(conn, window)
    elif event == "-but_correct_drug":
        # TODO move to function
        if len(values["-list_table-"]) > 0:
            selected_idx = values["-list_table-"][0]
            row = sql_utils.get_row(conn, "drugs", rows[selected_idx][0])
            drug_dict = sql_utils.parse_drug(conn, "drugs", row)
            drugs_win_utils.drug_session(conn, drug_dict)
    elif event == "-but_new_mov-":
        if len(values["-list_table-"]) > 0:
            selected_idx = values["-list_table-"][0]
            row = sql_utils.get_row(conn, "drugs", rows[selected_idx][0])
            drug_dict = sql_utils.parse_drug(conn, "drugs", row)
            movement_win_utils.movement_session(
                conn,
                drug=drug_dict,
            )
            main_win_utils.display_table(window, rows)
    elif event == "-but_report-":
        report_win_utils.report_session(conn)

    elif event == "-but_test-":
        session = tmp_win_utils.TestSession(layout_fun=get_test_layout, win_name="Test")
        session.run()

    if values["-in_name-"] == "":
        rows = main_win_utils.search_drug(conn, window, event, values)
        main_win_utils.display_table(window, rows)


window.close()
conn.close()
