import stock_management.sql_utils as sql_utils
import sqlite3
from tkinter import messagebox
from stock_management.common_utils import (
    is_positive_integer,
    clear_string,
    parse_dose_units,
)


def save_drug(values, connection, id=None):
    """
    Save or update a drug in the database
    
    Args:
        values: dictionary with form values
        connection: database connection
        id: drug id if updating, None if creating new
    
    Returns:
        True if successful, False otherwise
    """
    if not check_entries(values):
        return False

    # Parse the drug name, dose and units
    drug_string_clean = clear_string(values["in_drug_name"])
    name_in, dose_in, units_in = parse_dose_units(drug_string_clean)
    dose = values["in_dosagem"] if values["in_dosagem"] else dose_in
    units = values["comb_dosagem"] if values["comb_dosagem"] else units_in

    if id:
        sql_utils.update_drug(
            conn=connection,
            drug_id=id,
            name=name_in,
            dose=dose,
            units=units,
            expiration=values["in_DATE"],
            pieces_per_box=values["in_pieces_in_box"],
            drug_type=values["combo_forma"],
            lote=values["in_lote"],
        )
    else:
        sql_utils.add_drug(
            conn=connection,
            name=name_in,
            dose=dose,
            units=units,
            expiration=values["in_DATE"],
            pieces_per_box=values["in_pieces_in_box"],
            drug_type=values["combo_forma"],
            lote=values["in_lote"],
        )

    return True


def check_entries(values):
    """
    Validate form entries
    
    Args:
        values: dictionary with form values
    
    Returns:
        True if valid, False otherwise (shows popup with errors)
    """
    error_msg = ""
    if values["in_drug_name"] == "":
        error_msg += "\nInserir nome do medicamento"
    if values["in_DATE"] == "":
        error_msg += "\nInserir data expiracao"
    if not is_positive_integer(values["in_pieces_in_box"]):
        error_msg += f"\nNumero de pecas dentro uma caiza tem que ser un numero >0"
    if error_msg != "":
        messagebox.showerror("Erro", error_msg)
        return False
    return True
