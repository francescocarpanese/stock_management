import sql_utils
import sqlite3


def save_drug(window,event,values, connection):
        sql_utils.add_drug(
            conn=connection,
            name=values['-in_drug_name-'],
            dose=values['-in_dosagem-'],
            units=values['-comb_dosagem-'],
            expiration=values['-in_DATE-'],
            pieces=values['-in_pieces_in_box-'],
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






