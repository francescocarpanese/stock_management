import PySimpleGUI as sg
from layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import sqlite3
import sql_utils
import main_win_utils
import drugs_win_utils


path_to_database = 'test.db'

layout = get_main_layout()

# Connect to the database
conn = sqlite3.connect(path_to_database)

window = sg.Window('Main', layout)
window.finalize()

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event == '-in_name-':
        rows = main_win_utils.search_drug(conn, window, event, values)
        main_win_utils.display_table(window, event, values, rows)
    elif event == '-but_new_drug-':
        drugs_win_utils.drug_session(conn)
    elif event == '-but_correct_drug':
        # TODO move to function
        if len(values['-list_table-']) > 0:
            selected_idx = values['-list_table-'][0]
            print(rows[selected_idx][0])
            row = sql_utils.get_row(conn, 'drugs', rows[selected_idx][0])
            drug_dict = sql_utils.parse_drug(conn, 'drugs', row)
            drugs_win_utils.drug_session(conn, drug_dict)


    if values['-in_name-'] == '':
        rows = main_win_utils.get_all_drugs(conn, window, event, values)
        main_win_utils.display_table(window, event, values, rows)

        
        
window.close()
conn.close()