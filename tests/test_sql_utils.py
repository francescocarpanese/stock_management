import stock_management.sql_utils as sql_utils
from stock_management.create_tables import create_all_tables
import sqlite3
import pytest
import os
from datetime import datetime, date


@pytest.fixture(scope="module")
def db_connection():
    path_to_database = "test_sql.db"
    # Remove the databse is already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

    # Fresh create the tables
    create_all_tables(path_to_database)

    conn = sqlite3.connect(path_to_database)
    yield conn

    conn.close()


def test_add_drug(db_connection):
    sql_utils.add_drug(
        conn=db_connection,
        name="pippo",
        dose="500",
        units="ml",
        expiration=date(2023, 1, 1),
        pieces_per_box=10,
        drug_type="comprimidos",
        lote="a123",
    )

    # TODO check that it was inserted correctly


def test_update_drug(db_connection):
    table_name = "drugs"
    original = {
        "name": "pippo",
        "dose": "100",
        "units": "cl",
        "expiration": date(2023, 1, 1),
        "pieces_per_box": 10,
        "type": "compridos",
        "lote": "a123",
        "current_stock": 0,
        "last_inventory_date": date(2023, 1, 1),
    }
    modified = {
        "name": "franco",
        "dose": "200",
        "units": "ml",
        "expiration": date(2025, 1, 1),
        "pieces_per_box": 20,
        "type": "ampulas",
        "lote": "b123",
        "current_stock": 0,
        "last_inventory_date": date(2025, 1, 2),
    }

    sql_utils.add_drug(
        conn=db_connection,
        name=original["name"],
        dose=original["dose"],
        units=original["units"],
        expiration=original["expiration"],
        pieces_per_box=original["pieces_per_box"],
        drug_type=original["type"],
        lote=original["lote"],
        stock=original["current_stock"],
    )

    id = sql_utils.get_last_row_id(db_connection, table_name)
    sql_utils.update_drug(
        conn=db_connection,
        drug_id=id,
        name=modified["name"],
        dose=modified["dose"],
        units=modified["units"],
        expiration=modified["expiration"],
        pieces_per_box=modified["pieces_per_box"],
        drug_type=modified["type"],
        lote=modified["lote"],
        stock=modified["current_stock"],
        last_inventory_date=modified["last_inventory_date"],
    )

    drug = sql_utils.get_row(
        conn=db_connection,
        table_name=table_name,
        id=id,
    )
    columns = sql_utils.get_table_col_names(db_connection, table_name)
    drug_dict = sql_utils.drug_row_to_dict(drug, columns)
    drug_dict.pop("id")
    assert drug_dict == modified


def test_add_movement(db_connection):
    original = {
        "date_movement": date(2023, 1, 1),
        "destination_origin": "Prince Pharma",
        "pieces_moved": 10,
        "movement_type": "entry",
        "signature": "Francesco",
    }

    # Add a drug to test movement
    sql_utils.add_drug(
        conn=db_connection,
        name="test_mov",
        dose="1",
        units="l",
        expiration=date(2023, 1, 1),
        pieces_per_box=1,
        drug_type="comprimidos",
        lote="a123",
    )

    drug_id = sql_utils.get_last_row_id(db_connection, "drugs")
    original["drug_id"] = drug_id

    sql_utils.add_movement(
        conn=db_connection,
        date_movement=original["date_movement"],
        destination_origin=original["destination_origin"],
        pieces_moved=original["pieces_moved"],
        movement_type=original["movement_type"],
        signature=original["signature"],
        drug_id=drug_id,
    )

    movement_id = sql_utils.get_last_row_id(db_connection, "movements")

    movement = sql_utils.get_row(db_connection, "movements", movement_id)
    movement_dict = sql_utils.parse_movement(db_connection, "movements", movement)

    # Pop filed that are generated automatically
    movement_dict.pop("id")
    movement_dict.pop("entry_datetime")

    assert movement_dict == original


def test_update_movement(db_connection):
    table_name = "movements"
    original = {
        "date_movement": date(2023, 1, 1),
        "destination_origin": "Prince Pharma",
        "pieces_moved": 10,
        "movement_type": "entry",
        "signature": "Francesco",
    }
    modified = {
        "date_movement": date(2025, 1, 1),
        "destination_origin": "pippo",
        "pieces_moved": 20,
        "movement_type": "exit",
        "signature": "Francesco_1",
    }

    sql_utils.add_drug(
        conn=db_connection,
        name="test_mov",
        dose="1",
        units="l",
        expiration=date(2023, 1, 1),
        pieces_per_box=1,
        drug_type="comprimidos",
        lote="a123",
    )

    drug_id = sql_utils.get_last_row_id(db_connection, "drugs")
    original["drug_id"] = drug_id
    modified["drug_id"] = drug_id

    sql_utils.add_movement(
        conn=db_connection,
        date_movement=original["date_movement"],
        destination_origin=original["destination_origin"],
        pieces_moved=original["pieces_moved"],
        movement_type=original["movement_type"],
        signature=original["signature"],
        drug_id=drug_id,
    )

    movement_id = sql_utils.get_last_row_id(db_connection, "movements")

    sql_utils.update_movement(
        conn=db_connection,
        date_movement=modified["date_movement"],
        destination_origin=modified["destination_origin"],
        pieces_moved=modified["pieces_moved"],
        movement_type=modified["movement_type"],
        signature=modified["signature"],
        mov_id=movement_id,
    )

    movement = sql_utils.get_row(db_connection, "movements", movement_id)
    movement_dict = sql_utils.parse_movement(db_connection, "movements", movement)

    # Pop filed that are generated automatically
    movement_dict.pop("id")
    movement_dict.pop("entry_datetime")

    assert movement_dict == modified


def pytest_sessionfinish(session, exitstatus):
    # Close the database connection after all tests have finished
    db_connection().close()
