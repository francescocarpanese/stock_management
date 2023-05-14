import PySimpleGUI as sg
from layouts import get_main_layout, get_new_drug_layout, get_new_movement_layout
import sql_utils
import sqlite3
import drugs_win_utils
import pytest
from create_tables import create_all_tables
import os


@pytest.fixture(scope='module')
def db_connection():
    path_to_database = 'test.db'

    conn =  sqlite3.connect(path_to_database)
    yield conn

    conn.close()


def test_new_drug(db_connection):
    '''
    Test saving new drug from the GUI
    '''
    layout = get_new_drug_layout()
    window = sg.Window('Test window and save', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        elif event=='-but_save_new_drug':
            drugs_win_utils.save_drug(window,event,values,db_connection)
            break
        # TODO tigger a save event
        # TODO check sql after saving.


    window.close()

def test_fill_drug():
    '''
    Test filling drug data into GUI
    '''
    # TODO parametrize the event. Saving, and exit.
    # TODO check also the update case, not just the new drug

    layout = get_new_drug_layout()
    window = sg.Window('My GUI', layout)
    window.finalize()

    drugs_win_utils.fill_drug(
        window=window,
        drug_name = 'meto',
        dose= 500,
        units = 'ml',
        expiration= 0 , 
        pieces_per_box= 1 , 
        type='comprimidos',
        lote='kk23'
    )

    # TODO check the fields after filling.
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED:
            break
        # TODO trigger a save event
    
    # TODO check sql after saving

    window.close()



def pytest_sessionfinish(session, exitstatus):
    # Close the database connection after all tests have finished
    db_connection().close()