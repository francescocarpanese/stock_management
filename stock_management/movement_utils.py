"""
Movement management utilities - shared business logic
Extracted from tkinter_movement_win_utils.py for use across different UIs
"""
import stock_management.sql_utils as sql_utils
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
    if movement_date >= last_inventory_date:
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


def validate_movement_entries(values):
    """
    Validate movement form entries
    
    Args:
        values: dictionary with form values
    
    Returns:
        tuple: (is_valid, error_message)
    """
    error_msgs = []
    
    if not values.get("in_data_movido") or values["in_data_movido"] == "":
        error_msgs.append("Inserir data")
    
    if not values.get("comb_type_mov") or values["comb_type_mov"] == "":
        error_msgs.append("Inserir Entrada/Saida/Inventario")
    
    if not is_positive_null_integer(values.get("boxes_moved", "")):
        error_msgs.append("Numero de caixinha tem que ser un numero >=0")
    
    if not is_positive_null_integer(values.get("pieces_moved", "")):
        error_msgs.append("Numero de pecas tem que ser un numero >=0")

    if error_msgs:
        return False, "\n".join(error_msgs)
    
    return True, ""


def get_tot_pieces_moved_casted(values, drug):
    """
    Calculate total pieces moved from boxes and individual pieces
    
    Args:
        values: dictionary with form values
        drug: dictionary with drug information
    
    Returns:
        int: total number of pieces moved
    """
    pieces_moved = 0
    boxes_moved = 0
    
    if values.get("pieces_moved", "").isdigit() and int(values["pieces_moved"]) > 0:
        pieces_moved = int(values["pieces_moved"])
    
    if values.get("boxes_moved", "").isdigit() and int(values["boxes_moved"]) > 0:
        boxes_moved = int(values["boxes_moved"])

    tot_pieces_moved = pieces_moved + boxes_moved * drug["pieces_per_box"]
    return tot_pieces_moved


def save_move(values, connection, drug, movement_id=None):
    """
    Save or update a movement in the database
    
    Args:
        values: dictionary with form values
        connection: database connection
        drug: dictionary with drug information
        movement_id: movement id if updating, None if creating new
    
    Returns:
        tuple: (success, error_message)
    """
    is_valid, error_msg = validate_movement_entries(values)
    if not is_valid:
        return False, error_msg

    # Map movement type
    mov_type_map = {
        "Entrada": "entry",
        "Saida": "exit",
        "Inventario": "inventory"
    }
    mov_type = mov_type_map.get(values["comb_type_mov"], values["comb_type_mov"])

    pieces_moved = get_tot_pieces_moved_casted(values, drug)

    try:
        # Ensure origin_destination exists in the lookup table
        origin_destiny_name = values.get("in_origin_destiny", "")
        sql_utils.get_or_create_origin_destination(connection, origin_destiny_name)

        if movement_id:
            sql_utils.update_movement(
                conn=connection,
                date_movement=values["in_data_movido"],
                destination_origin=origin_destiny_name,
                pieces_moved=pieces_moved,
                movement_type=mov_type,
                signature=values.get("in_signature", ""),
                mov_id=movement_id,
            )
        else:
            sql_utils.add_movement(
                conn=connection,
                date_movement=values["in_data_movido"],
                destination_origin=origin_destiny_name,
                pieces_moved=pieces_moved,
                movement_type=mov_type,
                signature=values.get("in_signature", ""),
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
        
        return True, ""
    except Exception as e:
        return False, f"Erro ao guardar movimento: {str(e)}"
