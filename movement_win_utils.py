import sql_utils
import sqlite3
import layouts
import PySimpleGUI as sg
import movement_win_utils



def save_move(window,event,values, connection, drug_id, movement_id):
        # TODO need to be completed for movement
        if movement_id:
            sql_utils.update_move(
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
            sql_utils.add_movem(
                conn=connection,
                name=values['-in_drug_name-'],
                dose=values['-in_dosagem-'],
                units=values['-comb_dosagem-'],
                expiration=values['-in_DATE-'],
                pieces_per_box=values['-in_pieces_in_box-'],
                drug_type=values['-combo_forma-'],
                lote=values['-in_lote-'],
            )


def fill_mov(
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
        window['-txt_drug_name-'].update(value = drug_name)
        window['-txt_dosagem-'].update(value = dose)
        window['-txt_dosagem_unit-'].update(value = units)
        window['-txt_DATE-'].update(value = expiration)
        window['-txt_pieces_in_box-'].update(value = pieces_per_box)
        window['-txt_forma-'].update(value = type)
        window['-txt_lote-'].update(value = lote)
        window['-in_data_movido-'].update(value = data_mov)
        window['-in_origin_destiny-'].update(value = orig_dest)
        window['-boxes_moved-'].update(value = n_box)
        window['-pieces_moved-'].update(value = n_pieces)
        window['-comb_type_mov-'].update(value = mov_type)
        window['-in_signature-'].update(value = signature)


def movement_session(db_connection, drug, movement=None):
    '''
    Movement session
    '''
    layout = layouts.get_new_movement_layout() 
    window = sg.Window('Drug', layout)
    window.finalize()

    move_id = None
    if movement:
        movement_win_utils.fill_drug(
            window=window,
            drug_name = drug['name'],
            dose= drug['dose'],
            units = drug['units'],
            expiration= drug['expiration'], 
            pieces_per_box= drug['pieces_per_box'], 
            type=drug['type'],
            lote=drug['lote'],
            data_mov=movement[''],
            orig_dest=movement[''],
            n_box=movement[''],
            n_pieces=movement[''],
            mov_type=movement[''],
            signature=movement[''],
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

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event=='-but_save_new_drug':
            movement_win_utils.save_mov(window,event,values,db_connection, drug['id'], mov_id = move_id)
            break
        elif event=='-but-exit_new_drug':
            break

    window.close()