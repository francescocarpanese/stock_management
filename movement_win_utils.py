import sql_utils
import sqlite3
import layouts
import PySimpleGUI as sg
import time
import movement_win_utils
import drugs_win_utils

def save_move(window,event,values, connection, drug, movement_id):
        # Add a check for the different entries types
        if values['-comb_type_mov-'] == 'Entrada':
            mov_type = 'entry'
        elif values['-comb_type_mov-'] == 'Saida':
            mov_type = 'exit'
        elif values['-comb_type_mov-'] == 'Saida':
             mov_type = 'inventory'

        pieces_moved = int(values['-pieces_moved-']) + int(values['-boxes_moved-'])*drug['pieces_per_box']

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

        # TODO update the total stock for the drug
        # TODO add the logic to update the stock depending on the inventory date

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


def movement_session(db_connection, drug, movement=None, test_events=[], timeout=None):
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
            movement_win_utils.save_move(window,event,values,db_connection, drug, mov_id)
            break
        elif event=='-but_exit_mov-':
            break
        
        # Implement timeout
        if timeout:
            if time.time()-tstart > timeout:
                break
        
        # Running automatic events for test purposes
        for ev in test_events:
            ev(window,event,values, mov_id)
        

    window.close()