import PySimpleGUI as sg
from layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import sql_utils

layouts = [
    get_main_layout(),
    get_new_drug_layout(),
    get_new_movement_layout()
]

for lyt in layouts:
    window = sg.Window('My GUI', lyt)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()