import stock_management.sql_utils as sql_utils
import pytest
from stock_management.create_tables import create_all_tables
import os
import sqlite3
from datetime import date, datetime
from stock_management.movement_win_utils import update_stock
import stock_management.reports_utils as reports_utils
import pandas as pd


@pytest.fixture(scope="module")
def gen_drug_list():
    return [
        ("test_drug", "1", "l", date(2025, 1, 1), 1, "comprimidos", "a1"),
        ("test_drug2", "1", "l", date(2025, 1, 1), 1, "xerope", "a2"),
        ("test_drug3", "1", "l", date(2025, 1, 1), 1, "ampulas", "a3"),
        # Same name different expiration date
        ("test_drug", "1", "l", date(2025, 2, 1), 1, "comprimidos", "a4"),
        # Same name different dose
        ("test_drug", "10", "l", date(2025, 1, 1), 1, "comprimidos", "a5"),
        ("test_drug6", "1", "l", date(2025, 1, 1), 1, "comprimidos", "a6"),
        ("test_drug7", "1", "l", date(2025, 1, 1), 1, "comprimidos", "a7"),
        ("test_drug8", "1", "l", date(1990, 1, 1), 1, "comprimidos", "a8"),
        ("test_drug9", "1", "l", date(1990, 1, 1), 1, "comprimidos", "a9"),
    ]


@pytest.fixture(scope="module")
def gen_movement_list():
    return [
        # Entry, Exit , still in stock, on same month
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 1),
        (date(2023, 1, 2), "dep1", 1, "exit", "Francesco", 1),
        (date(2023, 1, 2), "dep2", 1, "exit", "Francesco", 1),
        # Same name different ID, entry, exit, still in stock
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 2),
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 4),
        (date(2023, 1, 2), "dep1", 1, "exit", "Francesco", 4),
        (date(2023, 1, 2), "dep2", 2, "exit", "Francesco", 2),
        # Entry, exit, inventory, exit still in stock
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 3),
        (date(2023, 1, 2), "dep1", 1, "exit", "Francesco", 3),
        (date(2023, 1, 3), "dep1", 20, "inventory", "Francesco", 3),
        (date(2023, 1, 4), "dep2", 1, "exit", "Francesco", 3),
        # Entry exit in different months, still in stock
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 5),
        (date(2023, 1, 2), "dep1", 1, "exit", "Francesco", 5),
        (date(2023, 2, 1), "dep2", 1, "exit", "Francesco", 5),
        # Entry, exit, exit, out of stock
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 6),
        (date(2023, 1, 2), "dep1", 1, "exit", "Francesco", 6),
        (date(2023, 1, 2), "dep2", 10, "exit", "Francesco", 6),
        # Entry, exit, exit out of stock, inventory, still in stock
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 7),
        (date(2023, 1, 2), "dep1", 1, "exit", "Francesco", 7),
        (date(2023, 1, 2), "dep2", 10, "exit", "Francesco", 7),
        (date(2023, 1, 3), "dep2", 20, "inventory", "Francesco", 7),
        # Expired drug, Entry, Exit, still in stock
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 8),
        (date(2023, 1, 2), "dep1", 1, "exit", "Francesco", 8),
        # Entry, exit, exit before the first one still in stock
        (date(2023, 1, 1), "Pharma1", 10, "entry", "Francesco", 9),
        (date(2023, 1, 4), "dep1", 1, "exit", "Francesco", 9),
        (date(2023, 1, 3), "dep1", 2, "exit", "Francesco", 9),
        (date(2023, 1, 2), "dep2", 3, "exit", "Francesco", 9),
    ]


@pytest.fixture(scope="module")
def db_connection(gen_drug_list, gen_movement_list):
    path_to_database = "test_report.db"
    # Remove the databse is already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

    # Fresh create the tables
    create_all_tables(path_to_database)

    conn = sqlite3.connect(path_to_database)
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
            date_movement=movement[0].strftime("%Y-%m-%d"),
            movement_type=movement[3],
            drug_id=movement[5],
        )


@pytest.fixture(scope="function")
def df_drugs(db_connection):
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    return df_drugs


@pytest.fixture(scope="function")
def df_movs(db_connection):
    df_movs = sql_utils.get_all_movements_df(db_connection)
    return df_movs


def test_get_all_df(db_connection, gen_drug_list, gen_movement_list):
    df_drugs = sql_utils.get_all_drugs_df(db_connection)
    df_movs = sql_utils.get_all_movements_df(db_connection)

    assert df_drugs.shape[0] == len(gen_drug_list)
    assert df_movs.shape[0] == len(gen_movement_list)


@pytest.mark.parametrize(
    "groupby_cols",
    [
        (
            [
                "drug_id",
            ]
        ),
        (
            [
                "name",
                "dose",
            ]
        ),
    ],
)
def test_add_cum_stock_df(
    df_drugs,
    df_movs,
    groupby_cols,
    store_csv=False,
    store_xlsx=False,
    gen_test_data=False,
):
    """
    gen_test_data: if True, the test data will be generated and stored in a csv file
    """
    # Merge onto unique dataset
    df_merged = pd.merge(df_movs, df_drugs, on="drug_id", how="left")

    cumulative_result = reports_utils.add_cum_stock_df(
        df_merged, groupby_cols=groupby_cols
    )
    str_gropuby_cols = "_".join(groupby_cols)

    path_to_csv = "test_data/test_cum_stock_agg" + str_gropuby_cols + ".csv"
    if store_csv:
        path_to_csv_tmp = "test_data/tmp_test_cum_stock_agg" + str_gropuby_cols + ".csv"
        # Dump file for testing when test change
        cumulative_result.to_csv(path_to_csv_tmp)
    if store_xlsx:
        path_to_xlsx_tmp = (
            "test_data/tmp_test_cum_stock_agg" + str_gropuby_cols + ".xlsx"
        )
        cumulative_result.to_excel(path_to_xlsx_tmp)

    if gen_test_data:
        # Store the file for testing
        cumulative_result.to_csv(path_to_csv)

    comulative_result_expected = pd.read_csv(
        path_to_csv,
        index_col=0,
        parse_dates=[
            "date_movement",
            "last_inventory_date",
            "entry_datetime",
            "expiration",
        ],
    )

    # TODO clean up. Some custom casting
    cumulative_result["dose"] = cumulative_result["dose"].astype("int")
    # This value is generated at the moment of the dataset generation and will vary
    comulative_result_expected["entry_datetime"] = cumulative_result[
        "entry_datetime"
    ].astype("datetime64[ns]")

    # This field is generated with the dataset
    diff = cumulative_result.compare(comulative_result_expected)
    assert diff.empty


@pytest.mark.parametrize(
    "start_date, end_date, expected_consumption",
    [
        (  # Take all movements
            date(2023, 1, 1),
            date(3000, 1, 31),
            pd.DataFrame(
                [
                    [1, 10, 2, 8, date(1900, 1, 1), None],
                    [2, 10, 2, 8, date(1900, 1, 1), None],
                    [3, 10, 2, 19, date(2023, 1, 3), 20.0],
                    [4, 10, 1, 9, date(1900, 1, 1), None],
                    [5, 10, 2, 8, date(1900, 1, 1), None],
                    [6, 10, 11, 0, date(1900, 1, 1), None],
                    [7, 10, 11, 20, date(2023, 1, 3), 20.0],
                    [8, 10, 1, 9, date(1900, 1, 1), None],
                    [9, 10, 6, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "drug_id",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first 2 days
            date(2000, 1, 1),
            date(2023, 1, 2),
            pd.DataFrame(
                [
                    [1, 10, 2, 8, date(1900, 1, 1), None],
                    [2, 10, 2, 8, date(1900, 1, 1), None],
                    [3, 10, 1, 9, date(1900, 1, 1), None],
                    [4, 10, 1, 9, date(1900, 1, 1), None],
                    [5, 10, 1, 9, date(1900, 1, 1), None],
                    [6, 10, 11, 0, date(1900, 1, 1), None],
                    [7, 10, 11, 0, date(1900, 1, 1), None],
                    [8, 10, 1, 9, date(1900, 1, 1), None],
                    [9, 10, 3, 7, date(1900, 1, 1), None],
                ],
                columns=[
                    "drug_id",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first month
            date(2000, 1, 1),
            date(2023, 1, 31),
            pd.DataFrame(
                [
                    [1, 10, 2, 8, date(1900, 1, 1), None],
                    [2, 10, 2, 8, date(1900, 1, 1), None],
                    [3, 10, 2, 19, date(2023, 1, 3), 20.0],
                    [4, 10, 1, 9, date(1900, 1, 1), None],
                    [5, 10, 1, 9, date(1900, 1, 1), None],
                    [6, 10, 11, 0, date(1900, 1, 1), None],
                    [7, 10, 11, 20, date(2023, 1, 3), 20.0],
                    [8, 10, 1, 9, date(1900, 1, 1), None],
                    [9, 10, 6, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "drug_id",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Selected period with no entry
            date(2000, 1, 1),
            date(2000, 1, 2),
            pd.DataFrame(
                [],
                columns=[
                    "drug_id",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
    ],
)
def test_compute_consumption_per_ID(
    db_connection,
    start_date,
    end_date,
    expected_consumption,
    store_xlsx=True,
    store_csv=False,
):
    groupby_cols = [
        "drug_id",
    ]

    df_movs = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)

    # Compute cumlative results per group
    cumulative_result = reports_utils.computed_cum_res(
        df_drugs=df_drugs, df_movs=df_movs, groupby_cols=groupby_cols
    )

    # Compute consumption per group
    df_consumption_ID = reports_utils.compute_consumption_group(
        cumulative_result,
        start_date=start_date,
        end_date=end_date,
        groupby_cols=groupby_cols,
    )

    if store_xlsx:
        path_to_csv = "test_data/tmp_consumption_agg_per_ID.xlsx"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption_ID.to_excel(path_to_csv, index=False)

    if store_csv:
        path_to_csv = "test_data/tmp_consumption_agg_per_ID.csv"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption_ID.to_csv(path_to_csv, index=False)

    diff = df_consumption_ID.compare(expected_consumption)

    assert diff.empty


@pytest.mark.parametrize(
    "end_date, expected_consumption",
    [
        (  # Take all movements
            date(3000, 1, 31),
            pd.DataFrame(
                [
                    [1, 8, date(1900, 1, 1), None],
                    [2, 8, date(1900, 1, 1), None],
                    [3, 19, date(2023, 1, 3), 20.0],
                    [4, 9, date(1900, 1, 1), None],
                    [5, 8, date(1900, 1, 1), None],
                    [6, 0, date(1900, 1, 1), None],
                    [7, 20, date(2023, 1, 3), 20.0],
                    [8, 9, date(1900, 1, 1), None],
                    [9, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "drug_id",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first 2 days
            date(2023, 1, 2),
            pd.DataFrame(
                [
                    [1, 8, date(1900, 1, 1), None],
                    [2, 8, date(1900, 1, 1), None],
                    [3, 9, date(1900, 1, 1), None],
                    [4, 9, date(1900, 1, 1), None],
                    [5, 9, date(1900, 1, 1), None],
                    [6, 0, date(1900, 1, 1), None],
                    [7, 0, date(1900, 1, 1), None],
                    [8, 9, date(1900, 1, 1), None],
                    [9, 7, date(1900, 1, 1), None],
                ],
                columns=[
                    "drug_id",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first month
            date(2023, 1, 31),
            pd.DataFrame(
                [
                    [1, 8, date(1900, 1, 1), None],
                    [2, 8, date(1900, 1, 1), None],
                    [3, 19, date(2023, 1, 3), 20.0],
                    [4, 9, date(1900, 1, 1), None],
                    [5, 9, date(1900, 1, 1), None],
                    [6, 0, date(1900, 1, 1), None],
                    [7, 20, date(2023, 1, 3), 20.0],
                    [8, 9, date(1900, 1, 1), None],
                    [9, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "drug_id",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Selected period with no entry
            date(2000, 1, 2),
            pd.DataFrame(
                [],
                columns=[
                    "drug_id",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
    ],
)
def test_compute_stock_per_ID(
    db_connection, end_date, expected_consumption, store_xlsx=True, store_csv=False
):
    groupby_cols = [
        "drug_id",
    ]

    df_movs = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)

    # Compute cumlative results per group
    cumulative_result = reports_utils.computed_cum_res(
        df_drugs=df_drugs, df_movs=df_movs, groupby_cols=groupby_cols
    )

    # Compute consumption per group
    df_consumption_ID = reports_utils.compute_stock_group(
        cumulative_result,
        end_date=end_date,
        groupby_cols=groupby_cols,
    )

    if store_xlsx:
        path_to_csv = "test_data/tmp_consumption_agg_per_ID.xlsx"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption_ID.to_excel(path_to_csv, index=False)

    if store_csv:
        path_to_csv = "test_data/tmp_consumption_agg_per_ID.csv"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption_ID.to_csv(path_to_csv, index=False)

    diff = df_consumption_ID.compare(expected_consumption)

    assert diff.empty


@pytest.mark.parametrize(
    "start_date, end_date, expected_consumption",
    [
        (  # Take all movements
            date(2023, 1, 1),
            date(3000, 1, 31),
            pd.DataFrame(
                [
                    # name, dose, entry, exit, stock, last_inventory_date, last_inventory_stock
                    ["test_drug", 1, 20, 3, 17, date(1900, 1, 1), None],
                    ["test_drug", 10, 10, 2, 8, date(1900, 1, 1), None],
                    ["test_drug2", 1, 10, 2, 8, date(1900, 1, 1), None],
                    ["test_drug3", 1, 10, 2, 19, date(2023, 1, 3), 20],
                    ["test_drug6", 1, 10, 11, 0, date(1900, 1, 1), None],
                    ["test_drug7", 1, 10, 11, 20, date(2023, 1, 3), 20],
                    ["test_drug8", 1, 10, 1, 9, date(1900, 1, 1), None],
                    ["test_drug9", 1, 10, 6, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "name",
                    "dose",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first 2 days
            date(2000, 1, 1),
            date(2023, 1, 2),
            pd.DataFrame(
                [
                    # name, dose, entry, exit, stock, last_inventory_date, last_inventory_stock
                    ["test_drug", 1, 20, 3, 17, date(1900, 1, 1), None],
                    ["test_drug", 10, 10, 1, 9, date(1900, 1, 1), None],
                    ["test_drug2", 1, 10, 2, 8, date(1900, 1, 1), None],
                    ["test_drug3", 1, 10, 1, 9, date(1900, 1, 1), None],
                    ["test_drug6", 1, 10, 11, 0, date(1900, 1, 1), None],
                    ["test_drug7", 1, 10, 11, 0, date(1900, 1, 1), None],
                    ["test_drug8", 1, 10, 1, 9, date(1900, 1, 1), None],
                    ["test_drug9", 1, 10, 3, 7, date(1900, 1, 1), None],
                ],
                columns=[
                    "name",
                    "dose",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first month
            date(2000, 1, 1),
            date(2023, 1, 31),
            pd.DataFrame(
                [
                    # name, dose, entry, exit, stock, last_inventory_date, last_inventory_stock
                    ["test_drug", 1, 20, 3, 17, date(1900, 1, 1), None],
                    ["test_drug", 10, 10, 1, 9, date(1900, 1, 1), None],
                    ["test_drug2", 1, 10, 2, 8, date(1900, 1, 1), None],
                    ["test_drug3", 1, 10, 2, 19, date(2023, 1, 3), 20],
                    ["test_drug6", 1, 10, 11, 0, date(1900, 1, 1), None],
                    ["test_drug7", 1, 10, 11, 20, date(2023, 1, 3), 20],
                    ["test_drug8", 1, 10, 1, 9, date(1900, 1, 1), None],
                    ["test_drug9", 1, 10, 6, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "name",
                    "dose",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Selected period with no entry
            date(2000, 1, 1),
            date(2000, 1, 2),
            pd.DataFrame(
                [],
                columns=[
                    "name",
                    "dose",
                    "entry",
                    "exit",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
    ],
)
def test_compute_consumption_per_name_dose(
    db_connection,
    start_date,
    end_date,
    expected_consumption,
    store_xlsx=True,
    store_csv=False,
):
    # Specify groupby columns
    groupby_cols = [
        "name",
        "dose",
    ]

    df_movs = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)

    cumulative_result = reports_utils.computed_cum_res(
        df_drugs=df_drugs, df_movs=df_movs, groupby_cols=groupby_cols
    )

    df_consumption = reports_utils.compute_consumption_group(
        cumulative_result,
        start_date=start_date,
        end_date=end_date,
        groupby_cols=groupby_cols,
    )

    if store_xlsx:
        path_to_csv = "test_data/consumption_agg_per_name_dose.xlsx"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption.to_excel(path_to_csv, index=False)

    if store_csv:
        path_to_csv = "test_data/consumption_agg_per_name_dose.csv"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption.to_csv(path_to_csv, index=False)

    # TODO clean up. Some custom casting
    df_consumption["dose"] = df_consumption["dose"].astype("int")
    expected_consumption["dose"] = expected_consumption["dose"].astype("int")

    diff = df_consumption.compare(expected_consumption)

    assert diff.empty


@pytest.mark.parametrize(
    "end_date, expected_consumption",
    [
        (  # Take all movements
            date(3000, 1, 31),
            pd.DataFrame(
                [
                    # name, dose, stock, last_inventory_date, last_inventory_stock
                    ["test_drug", 1, 17, date(1900, 1, 1), None],
                    ["test_drug", 10, 8, date(1900, 1, 1), None],
                    ["test_drug2", 1, 8, date(1900, 1, 1), None],
                    ["test_drug3", 1, 19, date(2023, 1, 3), 20],
                    ["test_drug6", 1, 0, date(1900, 1, 1), None],
                    ["test_drug7", 1, 20, date(2023, 1, 3), 20],
                    ["test_drug8", 1, 9, date(1900, 1, 1), None],
                    ["test_drug9", 1, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "name",
                    "dose",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first 2 days
            date(2023, 1, 2),
            pd.DataFrame(
                [
                    # name, dose, entry, exit, stock, last_inventory_date, last_inventory_stock
                    ["test_drug", 1, 17, date(1900, 1, 1), None],
                    ["test_drug", 10, 9, date(1900, 1, 1), None],
                    ["test_drug2", 1, 8, date(1900, 1, 1), None],
                    ["test_drug3", 1, 9, date(1900, 1, 1), None],
                    ["test_drug6", 1, 0, date(1900, 1, 1), None],
                    ["test_drug7", 1, 0, date(1900, 1, 1), None],
                    ["test_drug8", 1, 9, date(1900, 1, 1), None],
                    ["test_drug9", 1, 7, date(1900, 1, 1), None],
                ],
                columns=[
                    "name",
                    "dose",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Take only the first month
            date(2023, 1, 31),
            pd.DataFrame(
                [
                    # name, dose, entry, exit, stock, last_inventory_date, last_inventory_stock
                    ["test_drug", 1, 17, date(1900, 1, 1), None],
                    ["test_drug", 10, 9, date(1900, 1, 1), None],
                    ["test_drug2", 1, 8, date(1900, 1, 1), None],
                    ["test_drug3", 1, 19, date(2023, 1, 3), 20],
                    ["test_drug6", 1, 0, date(1900, 1, 1), None],
                    ["test_drug7", 1, 20, date(2023, 1, 3), 20],
                    ["test_drug8", 1, 9, date(1900, 1, 1), None],
                    ["test_drug9", 1, 4, date(1900, 1, 1), None],
                ],
                columns=[
                    "name",
                    "dose",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
        (  # Selected period with no entry
            date(2000, 1, 2),
            pd.DataFrame(
                [],
                columns=[
                    "name",
                    "dose",
                    "stock",
                    "last_inventory_date",
                    "last_inventory_stock",
                ],
            ),
        ),
    ],
)
def test_compute_stock_per_name_dose(
    db_connection, end_date, expected_consumption, store_xlsx=True, store_csv=False
):
    # Specify groupby columns
    groupby_cols = [
        "name",
        "dose",
    ]

    df_movs = sql_utils.get_all_movements_df(db_connection)
    df_drugs = sql_utils.get_all_drugs_df(db_connection)

    cumulative_result = reports_utils.computed_cum_res(
        df_drugs=df_drugs, df_movs=df_movs, groupby_cols=groupby_cols
    )

    df_consumption = reports_utils.compute_stock_group(
        cumulative_result,
        end_date=end_date,
        groupby_cols=groupby_cols,
    )

    if store_xlsx:
        path_to_csv = "test_data/stock_agg_per_name_dose.xlsx"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption.to_excel(path_to_csv, index=False)

    if store_csv:
        path_to_csv = "test_data/stock_agg_per_name_dose.csv"
        # Store in file for if mofidications are made to the database created for testing
        df_consumption.to_csv(path_to_csv, index=False)

    # TODO clean up. Some custom casting
    df_consumption["dose"] = df_consumption["dose"].astype("int")
    expected_consumption["dose"] = expected_consumption["dose"].astype("int")

    diff = df_consumption.compare(expected_consumption)

    assert diff.empty


def test_gen_consumption_per_ID_xlsx(db_connection):
    _, agg_ID_path, _ = reports_utils.create_folders()
    file_name = "test_consumption_per_ID.xlsx"
    reports_utils.save_xlsx_consumption_ID(
        db_connection=db_connection,
        start_date=date(1990, 1, 1),
        end_date=date(3000, 1, 1),
        folder_path=agg_ID_path,
        file_name=file_name,
    )

    # Check that the file was created
    assert os.path.exists(os.path.join(agg_ID_path, file_name))


def test_gen_consumption_per_nome_dosagem_xlsx(db_connection):
    _, _, path_agg_name = reports_utils.create_folders()
    file_name = "test_consumption_per_nome_dosagem.xlsx"
    reports_utils.save_xlsx_consumption_nome_dose_type(
        db_connection=db_connection,
        start_date=date(1990, 1, 1),
        end_date=date(3000, 1, 1),
        folder_path=path_agg_name,
        file_name=file_name,
    )

    # Check that the file was created
    assert os.path.exists(os.path.join(path_agg_name, file_name))


def test_gen_stock_per_ID_xlsx(db_connection):
    base_path, _, _ = reports_utils.create_folders()
    file_name = "test_stock_per_ID.xlsx"
    reports_utils.save_stock_ID_xlsx(
        db_connection=db_connection,
        end_date=date(3000, 1, 1),
        folder_path=base_path,
        file_name=file_name,
    )

    # Check that the file was created
    assert os.path.exists(os.path.join(base_path, file_name))


def test_gen_stock_per_nome_dosagem_xlsx(db_connection):
    base_path, _, _ = reports_utils.create_folders()
    file_name = "test_stock_per_nome_dosagem.xlsx"
    reports_utils.save_stock_nome_dose_type_xlsx(
        db_connection=db_connection,
        end_date=date(3000, 1, 1),
        folder_path=base_path,
        file_name=file_name,
    )

    # Check that the file was created
    assert os.path.exists(os.path.join(base_path, file_name))


def test_gen_mov_report_per_ID_txt(db_connection):
    _, agg_ID_path, _ = reports_utils.create_folders()
    file_name = "test_mov_per_ID.txt"
    reports_utils.gen_mov_report_ID(
        db_connection=db_connection,
        folder_path=agg_ID_path,
        file_name=file_name,
    )

    # Check that the file was created
    assert os.path.exists(os.path.join(agg_ID_path, "test_mov_per_ID.txt"))


def test_gen_mov_report_per_name_txt(db_connection):
    _, _, path_agg_name = reports_utils.create_folders()
    file_name = "test_mov_per_name.txt"
    reports_utils.gen_mov_report_nome_dose_type(
        db_connection=db_connection,
        folder_path=path_agg_name,
        file_name=file_name,
    )
    # Check that the file was created
    assert os.path.exists(os.path.join(path_agg_name, file_name))


def test_save_full_ds(db_connection):
    report_path, _, _ = reports_utils.create_folders()
    file_name = "test_full_ds.xlsx"
    reports_utils.dump_full_dataset(
        db_connection=db_connection,
        folder_path=report_path,
        file_name=file_name,
    )
    assert os.path.exists(os.path.join(report_path, file_name))


def pytest_sessionfinish(session, exitstatus):
    # Close the database connection after all tests have finished
    db_connection().close()
