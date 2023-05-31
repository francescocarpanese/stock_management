import sql_utils
import sqlite3
import layouts
import PySimpleGUI as sg
import drugs_win_utils
import time
from common_utils import is_positive_integer, clear_string, parse_dose_units

def save_drug(window,event,values, connection, id=None):
        if not check_entries(window, values):
            return False
        
        drug_string_clean = clear_string(values['-in_drug_name-'])
        name_in, dose_in, units_in = parse_dose_units(drug_string_clean)
        dose = values['-in_dosagem-'] if values['-in_dosagem-'] else dose_in
        units = values['-comb_dosagem-'] if values['-comb_dosagem-'] else units_in

        if id:
            sql_utils.update_drug(
                conn=connection,
                drug_id=id,
                name=name_in,
                dose=dose,
                units=units,
                expiration=values['-in_DATE-'],
                pieces_per_box=values['-in_pieces_in_box-'],
                drug_type=values['-combo_forma-'],
                lote=values['-in_lote-'],
            )                
        else:
            sql_utils.add_drug(
                conn=connection,
                name=name_in,
                dose=dose,
                units=units,
                expiration=values['-in_DATE-'],
                pieces_per_box=values['-in_pieces_in_box-'],
                drug_type=values['-combo_forma-'],
                lote=values['-in_lote-'],
            )

        return True

def fill_drug(
                window,
                drug_name = '',
                dose= '',
                units = '' ,
                expiration= 0 , 
                pieces_per_box= 1 , 
                type='',
                lote='',

            ):
        window['-in_drug_name-'].update(value = drug_name)
        window['-in_dosagem-'].update(value = dose)
        window['-comb_dosagem-'].update(value = units)
        window['-in_DATE-'].update(value = expiration)
        window['-in_pieces_in_box-'].update(value = pieces_per_box)
        window['-combo_forma-'].update(value = type)
        window['-in_lote-'].update(value = lote)


def check_entries(window, values):
    error_msg = ''
    if values['-in_drug_name-'] == '':
        error_msg += '\nInserir nome do medicamento'    
    if values['-in_DATE-'] == '':
        error_msg += '\nInserir data expiracao'
    if not is_positive_integer(values['-in_pieces_in_box-']):
        error_msg += f'\nNumero de pecas dentro uma caiza tem que ser un numero >0'
    if error_msg != '':
        sg.popup(error_msg)
        return False
    return True

      
def drug_session(
          db_connection,
          drug=None,
          test_events=[],
          test_args=[],
          timeout=None,
          ):
    '''
    New drug
    '''
    layout = layouts.get_new_drug_layout() 
    window = sg.Window('Drug', layout)
    window.finalize()

    drug_id = None

    if drug:
        drugs_win_utils.fill_drug(
            window=window,
            drug_name = drug['name'],
            dose= drug['dose'],
            units = drug['units'],
            expiration= drug['expiration'], 
            pieces_per_box= drug['pieces_per_box'], 
            type=drug['type'],
            lote=drug['lote']
        )
        drug_id = drug['id']

    tstart = time.time()
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break
        elif event=='-but_save_new_drug-':
            if drugs_win_utils.save_drug(window,event,values,db_connection, id=drug_id):
                break
        elif event=='-but-exit_new_drug-':
            break

        # Timeout for the the window used for testing purposes
        if timeout:
            if time.time()-tstart > timeout:
                break

        # Running automatic events for test purposes
        for ev, arg in zip(test_events, test_args):
            ev(window,event,values,drug_id,arg)

    window.close()
