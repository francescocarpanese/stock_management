"""
Drug management utilities - shared business logic
Extracted from tkinter_drugs_win_utils.py for use across different UIs
"""
import stock_management.sql_utils as sql_utils
from stock_management.common_utils import (
    is_positive_integer,
    clear_string,
    parse_dose_units,
)


def validate_drug_entries(values):
    """
    Validate drug form entries
    
    Args:
        values: dictionary with form values
            - in_drug_name: drug name (required)
            - in_DATE: expiration date (required)
            - in_pieces_in_box: pieces per box (must be positive integer)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    error_msgs = []
    
    if not values.get("in_drug_name") or values["in_drug_name"] == "":
        error_msgs.append("Inserir nome do medicamento")
    
    if not values.get("in_DATE") or values["in_DATE"] == "":
        error_msgs.append("Inserir data expiracao")
    
    if not is_positive_integer(values.get("in_pieces_in_box", "")):
        error_msgs.append("Numero de pecas dentro uma caiza tem que ser un numero >0")
    
    if error_msgs:
        return False, "\n".join(error_msgs)
    
    return True, ""


def save_drug(values, connection, id=None):
    """
    Save or update a drug in the database
    
    Args:
        values: dictionary with form values
        connection: database connection
        id: drug id if updating, None if creating new
    
    Returns:
        tuple: (success, error_message)
    """
    is_valid, error_msg = validate_drug_entries(values)
    if not is_valid:
        return False, error_msg

    # Parse the drug name, dose and units
    drug_string_clean = clear_string(values["in_drug_name"])
    name_in, dose_in, units_in = parse_dose_units(drug_string_clean)
    name_in = drug_string_clean # We keep dose and units as part of the name as too many edge cases
    # TODO keep for the moment this in the database even if no longer used
    dose = ""
    units = ""

    try:
        if id:
            sql_utils.update_drug(
                conn=connection,
                drug_id=id,
                name=name_in,
                dose=dose,
                units=units,
                expiration=values["in_DATE"],
                pieces_per_box=values["in_pieces_in_box"],
                drug_type=values.get("combo_forma", ""),
                lote=values.get("in_lote", ""),
            )
        else:
            sql_utils.add_drug(
                conn=connection,
                name=name_in,
                dose=dose,
                units=units,
                expiration=values["in_DATE"],
                pieces_per_box=values["in_pieces_in_box"],
                drug_type=values.get("combo_forma", ""),
                lote=values.get("in_lote", ""),
            )
        return True, ""
    except Exception as e:
        return False, f"Erro ao guardar medicamento: {str(e)}"
