import stock_management.sql_utils as sql_utils
import sqlite3
from tkinter import messagebox
from datetime import datetime

from stock_management.common_utils import is_positive_null_integer


def compute_new_stock(
    old_stock,
    pieces_moved,
    movement_type,
    movement_date,
    last_inventory_date,
    last_inventory_stock=0,
):
    """
    Compute the new stock based on movement
    
    Args:
        old_stock: current stock level
        pieces_moved: number of pieces in the movement
        movement_type: 'entry', 'exit', or 'inventory'
        movement_date: date of the movement
        last_inventory_date: date of last inventory
        last_inventory_stock: stock at last inventory
    
    Returns:
        tuple: (new_stock, last_inventory_date, last_inventory_stock)
    """
    new_stock = old_stock
    if movement_date > last_inventory_date:
        if movement_type == "inventory":
            last_inventory_date = movement_date
            new_stock = pieces_moved
            last_inventory_stock = new_stock
        elif movement_type == "entry":
            new_stock = old_stock + pieces_moved
        elif movement_type == "exit":
            new_stock = old_stock - pieces_moved
    else:
        new_stock = old_stock
    return max(0.0, new_stock), last_inventory_date, last_inventory_stock


def update_stock(
    db_connection,
    pieces_moved,
    date_movement,
    movement_type,
    drug_id,
):
    """
    Update the drug stock after a movement
    
    Args:
        db_connection: database connection
        pieces_moved: number of pieces moved
        date_movement: date of movement (string YYYY-MM-DD)
        movement_type: 'entry', 'exit', or 'inventory'
        drug_id: id of the drug
    """
    drug = sql_utils.get_row(db_connection, "drugs", drug_id)
    drug_dict = sql_utils.parse_drug(db_connection, "drugs", drug)

    # Parse to datetime
    date_movement = datetime.strptime(date_movement, "%Y-%m-%d").date()

    new_stock, last_inventory_date, last_inventory_stock = compute_new_stock(
        drug_dict["current_stock"],
        pieces_moved,
        movement_type,
        date_movement,
        drug_dict["last_inventory_date"],
    )
    drug_dict["current_stock"] = new_stock
    drug_dict["last_inventory_date"] = last_inventory_date

    # The inventory has the highest priority for updating the stock on a given date
    sql_utils.update_drug(
        conn=db_connection,
        drug_id=drug_id,
        name=drug_dict["name"],
        dose=drug_dict["dose"],
        units=drug_dict["units"],
        expiration=drug_dict["expiration"],
        pieces_per_box=drug_dict["pieces_per_box"],
        drug_type=drug_dict["type"],
        lote=drug_dict["lote"],
        stock=drug_dict["current_stock"],
        last_inventory_date=drug_dict["last_inventory_date"],
    )


def check_entries(values):
    """
    Validate form entries
    
    Args:
        values: dictionary with form values
    
    Returns:
        True if valid, False otherwise (shows popup with errors)
    """
    error_msg = ""
    if values["in_data_movido"] == "":
        error_msg += "\nInserir data"
    if values["comb_type_mov"] == "":
        error_msg += "\nInserir Entrada/Saida/Inventario"
    if not is_positive_null_integer(values["boxes_moved"]):
        error_msg += f"\nNumero de caixinha tem que ser un numero >=0"
    if not is_positive_null_integer(values["pieces_moved"]):
        error_msg += f"\nNumero de pecas tem que ser un numero >=0"

    if error_msg != "":
        messagebox.showerror("Erro", error_msg)
        return False
    return True


def save_move(values, connection, drug, movement_id):
    """
    Save or update a movement in the database
    
    Args:
        values: dictionary with form values
        connection: database connection
        drug: dictionary with drug information
        movement_id: movement id if updating, None if creating new
    
    Returns:
        True if successful, False otherwise
    """
    if not check_entries(values):
        return False

    if values["comb_type_mov"] == "Entrada":
        mov_type = "entry"
    elif values["comb_type_mov"] == "Saida":
        mov_type = "exit"
    elif values["comb_type_mov"] == "Inventario":
        mov_type = "inventory"

    pieces_moved = get_tot_pieces_moved_casted(values, drug)

    if movement_id:
        sql_utils.update_movement(
            conn=connection,
            date_movement=values["in_data_movido"],
            destination_origin=values["in_origin_destiny"],
            pieces_moved=pieces_moved,
            movement_type=mov_type,
            signature=values["in_signature"],
            mov_id=movement_id,
        )
    else:
        sql_utils.add_movement(
            conn=connection,
            date_movement=values["in_data_movido"],
            destination_origin=values["in_origin_destiny"],
            pieces_moved=pieces_moved,
            movement_type=mov_type,
            signature=values["in_signature"],
            drug_id=drug["id"],
        )

    # Update the stock and stock date in drug table
    update_stock(
        connection,
        pieces_moved,
        values["in_data_movido"],
        mov_type,
        drug["id"],
    )

    return True


def get_tot_pieces_moved_casted(values, drug):
    """
    Calculate total pieces moved from boxes and individual pieces
    
    Args:
        values: dictionary with form values
        drug: dictionary with drug information
    
    Returns:
        int: total number of pieces moved
    """
    if values["pieces_moved"].isdigit() and int(values["pieces_moved"]) > 0:
        pieces_moved = int(values["pieces_moved"])
    else:
        pieces_moved = 0
    if values["boxes_moved"].isdigit() and int(values["boxes_moved"]) > 0:
        boxes_moved = int(values["boxes_moved"])
    else:
        boxes_moved = 0

    tot_pieces_moved = pieces_moved + boxes_moved * drug["pieces_per_box"]
    return tot_pieces_moved
