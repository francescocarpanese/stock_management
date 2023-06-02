import sql_utils
import sqlite3
import stock_management.layouts as layouts
import PySimpleGUI as sg
import time
import stock_management.movement_win_utils as movement_win_utils
import stock_management.drugs_win_utils as drugs_win_utils
from datetime import datetime

from stock_management.common_utils import is_positive_null_integer

def compute_new_stock(
        old_stock,
        pieces_moved,
        movement_type, 
        movement_date,
        last_inventory_date,
        last_inventory_stock=0,
        ):
    new_stock = old_stock
    if movement_date > last_inventory_date:
        if movement_type == 'inventory':
            last_inventory_date = movement_date
            new_stock = pieces_moved
            last_inventory_stock = new_stock
        elif movement_type == 'entry':
            new_stock = old_stock + pieces_moved
        elif movement_type == 'exit':
            new_stock = old_stock - pieces_moved
    else:
        new_stock = old_stock
    return max(0., new_stock), last_inventory_date, last_inventory_stock


def update_stock(
        db_connection,
        pieces_moved,
        date_movement,
        movement_type,
        drug_id,
    ):
    # This should be moved directly to the SQL events instead

    drug = sql_utils.get_row(db_connection, 'drugs', drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)

    # Parse to datetime
    date_movement = datetime.strptime(date_movement, '%Y-%m-%d').date()

    new_stock, last_inventory_date,last_inventory_stock = compute_new_stock(
        drug_dict['current_stock'],
        pieces_moved,
        movement_type,
        date_movement,
        drug_dict['last_inventory_date'],
    )
    drug_dict['current_stock'] = new_stock
    drug_dict['last_inventory_date'] = last_inventory_date

    # The inventory has the highest priority for updating the stock on a given date
    sql_utils.update_drug(
        conn=db_connection,
        drug_id=drug_id,
        name=drug_dict['name'],
        dose=drug_dict['dose'],
        units=drug_dict['units'],
        expiration=drug_dict['expiration'],
        pieces_per_box=drug_dict['pieces_per_box'],
        drug_type=drug_dict['type'],
        lote=drug_dict['lote'],
        stock=drug_dict['current_stock'],
        last_inventory_date=drug_dict['last_inventory_date'],
    )


def check_entries(window, values):
    error_msg = ''
    if values['-in_data_movido-'] == '':
        error_msg += '\nInserir data'
    if values['-comb_type_mov-'] == '':
        error_msg += '\nInserir Entrada/Saida/Inventario'
    if not is_positive_null_integer(values['-boxes_moved-']):
        error_msg += f'\nNumero de caixinha tem que ser un numero >=0'
    if not is_positive_null_integer(values['-pieces_moved-']):
        error_msg += f'\nNumero de pecas tem que ser un numero >=0'
    
    if error_msg != '':
        sg.popup(error_msg)
        return False
    return True


def save_move(window,event,values, connection, drug, movement_id):
        
        if not check_entries(window, values):
            return False

        if values['-comb_type_mov-'] == 'Entrada':
            mov_type = 'entry'
        elif values['-comb_type_mov-'] == 'Saida':
            mov_type = 'exit'
        elif values['-comb_type_mov-'] == 'Inventario':
            mov_type = 'inventory'

        pieces_moved = get_tot_pieces_moved_casted(window, values, drug)

        if movement_id:
            sql_utils.update_movement(
                conn = connection,
                date_movement= values['-in_data_movido-'] ,
                destination_origin= values['-in_origin_destiny-'],
                pieces_moved= pieces_moved,
                movement_type= mov_type, 
                signature= values['-in_signature-'], 
                mov_id=movement_id,
            )                
        else:
            sql_utils.add_movement(
                conn = connection,
                date_movement= values['-in_data_movido-'],
                destination_origin= values['-in_origin_destiny-'],
                pieces_moved=  pieces_moved,
                movement_type= mov_type, 
                signature= values['-in_signature-'], 
                drug_id= drug['id'],
            )

        # Update the stock and stock date in drug table
        update_stock(
            connection,
            pieces_moved,
            values['-in_data_movido-'],
            mov_type,
            drug['id'],
              )

        return True

def fill_mov(
                window,
                data_mov='',
                orig_dest='',
                n_box=0,
                n_pieces=0,
                mov_type='',
                signature='',
            ):
    window['-in_data_movido-'].update(value = data_mov)
    window['-in_origin_destiny-'].update(value = orig_dest)
    window['-boxes_moved-'].update(value = n_box)
    window['-pieces_moved-'].update(value = n_pieces)
    window['-comb_type_mov-'].update(mov_type)
    window['-in_signature-'].update(value = signature)


def fill_drug(
                window,
                drug_name = '',
                dose= '',
                units = '' ,
                expiration= '', 
                pieces_per_box= '', 
                type='',
                lote='',
            ):
    window['-txt_drug_name-'].update(value = drug_name)
    window['-txt_dosagem-'].update(value = dose)
    window['-txt_dosagem_unit-'].update(value = units)
    window['-txt_DATE-'].update(value = expiration)
    window['-txt_pieces_in_box-'].update(value = pieces_per_box)
    window['-txt_forma-'].update(value = type)
    window['-txt_lote-'].update(value = lote)               

def fill_win(
                window,
                drug_name = '',
                dose= '',
                units = '' ,
                expiration= '', 
                pieces_per_box= '', 
                type='',
                lote='',
                data_mov='',
                orig_dest='',
                n_box=0,
                n_pieces=0,
                mov_type='',
                signature='',
            ):
    fill_mov(  
        window,
        data_mov= data_mov,
        orig_dest= orig_dest,
        n_box=n_box,
        n_pieces=n_pieces,
        mov_type=mov_type,
        signature=signature,
                )
    
    fill_drug(
        window,
        drug_name = drug_name,
        dose= dose,
        units = units,
        expiration= expiration, 
        pieces_per_box= pieces_per_box, 
        type= type,
        lote=lote,        
    )

def get_tot_pieces_moved_casted(window, values, drug):
    if values['-pieces_moved-'].isdigit() and int( values['-pieces_moved-'])>0:
        pieces_moved = int( values['-pieces_moved-'])
    else:
        pieces_moved = 0
    if values['-boxes_moved-'].isdigit() and int( values['-boxes_moved-'])>0:
        boxes_moved =  int(values['-boxes_moved-'])
    else:
        boxes_moved = 0 

    tot_pieces_moved = pieces_moved + boxes_moved*drug['pieces_per_box']
    return tot_pieces_moved

def update_tot_pieces_moved(window, values, drug):
    tot_pieces_moved = get_tot_pieces_moved_casted(window, values, drug)
    window['-tot_pieces_moved-'].update(value=tot_pieces_moved)

def movement_session(db_connection, drug, movement=None, test_events=[], test_args=[], timeout=None):
    '''
    Movement session
    '''
    layout = layouts.get_new_movement_layout() 
    window = sg.Window('Drug', layout)
    window.finalize()

    mov_id = None
    if movement:
        movement_win_utils.fill_win(
            window=window,
            drug_name = drug['name'],
            dose= drug['dose'],
            units = drug['units'],
            expiration= drug['expiration'], 
            pieces_per_box= drug['pieces_per_box'], 
            type=drug['type'],
            lote=drug['lote'],
            data_mov=movement['date_movement'],
            orig_dest=movement['destination_origin'],
            n_box=0,
            n_pieces=movement['pieces_moved'],
            mov_type=movement['movement_type'],
            signature=movement['signature'],
        )
        mov_id = movement['id']
    else:
        movement_win_utils.fill_drug(
            window=window,
            drug_name = drug['name'],
            dose= drug['dose'],
            units = drug['units'],
            expiration= drug['expiration'], 
            pieces_per_box= drug['pieces_per_box'], 
            type=drug['type'],
            lote=drug['lote']
        )

    tstart = time.time()
    while True:
        event, values = window.read(timeout=100)
        if event == sg.WIN_CLOSED:
            break
        elif event=='-but_save_mov-':
            if movement_win_utils.save_move(window,event,values,db_connection, drug, mov_id):
                break
        elif event=='-but_exit_mov-':
            break
        
        update_tot_pieces_moved(window,values,drug)

        # Timeout for the the window used for testing purposes
        if timeout:
            if time.time()-tstart > timeout:
                break
        
        # Running automatic events for test purposes
        for ev, arg in zip(test_events, test_args):
            ev(window,event,values, mov_id, arg)
        

    window.close()