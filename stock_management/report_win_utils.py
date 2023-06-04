import stock_management.sql_utils as sql_utils
from  stock_management.layouts import get_report_layout
import PySimpleGUI as sg
import time
from datetime import datetime
from stock_management import reports_utils
import os
from datetime import date

def save_report(window, values, db_connection):
    folder_base_path, agg_ID_path, agg_name_path = reports_utils.create_folders()
  
    if not values['-in_data_start-']:
        start_date = date(1990, 1, 1)
    else:
        start_date = datetime.strptime(values['-in_data_start-'], '%Y-%m-%d').date()
    
    if not values['-in_data_end-']:
        end_date = date(2300, 1, 1)
    else:
        end_date = datetime.strptime(values['-in_data_end-'], '%Y-%m-%d').date()

    # Save consumption report grouped by name, dose, type
    try:
        reports_utils.save_xlsx_consumption_nome_dose_type(
            db_connection=db_connection,
            start_date=start_date,
            end_date=end_date,
            folder_path=agg_name_path,
            file_name='consumption_nome_dose_type.xlsx',
        )
    except Exception as e:
        print(e)
        sg.popup_error('Erro ao gerar o relatorio de consumo por nome, dose e tipo')
    
    # Save consumption report grouped by ID (drug with same lote)
    try:
        reports_utils.save_xlsx_consumption_ID(
            db_connection=db_connection,
            start_date=start_date,
            end_date=end_date,
            folder_path=agg_ID_path,
            file_name='consumption_ID.xlsx',
        )
    except Exception as e:
        print(e)
        sg.popup_error('Erro ao gerar o relatorio de consumo por ID')
    
    # Save info for the generated reports
    try:
        reports_utils.save_INFO_txt(
            folder_path=folder_base_path,
            file_name='INFO.txt',
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        print(e)
        sg.popup_error('Erro ao gerar o ficheiro INFO.txt')

    # Dump full database
    try:
        reports_utils.dump_full_dataset(
            db_connection=db_connection,
            folder_path=folder_base_path,
            file_name='dump.xlsx',
        )
    except Exception as e:
        print(e)
        sg.popup_error('Erro ao gerar o dump da base de dados')

    # Save movement report per ID
    try:
        reports_utils.gen_mov_report_ID(
        db_connection=db_connection,
        folder_path=agg_ID_path,
        )
    except Exception as e:
        print(e)
        sg.popup_error('Erro ao gerar o relatorio de movimentos por ID')

    # Save movement report per nome, dose, type
    try:
        reports_utils.gen_mov_report_nome_dose_type(
            db_connection=db_connection,
            folder_path=agg_name_path,
        )
    except Exception as e:
        print(e)
        sg.popup_error('Erro ao gerar o relatorio de movimentos por nome, dose e tipo')

    window['-txt_link_folder-'].update(folder_base_path,
                                       text_color='blue',
                                       visible=True,)

        
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

        
