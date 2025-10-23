"""
Tkinter tests for movement window - migrated from PySimpleGUI tests
"""
import sqlite3
import pytest
import os
from datetime import date
import stock_management.sql_utils as sql_utils
import stock_management.tkinter_movement_win_utils as movement_win_utils
from stock_management.create_tables import create_all_tables


@pytest.fixture(scope="module")
def db_connection():
    path_to_database = "test_mov_tkinter.db"
    # Remove the database if already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

    # Fresh create the tables
    create_all_tables(path_to_database)

    conn = sqlite3.connect(path_to_database)
    yield conn

    conn.close()
    
    # Remove the database
    if os.path.exists(path_to_database):
        os.remove(path_to_database)


@pytest.fixture(scope="function")
def drug_id(db_connection):
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

    yield drug_id


@pytest.fixture(scope="function")
def mov_id(db_connection, drug_id):
    original = {
        "date_movement": date(2023, 1, 1),
        "destination_origin": "Prince Pharma",
        "pieces_moved": 10,
        "movement_type": "entry",
        "signature": "Francesco",
    }
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

    # Update the stock
    movement_win_utils.update_stock(
        db_connection=db_connection,
        pieces_moved=int(original["pieces_moved"]),
        date_movement=str(original["date_movement"]),
        movement_type=original["movement_type"],
        drug_id=drug_id,
    )

    yield movement_id


@pytest.fixture(scope="function")
def single_movement():
    return {
        "in_data_movido": "2025-01-01",
        "in_origin_destiny": "pippo",
        "boxes_moved": "0",
        "pieces_moved": "20",
        "comb_type_mov": "Entrada",
        "in_signature": "Francesco_1",
    }


def test_new_movement_fill(db_connection, drug_id, single_movement):
    """Test creating a new movement"""
    drug = sql_utils.get_row(
        conn=db_connection,
        table_name="drugs",
        id=drug_id,
    )

    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)

    assert drug_dict["current_stock"] == 0

    # Save the movement
    success = movement_win_utils.save_move(
        single_movement, db_connection, drug_dict, None
    )
    assert success

    movement_id = sql_utils.get_last_row_id(db_connection, "movements")
    movement = sql_utils.get_row(db_connection, "movements", movement_id)
    movement_dict = sql_utils.parse_movement(db_connection, "movements", movement)

    movement_dict.pop("entry_datetime")
    movement_dict.pop("drug_id")
    movement_dict.pop("id")

    # Check that the movement has been correctly inserted into the db
    expected = {
        "date_movement": date(2025, 1, 1),
        "destination_origin": "pippo",
        "pieces_moved": 20,
        "movement_type": "entry",
        "signature": "Francesco_1",
    }
    assert movement_dict == expected

    # Check that the stock has been updated correctly
    drug = sql_utils.get_row(db_connection, "drugs", drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)
    assert int(drug_dict["current_stock"]) == 20


@pytest.mark.parametrize(
    "multi_mov",
    [
        [  # Test with multiple movements, no inventory
            {
                "in_data_movido": "2025-01-01",
                "in_origin_destiny": "pippo_1",
                "boxes_moved": "0",
                "pieces_moved": "20",
                "comb_type_mov": "Entrada",
                "in_signature": "Francesco_1",
                "expected_stock": 20,
            },
            {
                "in_data_movido": "2025-01-01",
                "in_origin_destiny": "pippo_2",
                "boxes_moved": "0",
                "pieces_moved": "10",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_2",
                "expected_stock": 10,
            },
            {
                "in_data_movido": "2025-01-01",
                "in_origin_destiny": "pipp_3",
                "boxes_moved": "0",
                "pieces_moved": "2",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 8,
            },
            {
                "in_data_movido": "2025-01-01",
                "in_origin_destiny": "pippo_4",
                "boxes_moved": "0",
                "pieces_moved": "1",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 7,
            },
        ],
        [  # Test with multiple movements, with inventory
            {
                "in_data_movido": "2023-01-01",
                "in_origin_destiny": "pippo_1",
                "boxes_moved": "0",
                "pieces_moved": "20",
                "comb_type_mov": "Inventario",
                "in_signature": "Francesco_1",
                "expected_stock": 20,
            },
            {
                "in_data_movido": "2023-01-02",
                "in_origin_destiny": "pippo_2",
                "boxes_moved": "0",
                "pieces_moved": "10",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_2",
                "expected_stock": 10,
            },
            {
                "in_data_movido": "2023-01-02",
                "in_origin_destiny": "pipp_3",
                "boxes_moved": "0",
                "pieces_moved": "2",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 8,
            },
            {
                "in_data_movido": "2023-01-02",
                "in_origin_destiny": "pippo_4",
                "boxes_moved": "0",
                "pieces_moved": "1",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 7,
            },
        ],
        [  # Test with multiple movements, with inventory after first entry
            {
                "in_data_movido": "2023-01-01",
                "in_origin_destiny": "pippo_1",
                "boxes_moved": "0",
                "pieces_moved": "20",
                "comb_type_mov": "Entrada",
                "in_signature": "Francesco_1",
                "expected_stock": 20,
            },
            {
                "in_data_movido": "2023-01-02",
                "in_origin_destiny": "pippo_2",
                "boxes_moved": "0",
                "pieces_moved": "30",
                "comb_type_mov": "Inventario",
                "in_signature": "Francesco_2",
                "expected_stock": 30,
            },
            {
                "in_data_movido": "2023-01-03",
                "in_origin_destiny": "pipp_3",
                "boxes_moved": "0",
                "pieces_moved": "2",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 28,
            },
            {
                "in_data_movido": "2023-01-04",
                "in_origin_destiny": "pippo_4",
                "boxes_moved": "0",
                "pieces_moved": "1",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 27,
            },
        ],
        [  # Test that the inventory has the highest priority on the same date
            {
                "in_data_movido": "2023-01-01",
                "in_origin_destiny": "pippo_1",
                "boxes_moved": "0",
                "pieces_moved": "20",
                "comb_type_mov": "Entrada",
                "in_signature": "Francesco_1",
                "expected_stock": 20,
            },
            {
                "in_data_movido": "2023-01-02",
                "in_origin_destiny": "pippo_2",
                "boxes_moved": "0",
                "pieces_moved": "30",
                "comb_type_mov": "Inventario",
                "in_signature": "Francesco_2",
                "expected_stock": 30,
            },
            {
                "in_data_movido": "2023-01-02",
                "in_origin_destiny": "pipp_3",
                "boxes_moved": "0",
                "pieces_moved": "2",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 30,
            },
            {
                "in_data_movido": "2023-01-04",
                "in_origin_destiny": "pippo_4",
                "boxes_moved": "0",
                "pieces_moved": "1",
                "comb_type_mov": "Saida",
                "in_signature": "Francesco_3",
                "expected_stock": 29,
            },
        ],
    ],
)
def test_multiple_movements(db_connection, drug_id, multi_mov):
    """Test multiple movements with various scenarios"""
    drug = sql_utils.get_row(
        conn=db_connection,
        table_name="drugs",
        id=drug_id,
    )

    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)

    assert drug_dict["current_stock"] == 0

    for mov in multi_mov:
        expected_stock = mov.pop("expected_stock")
        
        success = movement_win_utils.save_move(
            mov, db_connection, drug_dict, None
        )
        assert success

        # Check that the stock has been updated correctly
        drug = sql_utils.get_row(db_connection, "drugs", drug_id)
        drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)
        assert int(drug_dict["current_stock"]) == expected_stock


def test_update_movement(db_connection, drug_id, mov_id):
    """Test updating an existing movement"""
    drug = sql_utils.get_row(
        conn=db_connection,
        table_name="drugs",
        id=drug_id,
    )

    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)

    movement = sql_utils.get_row(
        conn=db_connection,
        table_name="movements",
        id=mov_id,
    )

    movement_dict = sql_utils.parse_movement(db_connection, "movements", movement)

    # Update the movement
    updated_values = {
        "in_data_movido": "2023-01-02",
        "in_origin_destiny": "Updated Destination",
        "boxes_moved": "0",
        "pieces_moved": "15",
        "comb_type_mov": "Saida",
        "in_signature": "Updated_Signature",
    }

    success = movement_win_utils.save_move(
        updated_values, db_connection, drug_dict, mov_id
    )
    assert success

    # Fetch the movement again
    movement = sql_utils.get_row(db_connection, "movements", mov_id)
    movement_dict = sql_utils.parse_movement(db_connection, "movements", movement)

    # Check that values were updated
    assert movement_dict["date_movement"] == date(2023, 1, 2)
    assert movement_dict["destination_origin"] == "Updated Destination"
    assert movement_dict["pieces_moved"] == 15
    assert movement_dict["movement_type"] == "exit"
    assert movement_dict["signature"] == "Updated_Signature"


def test_check_entries_validation():
    """Test input validation"""
    # Test empty date - should fail
    invalid_values = {
        "in_data_movido": "",
        "in_origin_destiny": "test",
        "boxes_moved": "0",
        "pieces_moved": "10",
        "comb_type_mov": "Entrada",
        "in_signature": "test",
    }
    assert not movement_win_utils.check_entries(invalid_values)

    # Test invalid boxes_moved - should fail
    invalid_values2 = {
        "in_data_movido": "2025-01-01",
        "in_origin_destiny": "test",
        "boxes_moved": "invalid",
        "pieces_moved": "10",
        "comb_type_mov": "Entrada",
        "in_signature": "test",
    }
    assert not movement_win_utils.check_entries(invalid_values2)

    # Test valid values - should pass
    valid_values = {
        "in_data_movido": "2025-01-01",
        "in_origin_destiny": "test",
        "boxes_moved": "0",
        "pieces_moved": "10",
        "comb_type_mov": "Entrada",
        "in_signature": "test",
    }
    assert movement_win_utils.check_entries(valid_values)


def test_get_tot_pieces_moved():
    """Test calculation of total pieces moved"""
    drug = {"pieces_per_box": 10}
    
    # Test with only pieces
    values = {
        "boxes_moved": "0",
        "pieces_moved": "5",
    }
    total = movement_win_utils.get_tot_pieces_moved_casted(values, drug)
    assert total == 5
    
    # Test with only boxes
    values = {
        "boxes_moved": "2",
        "pieces_moved": "0",
    }
    total = movement_win_utils.get_tot_pieces_moved_casted(values, drug)
    assert total == 20
    
    # Test with both boxes and pieces
    values = {
        "boxes_moved": "2",
        "pieces_moved": "5",
    }
    total = movement_win_utils.get_tot_pieces_moved_casted(values, drug)
    assert total == 25
    
    # Test with invalid inputs
    values = {
        "boxes_moved": "invalid",
        "pieces_moved": "",
    }
    total = movement_win_utils.get_tot_pieces_moved_casted(values, drug)
    assert total == 0
