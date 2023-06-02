import PySimpleGUI as sg
from stock_management.layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import stock_management.sql_utils as sql_utils
import sqlite3
import stock_management.drugs_win_utils as drugs_win_utils
import pytest
from stock_management.create_tables import create_all_tables
import os
import stock_management.movement_win_utils as movement_win_utils
from datetime import date
import time

@pytest.fixture(scope='module')
def db_connection():
    path_to_database = 'test_mov.db'
    # Remove the databse is already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

    # Fresh create the tables
    create_all_tables(path_to_database)

    conn =  sqlite3.connect(path_to_database)
    yield conn

    conn.close()

@pytest.fixture(scope='function')
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

@pytest.fixture(scope='function')
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

    # Update the stock
    movement_win_utils.update_stock(
        db_connection=db_connection,
        pieces_moved=int(original['pieces_moved']),
        date_movement=str(original['date_movement']),
        movement_type=original['movement_type'],
        drug_id=drug_id,
    )

    yield movement_id

@pytest.fixture(scope='function')
def single_movement(db_connection, drug_id):
    return  {
            'date_movement': date(2025, 1,1),
            'destination_origin': 'pippo',
            'pieces_moved': 20,
            'movement_type': 'entry',
            'signature': 'Francesco_1',
    }

def test_new_movement_fill(db_connection, drug_id, single_movement):
    drug = sql_utils.get_row(
        conn=db_connection,
        table_name='drugs',
        id=drug_id,
    )

    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)

    assert drug_dict['current_stock'] == 0

    movement_win_utils.movement_session(
        db_connection=db_connection,
        drug=drug_dict,
        test_events=[
                event_fill_entry,
                event_save,
            ],
        test_args=[single_movement,[]],
        timeout=5,
    )

    movement_id = sql_utils.get_last_row_id(db_connection, 'movements')
    movement = sql_utils.get_row(db_connection, 'movements', movement_id)
    movement_dict = sql_utils.parse_movement(db_connection, 'movements', movement)

    movement_dict.pop('entry_datetime')
    movement_dict.pop('drug_id')
    movement_dict.pop('id')

    # Check that the movement has been correctly inserted into the db
    args = single_movement.copy()
    assert movement_dict == args

    # Check that the stock has been updated correctly
    drug = sql_utils.get_row(db_connection, 'drugs', drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)
    assert int(drug_dict['current_stock']) == args['pieces_moved']


@pytest.mark.parametrize("multi_mov", 
        [
[ # Test with multiple movements, no inventory
        {
            'date_movement': date(2025, 1,1),
            'destination_origin': 'pippo_1',
            'pieces_moved': 20,
            'movement_type': 'entry',
            'signature': 'Francesco_1',
            'current_stock': 20,
        },
        {
            'date_movement': date(2025, 1,1),
            'destination_origin': 'pippo_2',
            'pieces_moved': 10,
            'movement_type': 'exit',
            'signature': 'Francesco_2',
            'current_stock': 10,          
        },
        {
            'date_movement': date(2025, 1,1),
            'destination_origin': 'pipp_3',
            'pieces_moved': 2,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 8,        
        },
        {
            'date_movement': date(2025, 1,1),
            'destination_origin': 'pippo_4',
            'pieces_moved': 1,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 7,        
        }, 
],
[ # Test with multiple movements, with inventory
        {
            'date_movement': date(2023, 1,1),
            'destination_origin': 'pippo_1',
            'pieces_moved': 20,
            'movement_type': 'inventory',
            'signature': 'Francesco_1',
            'current_stock': 20,
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pippo_2',
            'pieces_moved': 10,
            'movement_type': 'exit',
            'signature': 'Francesco_2',
            'current_stock': 10,          
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pipp_3',
            'pieces_moved': 2,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 8,        
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pippo_4',
            'pieces_moved': 1,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 7,        
        }, 
],
[ # Test with multiple movements, with after first entry
        {
            'date_movement': date(2023, 1,1),
            'destination_origin': 'pippo_1',
            'pieces_moved': 20,
            'movement_type': 'entry',
            'signature': 'Francesco_1',
            'current_stock': 20,
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pippo_2',
            'pieces_moved': 30,
            'movement_type': 'inventory',
            'signature': 'Francesco_2',
            'current_stock': 30,          
        },
        {
            'date_movement': date(2023, 1,3),
            'destination_origin': 'pipp_3',
            'pieces_moved': 2,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 28,
        },
        {
            'date_movement': date(2023, 1,4),
            'destination_origin': 'pippo_4',
            'pieces_moved': 1,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 27,        
        }, 
],
[ # Test that the inventory has the highest priority on the same date
        {
            'date_movement': date(2023, 1,1),
            'destination_origin': 'pippo_1',
            'pieces_moved': 20,
            'movement_type': 'entry',
            'signature': 'Francesco_1',
            'current_stock': 20,
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pippo_2',
            'pieces_moved': 30,
            'movement_type': 'inventory',
            'signature': 'Francesco_2',
            'current_stock': 30,          
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pipp_3',
            'pieces_moved': 2,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 30,
        },
        {
            'date_movement': date(2023, 1,4),
            'destination_origin': 'pippo_4',
            'pieces_moved': 1,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 29,        
        }, 
],
[ # Test that entries dates before the last inventory are not condidered
        {
            'date_movement': date(2023, 1,1),
            'destination_origin': 'pippo_1',
            'pieces_moved': 20,
            'movement_type': 'entry',
            'signature': 'Francesco_1',
            'current_stock': 20,
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pippo_2',
            'pieces_moved': 30,
            'movement_type': 'inventory',
            'signature': 'Francesco_2',
            'current_stock': 30,          
        },
        {
            'date_movement': date(2023, 1,2),
            'destination_origin': 'pipp_3',
            'pieces_moved': 2,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 30,
        },
        {
            'date_movement': date(2023, 1,4),
            'destination_origin': 'pippo_4',
            'pieces_moved': 1,
            'movement_type': 'exit',
            'signature': 'Francesco_3',
            'current_stock': 29,        
        },
        {
            'date_movement': date(2023, 1,1),
            'destination_origin': 'pippo_2',
            'pieces_moved': 30,
            'movement_type': 'inventory',
            'signature': 'Francesco_2',
            'current_stock': 29,          
        },
        {
            'date_movement': date(2023, 1,1),
            'destination_origin': 'pippo_2',
            'pieces_moved': 30,
            'movement_type': 'entry',
            'signature': 'Francesco_2',
            'current_stock': 29,          
        },
],
    ]
)
def test_multiple_movements(db_connection, drug_id, multi_mov):
    drug = sql_utils.get_row(
        conn=db_connection,
        table_name='drugs',
        id=drug_id,
    )

    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)

    assert drug_dict['current_stock'] == 0

    for mov in multi_mov:
        movement_win_utils.movement_session(
            db_connection=db_connection,
            drug=drug_dict,
            test_events=[
                    event_fill_entry,
                    event_save,
                ],
            test_args=[mov,[]],
            timeout=5,
        )

        movement_id = sql_utils.get_last_row_id(db_connection, 'movements')
        movement = sql_utils.get_row(db_connection, 'movements', movement_id)
        movement_dict = sql_utils.parse_movement(db_connection, 'movements', movement)

        # Check that the stock has been updated correctly
        drug = sql_utils.get_row(db_connection, 'drugs', drug_id)
        drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)
        assert int(drug_dict['current_stock']) == mov['current_stock']

        # Pop extra fields
        movement_dict.pop('entry_datetime')
        movement_dict.pop('drug_id')
        movement_dict.pop('id')
        mov.pop('current_stock')

        # Check that the movement has been correctly inserted into the db
        assert movement_dict == mov

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
        timeout=2,
    )

    # TODO fill with updated values

    # TODO trigger saving.
    # TODO check the db after triggering save.


# ------- Events --------------
def event_fill_entry(window, event, values, mov_id, movement=[]):
    if movement['movement_type'] == 'entry':
        mov_type = 'Entrada'
    elif movement['movement_type'] == 'exit':
        mov_type = 'Saida'
    elif movement['movement_type'] == 'inventory':
        mov_type = 'Inventario'

    movement_win_utils.fill_mov(
                window=window,
                data_mov=movement['date_movement'],
                orig_dest=movement['destination_origin'],
                n_box=0,
                n_pieces=movement['pieces_moved'],
                mov_type=mov_type,
                signature=movement['signature'],
            )
    window.refresh()

def event_save(window,event,values, mov_id, args=[]):
    print('Event save')
    time.sleep(0.5)
    window.write_event_value('-but_save_mov-', True)    

def event_close_window(window,event,values, mov_id, args=[]):
    time.sleep(5)
    window.write_event_value('-but_exit_mov', True)


def pytest_sessionfinish(session, exitstatus):
    # Close the database connection after all tests have finished
    db_connection().close()