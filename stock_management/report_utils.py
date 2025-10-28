"""
Report generation utilities - shared business logic
Extracted from tkinter_report_win_utils.py for use across different UIs
"""
import stock_management.sql_utils as sql_utils
from datetime import datetime, date
from stock_management import reports_utils
import os


def generate_reports(db_connection, start_date=None, end_date=None):
    """
    Generate and save all reports
    
    Args:
        db_connection: database connection
        start_date: start date for reports (date object or None)
        end_date: end date for reports (date object or None)
    
    Returns:
        tuple: (success, error_message, folder_path)
    """
    folder_base_path, agg_ID_path, agg_name_path = reports_utils.create_folders()

    if not start_date:
        start_date = date(1990, 1, 1)

    if not end_date:
        end_date = date(2300, 1, 1)

    errors = []

    # Save consumption report grouped by name, dose, type
    try:
        reports_utils.save_xlsx_consumption_nome_dose_type(
            db_connection=db_connection,
            start_date=start_date,
            end_date=end_date,
            folder_path=agg_name_path,
            file_name="consumption_nome_dose_type.xlsx",
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o relatorio de consumo por nome, dose e tipo: {str(e)}")

    # Save consumption report grouped by ID (drug with same lote)
    try:
        reports_utils.save_xlsx_consumption_ID(
            db_connection=db_connection,
            start_date=start_date,
            end_date=end_date,
            folder_path=agg_ID_path,
            file_name="consumption_ID.xlsx",
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o relatorio de consumo por ID: {str(e)}")

    # Save info for the generated reports
    try:
        reports_utils.save_INFO_txt(
            folder_path=folder_base_path,
            file_name="INFO.txt",
            start_date=start_date,
            end_date=end_date,
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o ficheiro INFO.txt: {str(e)}")

    # Dump full database
    try:
        reports_utils.dump_full_dataset(
            db_connection=db_connection,
            folder_path=folder_base_path,
            file_name="full_database.xlsx",
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o dump da base de dados: {str(e)}")

    # Save movement report per ID
    try:
        reports_utils.gen_mov_report_ID(
            db_connection=db_connection,
            folder_path=agg_ID_path,
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o relatorio de movimentos por ID: {str(e)}")

    # Save movement report per nome, dose, type
    try:
        reports_utils.gen_mov_report_nome_dose_type(
            db_connection=db_connection,
            folder_path=agg_name_path,
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o relatorio de movimentos por nome, dose e tipo: {str(e)}")

    # Save stock report per ID
    try:
        reports_utils.save_stock_ID_xlsx(
            db_connection=db_connection,
            folder_path=folder_base_path,
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o relatorio de stock por ID: {str(e)}")

    # Save stock report per nome, dose, type
    try:
        reports_utils.save_stock_nome_dose_type_xlsx(
            db_connection=db_connection,
            folder_path=folder_base_path,
        )
    except Exception as e:
        errors.append(f"Erro ao gerar o relatorio de stock por nome, dose e tipo: {str(e)}")

    if errors:
        return False, "\n".join(errors), folder_base_path
    
    return True, "", folder_base_path
