"""
Tests for drug window - migrated from PySimpleGUI tests
"""
import sqlite3
import pytest
import os
from datetime import date
import stock_management.sql_utils as sql_utils
import stock_management.drug_utils as drugs_win_utils
from stock_management.create_tables import create_all_tables


@pytest.fixture(scope="module")
def db_connection():
    path_to_database = "test_drug.db"

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


# Check the logic for parsing dose and units
@pytest.mark.parametrize(
    "in_drug, expected_drug",
    [
        (
            dict(
                in_drug_name="test1",
                in_dosagem="500",
                comb_dosagem="ml",
                in_DATE="2025-01-01",
                in_pieces_in_box="1",
                combo_forma="Comprimidos",
                in_lote="kk23",
            ),
            dict(
                name="test 1",
                dose="500",
                units="ml",
                expiration=date(2025, 1, 1),
                pieces_per_box=1,
                type="Comprimidos",
                lote="kk23",
                last_inventory_date=date(1990, 1, 1),
                current_stock=0,
            ),
        ),
        (
            dict(
                in_drug_name="test 100ml",
                in_dosagem="",
                comb_dosagem="",
                in_DATE="2025-01-01",
                in_pieces_in_box="1",
                combo_forma="Comprimidos",
                in_lote="kk23",
            ),
            dict(
                name="test",
                dose="100",
                units="ml",
                expiration=date(2025, 1, 1),
                pieces_per_box=1,
                type="Comprimidos",
                lote="kk23",
                last_inventory_date=date(1990, 1, 1),
                current_stock=0,
            ),
        ),
        (
            dict(
                in_drug_name="test 100ml",
                in_dosagem="500",
                comb_dosagem="",
                in_DATE="2025-01-01",
                in_pieces_in_box="1",
                combo_forma="Comprimidos",
                in_lote="kk23",
            ),
            dict(
                name="test",
                dose="500",
                units="ml",
                expiration=date(2025, 1, 1),
                pieces_per_box=1,
                type="Comprimidos",
                lote="kk23",
                last_inventory_date=date(1990, 1, 1),
                current_stock=0,
            ),
        ),
        (
            dict(
                in_drug_name="test 100ml",
                in_dosagem="500",
                comb_dosagem="cl",
                in_DATE="2025-01-01",
                in_pieces_in_box="1",
                combo_forma="Comprimidos",
                in_lote="kk23",
            ),
            dict(
                name="test",
                dose="500",
                units="cl",
                expiration=date(2025, 1, 1),
                pieces_per_box=1,
                type="Comprimidos",
                lote="kk23",
                last_inventory_date=date(1990, 1, 1),
                current_stock=0,
            ),
        ),
    ],
)
def test_save_new_drug(db_connection, in_drug, expected_drug):
    """Test saving a new drug with various inputs"""
    # Save the drug using the utility function
    success = drugs_win_utils.save_drug(in_drug, db_connection)
    assert success

    # Check the drug was saved in the database
    drug_id = sql_utils.get_last_row_id(db_connection, "drugs")
    drug = sql_utils.get_row(db_connection, "drugs", drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)

    # Remove extra fields
    drug_dict.pop("id")

    assert drug_dict == expected_drug


def test_update_drug(db_connection, drug_id):
    """Test updating an existing drug"""
    # Fetch the drug from the database
    drug = sql_utils.get_row(db_connection, "drugs", drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)

    # Update the drug
    updated_values = {
        "in_drug_name": "test2",
        "in_dosagem": "200",
        "comb_dosagem": "ml",
        "in_DATE": "2025-12-31",
        "in_pieces_in_box": "5",
        "combo_forma": "Ampolla",
        "in_lote": "xyz789",
    }

    success = drugs_win_utils.save_drug(updated_values, db_connection, id=drug_id)
    assert success

    # Fetch the drug again
    drug = sql_utils.get_row(db_connection, "drugs", drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)

    # Check that values were updated
    assert drug_dict["name"] == "test 2"
    assert drug_dict["dose"] == "200"
    assert drug_dict["units"] == "ml"
    assert drug_dict["expiration"] == date(2025, 12, 31)
    assert drug_dict["pieces_per_box"] == 5
    assert drug_dict["type"] == "Ampolla"
    assert drug_dict["lote"] == "xyz789"


def test_check_entries_validation():
    """Test input validation"""
    # Test empty name - should fail
    invalid_values = {
        "in_drug_name": "",
        "in_dosagem": "500",
        "comb_dosagem": "ml",
        "in_DATE": "2025-01-01",
        "in_pieces_in_box": "1",
        "combo_forma": "Comprimidos",
        "in_lote": "kk23",
    }
    is_valid, error_msg = drugs_win_utils.validate_drug_entries(invalid_values)
    assert not is_valid
    assert "nome do medicamento" in error_msg

    # Test invalid pieces_per_box - should fail
    invalid_values2 = {
        "in_drug_name": "test",
        "in_dosagem": "500",
        "comb_dosagem": "ml",
        "in_DATE": "2025-01-01",
        "in_pieces_in_box": "invalid",
        "combo_forma": "Comprimidos",
        "in_lote": "kk23",
    }
    is_valid, error_msg = drugs_win_utils.validate_drug_entries(invalid_values2)
    assert not is_valid
    assert "numero" in error_msg.lower()

    # Test valid values - should pass
    valid_values = {
        "in_drug_name": "test",
        "in_dosagem": "500",
        "comb_dosagem": "ml",
        "in_DATE": "2025-01-01",
        "in_pieces_in_box": "1",
        "combo_forma": "Comprimidos",
        "in_lote": "kk23",
    }
    is_valid, error_msg = drugs_win_utils.validate_drug_entries(valid_values)
    assert is_valid
    assert error_msg == ""
