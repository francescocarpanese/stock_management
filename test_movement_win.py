import PySimpleGUI as sg
from layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import sql_utils
import sqlite3
import drugs_win_utils
import pytest
from create_tables import create_all_tables
import os
import movement_win_utils
from datetime import date
import time

@pytest.fixture(scope='module')
def db_connection():
    path_to_database = 'test.db'
    # Remove the databse is already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

    # Fresh create the tables
    create_all_tables(path_to_database)

    conn =  sqlite3.connect(path_to_database)
    yield conn

    conn.close()

@pytest.fixture(scope='module')
def drug_id(db_connection):
    sql_utils.add_drug(
        conn=db_connection,
        name='test_mov',
        dose='1',
        units='l',
        expiration=date(2023,1,1),
        pieces_per_box=1,
        drug_type='comprimidos',
        lote='a123',
              )
    drug_id = sql_utils.get_last_row_id(db_connection, 'drugs')

    yield drug_id

@pytest.fixture(scope='module')
def mov_id(db_connection, drug_id):
    original = {
            'date_movement': date(2023, 1,1),
            'destination_origin': 'Prince Pharma',
            'pieces_moved': 10,
            'movement_type': 'entry',
            'signature': 'Francesco',
    }
    sql_utils.add_movement(
        conn = db_connection,
        date_movement= original['date_movement'] ,
        destination_origin= original['destination_origin'],
        pieces_moved= original['pieces_moved'],
        movement_type= original['movement_type'], 
        signature= original['signature'], 
        drug_id= drug_id,
    )
    movement_id = sql_utils.get_last_row_id(db_connection, 'movements')

    yield movement_id

def get_modified_mov():
    modified = {
            'date_movement': date(2025, 1,1),
            'destination_origin': 'pippo',
            'pieces_moved': 20,
            'movement_type': 'entry',
            'signature': 'Francesco_1',
    }
    return modified


def test_new_movement_fill(db_connection, drug_id):
    drug = sql_utils.get_row(
        conn=db_connection,
        table_name='drugs',
        id=drug_id,
    )

    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)

    movement_win_utils.movement_session(
        db_connection=db_connection,
        drug=drug_dict,
        test_events=[
                event_fill_entry,
                event_save,
            ],
        timeout=5,
    )

    movement_id = sql_utils.get_last_row_id(db_connection, 'movements')
    movement = sql_utils.get_row(db_connection, 'movements', movement_id)
    movement_dict = sql_utils.parse_movement(db_connection, 'movements', movement)

    movement_dict.pop('entry_datetime')
    movement_dict.pop('drug_id')
    movement_dict.pop('id')

    modified_mov = get_modified_mov()
    assert movement_dict == modified_mov
    

def test_update_movement(db_connection, drug_id, mov_id):
    drug = sql_utils.get_row(
        conn=db_connection,
        table_name='drugs',
        id=drug_id,
    )

    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)

    movement = sql_utils.get_row(
        conn=db_connection,
        table_name='movements',
        id=mov_id,
    )

    movement_dict = sql_utils.parse_movement(db_connection, 'movements', movement)

    movement_win_utils.movement_session(
        db_connection=db_connection,
        drug=drug_dict,
        movement=movement_dict,
        timeout=5
    )



    # TODO trigger saving.
    # TODO check the db after triggering save.


# ------- Events --------------
def event_fill_entry(window, event, values, mov_id):
    print('Fill event')
    modified_mov = get_modified_mov()
    movement_win_utils.fill_mov(
                window=window,
                data_mov=modified_mov['date_movement'],
                orig_dest=modified_mov['destination_origin'],
                n_box=0,
                n_pieces=  modified_mov['pieces_moved'],
                mov_type='Entrada',
                signature=modified_mov['signature'],
            )
    window.refresh()

def event_save(window,event,values, mov_id):
    print('Event save')
    time.sleep(5)
    window.write_event_value('-but_save_mov-', True)    

def event_close_window(window,event,values, mov_id):
    time.sleep(5)
    window.write_event_value('-but_exit_mov', True)


def pytest_sessionfinish(session, exitstatus):
    # Close the database connection after all tests have finished
    db_connection().close()