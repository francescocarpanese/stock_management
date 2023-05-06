import PySimpleGUI as sg
from layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import sqlite3
import sql_utils


path_to_database = 'example1.db'

layout = get_main_layout()

# Connect to the database
conn = sqlite3.connect(path_to_database)

window = sg.Window('My GUI', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()
conn.close()