import sql_utils
import sqlite3
import layouts
import PySimpleGUI as sg
import drugs_win_utils
import time


def save_drug(window,event,values, connection, id=None):
        if id:
            sql_utils.update_drug(
                conn=connection,
                drug_id=id,
                name=values['-in_drug_name-'],
                dose=values['-in_dosagem-'],
                units=values['-comb_dosagem-'],
                expiration=values['-in_DATE-'],
                pieces_per_box=values['-in_pieces_in_box-'],
                drug_type=values['-combo_forma-'],
                lote=values['-in_lote-'],
            )                
        else:
            sql_utils.add_drug(
                conn=connection,
                name=values['-in_drug_name-'],
                dose=values['-in_dosagem-'],
                units=values['-comb_dosagem-'],
                expiration=values['-in_DATE-'],
                pieces_per_box=values['-in_pieces_in_box-'],
                drug_type=values['-combo_forma-'],
                lote=values['-in_lote-'],
            )

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
            drugs_win_utils.save_drug(window,event,values,db_connection, id=drug_id)
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
