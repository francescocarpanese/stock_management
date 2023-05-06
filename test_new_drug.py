import PySimpleGUI as sg
from layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import sql_utils

layout = get_new_drug_layout()

window = sg.Window('My GUI', layout)


while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    elif event=='-but_save_new_drug':
        pass
    elif event=='-but-exit_new_drug':
        break

window.close()