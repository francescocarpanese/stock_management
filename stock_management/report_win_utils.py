import stock_management.sql_utils as sql_utils
from  stock_management.layouts import get_report_layout
import PySimpleGUI as sg
import time
from datetime import datetime
from stock_management import reports_utils
import os


def save_report(window, values, db_connection):
    folder_base_path = reports_utils.create_folders()
    window['-txt_link_folder-'].update(folder_base_path,
                                       text_color='blue',
                                       visible=True,)

def check_entries(window, values):
    pass
        
def report_session(
    db_connection,
    test_events=[],
    test_args=[],
    timeout=None,
    ):
    '''
    Report session
    '''
    layout = get_report_layout()
    window = sg.Window('Report', layout)
    window.finalize()

    tstat = time.time()
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break
        elif event == '-but_generate_report-':
            save_report(window, values, db_connection)
        elif event == '-txt_link_folder-':
            report_folder = window['-txt_link_folder-'].get()
            if report_folder and os.path.exists(report_folder):
                os.startfile(report_folder)
            #subprocess.Popen(r'explorer /select,"{}"'.format(folder_path))
        if timeout:
            if time.time() - tstat > timeout:
                break
        
        # Running automatic events for test purposes
        for ev, arg in zip(test_events, test_args):
            ev(window, event, values, arg)

    window.close()    

        
