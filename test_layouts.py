import PySimpleGUI as sg
from layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import sql_utils


layout = get_main_layout()


window = sg.Window('My GUI', layout)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

window.close()