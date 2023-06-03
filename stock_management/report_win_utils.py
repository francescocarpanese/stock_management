import stock_management.sql_utils as sql_utils
from  stock_management.layouts import get_report_layout
import PySimpleGUI as sg
import time
from datetime import datetime
from stock_management import reports_utils
import os
from datetime import date

def save_report(window, values, db_connection):
    # TODO need to be clean up
    folder_base_path, agg_ID_path, _ = reports_utils.create_folders()
    df_movements = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    comulative_result = reports_utils.add_cum_stock_df(df_movements)
    df_consumption_ID = reports_utils.compute_consumption_agg_drug_ID(df_drugs, comulative_result, date(1990,1,1), date(2100,1,31))
    reports_utils.save_txt_agg_per_ID(
        df_drugs,
        df_consumption_ID,
        folder_path=agg_ID_path,
        col_mask_mov=['exit', 'entry', 'stock', 'last_inventory_date'],
        col_mask_drug=['name', 'dose', 'units', 'expiration', 'pieces_per_box', 'type', 'lote'],
        )
    reports_utils.save_xlsx_agg_per_ID(
        df_drugs,
        df_consumption_ID,
        folder_path=agg_ID_path,
        col_mask_mov=['exit', 'entry', 'stock', 'last_inventory_date'],
        col_mask_drug=['name', 'dose', 'units', 'expiration', 'pieces_per_box', 'type', 'lote'],
        )
   

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
        if timeout:
            if time.time() - tstat > timeout:
                break
        
        # Running automatic events for test purposes
        for ev, arg in zip(test_events, test_args):
            ev(window, event, values, arg)

    window.close()    

        
