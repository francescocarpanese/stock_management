import PySimpleGUI as sg
from stock_management.layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import stock_management.sql_utils as sql_utils
import sqlite3
import stock_management.drugs_win_utils as drugs_win_utils
import pytest
from stock_management.create_tables import create_all_tables
import os
from datetime import date
import time

@pytest.fixture(scope='module')
def db_connection():
    path_to_database = 'test_drug.db'

    if not os.path.exists(path_to_database):
       # Fresh create the tables
       create_all_tables(path_to_database)

    conn =  sqlite3.connect(path_to_database)
    yield conn

    conn.close()

    # Remove the databse is already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

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
def one_drug():
    return  {
            'name': 'test1',
            'dose': '500',
            'units': 'ml',
            'expiration': date(2025, 1,1),
            'pieces_per_box': 1,
            'type': 'comprimidos',
            'lote': 'kk23',
    }

# Check the logic for parsing dose and units
@pytest.mark.parametrize("in_drug, expected_drug", [
    (
    dict(name='test1', dose='500', units='ml', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23'),
    dict(name='test 1', dose='500', units='ml', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23', last_inventory_date=date(1990, 1,1), current_stock=0),
    ),
    (
    dict(name='test 100ml', dose='', units='', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23'),
    dict(name='test', dose='100', units='ml', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23', last_inventory_date=date(1990, 1,1), current_stock=0),
    ),
    (
    dict(name='test 100ml', dose='500', units='', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23'),
    dict(name='test', dose='500', units='ml', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23', last_inventory_date=date(1990, 1,1), current_stock=0),
    ),
    (
    dict(name='test 100ml', dose='500', units='cl', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23'),
    dict(name='test', dose='500', units='cl', expiration=date(2025, 1,1), pieces_per_box=1, type='comprimidos', lote='kk23', last_inventory_date=date(1990, 1,1), current_stock=0),
    ),
])
def test_fill_new_drug(db_connection, in_drug, expected_drug):
   
    drugs_win_utils.drug_session(
        db_connection=db_connection,
        test_events=[
            event_fill_drug,
            event_save_drug
        ],
        test_args=[
            in_drug,
            [],
        ],
        timeout=10
        )

    # Check the drug was saved in the database
    drug_id = sql_utils.get_last_row_id(db_connection, 'drugs')
    drug = sql_utils.get_row(db_connection, 'drugs', drug_id)    
    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)
    
    # Remove extra fields
    drug_dict.pop('id')
    
    assert drug_dict == expected_drug   

def test_update_drug_value(db_connection, drug_id, one_drug):
    # Fetch the drug from the database
    drug = sql_utils.get_row(db_connection, 'drugs', drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, 'drugs', drug)

    # Update the drug
    drug_dict['name'] = 'test2'
    pass
    # Fill the drug window
    # Save from the drug window
    # Fetch the drug again
    # Check that the drug was updated


# ------  Events -------
def event_fill_drug(window,event,values,drug_id,drug=[]):
    drugs_win_utils.fill_drug(
        window=window,
        drug_name = drug['name'],
        dose= drug['dose'],
        units = drug['units'],
        expiration= drug['expiration'] , 
        pieces_per_box= drug['pieces_per_box'], 
        type=drug['type'],
        lote=drug['lote']
    )
    window.refresh()

def event_save_drug(window,event,values,drug_id,args=[]):
    print('Event save')
    time.sleep(0.5)
    window.write_event_value('-but_save_new_drug-', True) 


def pytest_sessionfinish(session, exitstatus):
    # Close the database connection after all tests have finished
    db_connection().close()