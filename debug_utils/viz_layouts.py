# Visualize all the layouts to rapidly debug them

import PySimpleGUI as sg
from stock_management.layouts import (
    get_main_layout,
    get_new_drug_layout,
    get_new_movement_layout,
    get_report_layout,
)
import stock_management.sql_utils as sql_utils

layouts = [
    get_main_layout(),
    get_new_drug_layout(),
    get_new_movement_layout(),
    get_report_layout(),
]

for lyt in layouts:
    window = sg.Window("My GUI", lyt)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
    window.close()
