import stock_management.sql_utils as sql_utils
import pytest
from stock_management.create_tables import create_all_tables
import os
import sqlite3
from datetime import date
from stock_management.movement_win_utils import update_stock
import stock_management.reports_utils as reports_utils
import pandas as pd


@pytest.fixture(scope='module')
def gen_drug_list():
    return [
        ('test_drug', '1', 'l', date(2025,1,1), 1, 'comprimidos', 'a1'),
        ('test_drug2', '1', 'l', date(2025,1,1), 1, 'xerope', 'a2'),
        ('test_drug3', '1', 'l', date(2025,1,1), 1, 'ampulas', 'a3'),
        ('test_drug', '1', 'l', date(2025,2,1), 1, 'comprimidos', 'a4'),
        ('test_drug5', '1', 'l', date(2025,1,1), 1, 'comprimidos', 'a5'),
        ('test_drug6', '1', 'l', date(2025,1,1), 1, 'comprimidos', 'a6'),
        ('test_drug7', '1', 'l', date(2025,1,1), 1, 'comprimidos', 'a7'),
        ('test_drug8', '1', 'l', date(1990,1,1), 1, 'comprimidos', 'a8'),
        ('test_drug9', '1', 'l', date(1990,1,1), 1, 'comprimidos', 'a9'),
    ]

@pytest.fixture(scope='module')
def gen_movement_list():
    return [
        # Entry, Exit , still in stock, on same month
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 1),
        (date(2023,1,2), 'dep1', 1, 'exit', 'Francesco', 1),
        (date(2023,1,2), 'dep2', 1, 'exit', 'Francesco', 1),
        # Same name different ID, entry, exit, still in stock
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 2),
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 4),
        (date(2023,1,2), 'dep1', 1, 'exit', 'Francesco', 4),
        (date(2023,1,2), 'dep2', 2, 'exit', 'Francesco', 2),
        # Entry, exit, inventory, exit still in stock
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 3),
        (date(2023,1,2), 'dep1', 1, 'exit', 'Francesco', 3),
        (date(2023,1,3), 'dep1', 20, 'inventory', 'Francesco', 3),
        (date(2023,1,4), 'dep2', 1, 'exit', 'Francesco', 3),
        # Entry exit in different months, still in stock
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 5),
        (date(2023,1,2), 'dep1', 1, 'exit', 'Francesco', 5),
        (date(2023,2,1), 'dep2', 1, 'exit', 'Francesco', 5),
        # Entry, exit, exit, out of stock
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 6),
        (date(2023,1,2), 'dep1', 1, 'exit', 'Francesco', 6),
        (date(2023,1,2), 'dep2', 10, 'exit', 'Francesco', 6),
        # Entry, exit, exit out of stock, inventory, still in stock
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 7),
        (date(2023,1,2), 'dep1', 1, 'exit', 'Francesco', 7),
        (date(2023,1,2), 'dep2', 10, 'exit', 'Francesco', 7),
        (date(2023,1,3), 'dep2', 20, 'inventory', 'Francesco', 7),
        # Expired drug, Entry, Exit, still in stock
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 8),
        (date(2023,1,2), 'dep1', 1, 'exit', 'Francesco', 8),
        # Entry, exit, exit before the first one still in stock
        (date(2023,1,1), 'Pharma1', 10, 'entry', 'Francesco', 9),
        (date(2023,1,4), 'dep1', 1, 'exit', 'Francesco', 9),
        (date(2023,1,3), 'dep1', 2, 'exit', 'Francesco', 9),
        (date(2023,1,2), 'dep2', 3, 'exit', 'Francesco', 9),
    ]

@pytest.fixture(scope='module')
def db_connection(gen_drug_list, gen_movement_list):
    path_to_database = 'test_report.db'
    # Remove the databse is already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

    # Fresh create the tables
    create_all_tables(path_to_database)

    conn =  sqlite3.connect(path_to_database)
    gen_db(conn, gen_drug_list, gen_movement_list)

    yield conn

    conn.close()

def gen_db(db_connection, drug_list, movement_list):     
    # Add some drugs
    for drug in drug_list:
        sql_utils.add_drug(
            conn=db_connection,
            name=drug[0],
            dose=drug[1],
            units=drug[2],
            expiration=drug[3],
            pieces_per_box=drug[4],
            drug_type=drug[5],
            lote=drug[6],
        )

    # Add some movements
    for movement in movement_list:
        sql_utils.add_movement(
            conn=db_connection,
            date_movement=movement[0],
            destination_origin=movement[1],
            pieces_moved=movement[2],
            movement_type=movement[3],
            signature=movement[4],
            drug_id=movement[5],
        )

        update_stock(
            db_connection=db_connection,
            pieces_moved=movement[2],
            date_movement=movement[0].strftime('%Y-%m-%d'),
            movement_type=movement[3],
            drug_id=movement[5],
            )

@pytest.fixture(scope='function')
def df_drugs(db_connection):
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    return df_drugs

@pytest.fixture(scope='function')
def df_movs(db_connection):
    df_movs = sql_utils.get_all_movements_df(db_connection)
    return df_movs


@pytest.fixture(scope='function')
def df_consumption_ID(db_connection):
    # Generate consumption full period
    df_movements = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    cumulative_result = reports_utils.add_cum_stock_df(df_movements)
    df_consumption_ID = reports_utils.compute_consumption_agg_drug_ID(df_drugs, cumulative_result, date(1990,1,1), date(2100,1,31))
    return df_consumption_ID

def test_get_all_df(db_connection, gen_drug_list, gen_movement_list):
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    df_movements = sql_utils.get_all_movements_df(db_connection)

    assert df_drugs.shape[0] == len(gen_drug_list)
    assert df_movements.shape[0] == len(gen_movement_list)

def test_add_cum_stock_df(df_movs, store_csv=False):
    path_to_csv = 'test_data/test_cum_stock_agg.csv'
    cumulative_result = reports_utils.add_cum_stock_df(df_movs)
    if store_csv:
        # Store in file for debugging
        cumulative_result.to_csv(path_to_csv)
    
    comulative_result_expected = pd.read_csv(path_to_csv, index_col=0, parse_dates=['date_movement','last_inventory_date','entry_datetime'])
    
    # This field is generated with the dataset
    comulative_result_expected['entry_datetime'] = cumulative_result['entry_datetime']
    diff = cumulative_result.compare( comulative_result_expected)
    assert diff.empty
    

def test_compute_consumption_per_ID(db_connection):
    df_movements = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    cumulative_result = reports_utils.add_cum_stock_df(df_movements)
    df_consumption_ID = reports_utils.compute_consumption_agg_drug_ID(df_drugs, cumulative_result, date(2023,1,1), date(2023,1,31))

    pass


def test_gen_consumption_per_ID_txt(db_connection, df_drugs, df_consumption_ID):
    file_name = 'test_consumption_per_ID.txt'
    _, agg_ID_path, _ = reports_utils.create_folders()
    reports_utils.save_txt_agg_per_ID(
        df_drugs,
        df_consumption_ID,
        folder_path=agg_ID_path,
        file_name=file_name,
        col_mask_mov=['exit', 'entry', 'stock', 'last_inventory_date'],
        col_mask_drug=['name', 'dose', 'units', 'expiration', 'pieces_per_box', 'type', 'lote'],
        )
    
    # Check that the file was created
    assert os.path.exists(os.path.join(agg_ID_path, file_name))

def test_gen_consumption_per_ID_xlsx(db_connection, df_drugs, df_consumption_ID):
    file_name = 'test_consumption_per_ID.xlsx'
    _, agg_ID_path, _ = reports_utils.create_folders()
    reports_utils.save_xlsx_agg_per_ID(
        df_drugs,
        df_consumption_ID,
        folder_path=agg_ID_path,
        file_name=file_name,
        col_mask_mov=['exit', 'entry', 'stock', 'last_inventory_date'],
        col_mask_drug=['name', 'dose', 'units', 'expiration', 'pieces_per_box', 'type', 'lote'],
        )
    
    # Check that the file was created
    assert os.path.exists(os.path.join(agg_ID_path, file_name))

def test_gen_mov_report_per_ID_txt(db_connection):
    df_movements = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    cumulative_result = reports_utils.add_cum_stock_df(df_movements)
    _, agg_ID_path, _ = reports_utils.create_folders()
    file_name = 'test_mov_per_ID.txt'
    reports_utils.save_txt_mov_per_ID(df_drugs,
                                      cumulative_result,
                                      folder_path=agg_ID_path,
                                      file_name=file_name,
                                      )
    # Check that the file was created
    assert os.path.exists(os.path.join(agg_ID_path, 'test_mov_per_ID.txt'))

def pytest_sessionfinish(session, exitstatus):
    # Close the database connection after all tests have finished
    db_connection().close()