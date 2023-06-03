import stock_management.sql_utils as sql_utils
from stock_management.movement_win_utils import update_stock, compute_new_stock
from datetime import date
import os
from tabulate import tabulate
import pandas as pd
import stock_management.reports_utils as reports_utils
import datetime

BASE_DIR = 'reports'

# Create report directory if not existing
if not os.path.exists(BASE_DIR):
    os.makedirs(BASE_DIR)

def add_cum_stock_group(df):
    df.sort_values(by=['date_movement'], inplace=True)
    df['stock_after_movement'] = 0
    df['last_inventory_date'] = date(1900,1,1)
    df['last_inventory_stock'] = 0
    # Iterate over each row and apply the custom function
    previous_row = None
    indices = df.index
    for index in indices:
        row = df.loc[index]
        if previous_row is None:
            previous_row = row
        
        # For subsequent rows, apply the custom function using the previous row
        new_stock, last_inventory_date, last_invetory_stock = compute_new_stock(
                old_stock=previous_row['stock_after_movement'],
                pieces_moved=row['pieces_moved'],
                movement_type=row['movement_type'],
                movement_date=row['date_movement'],
                last_inventory_date=previous_row['last_inventory_date'],
                last_inventory_stock=previous_row['last_inventory_stock'],
            )
        # Update the current row with the new_stock and last_inventory_date values
        df.loc[index, 'stock_after_movement'] = new_stock
        df.loc[index, 'last_inventory_date'] = last_inventory_date
        df.loc[index, 'last_inventory_stock'] = last_invetory_stock
    
        previous_row = df.loc[index]
        
    return df

def add_cum_stock_df(df):
    # Group the DataFrame by a specific column(s)
    grouped_df = df.groupby('drug_id')
    df['stock_after_movement'] = 0
    df['last_inventory_date'] = date(1900,1,1)
    df['last_inventory_stock'] = 0
    
    # Iterate over each group and apply the custom function
    for group_name, group_df in grouped_df:

        index  = group_df.index
        # Apply the custom function to the group
        group_df = add_cum_stock_group(group_df.copy())

        # Update the group in the original DataFrame with the computed values
        df.loc[index, 'last_inventory_date'] = group_df.loc[index,'last_inventory_date']
        df.loc[index, 'stock_after_movement'] = group_df.loc[index,'stock_after_movement']
        df.loc[index, 'last_inventory_stock'] = group_df.loc[index,'last_inventory_stock']

    return df

def save_txt_mov_per_ID(df_drug, df_mov, file_name='mov_per_ID.txt'):
    # This has to be fildered by date already
    file_path = os.path.join(BASE_DIR, file_name)
    df_drug.sort_values(by=['name'], inplace=True)
    with open(file_path, 'w') as f:
        for index, row in df_drug.iterrows():
           df_mov_drug = df_mov[df_mov['drug_id'] == index]
           df_mov_drug.sort_values(by=['date_movement'], inplace=True)
           row_df = pd.DataFrame([row], columns=df_drug.columns)
           table_row = tabulate(row_df, headers='keys', tablefmt='simple')
           f.write(table_row)
           f.write('\n')
           table_mov = tabulate(df_mov_drug, headers='keys', tablefmt='psql')
           f.write(table_mov)
           f.write('\n\n')

def save_txt_agg_per_ID(
        df_drug,
        df_mov,
        mask=None,
        file_name='consumption_per_ID.txt',
        col_mask_drug = None,
        col_mask_mov = None,
        ):
    

    # df_mov needs to have already the cumulative stock added
    df_drug.sort_values(by=['name'], inplace=True)

    # Applying masks
    if mask is not None:
        df_mov = df_mov[mask]
    
    # Display all columns if no mask is provided
    if col_mask_drug is None:
        col_mask_drug = df_drug.columns

    if col_mask_mov is None:
        col_mask_mov = df_mov.columns

    # Compose the output path
    out_path = os.path.join(BASE_DIR, file_name)

    with open(out_path, 'w') as f:
        for index, row in df_drug.iterrows():
            # Extrac the movements for each drug_id
            df_consumption_drug_id = df_mov[df_mov['drug_id'] == index]
            row_df = pd.DataFrame([row], columns=df_drug.columns)
            table_row = tabulate(row_df[col_mask_drug], headers='keys', tablefmt='simple', showindex=False)
            f.write(table_row)
            f.write('\n')
            table_mov = tabulate(df_consumption_drug_id[col_mask_mov], headers='keys', tablefmt='psql', showindex=False)
            f.write(table_mov)
            f.write('\n\n')

def compute_consumption_agg_drug_ID(
        df_drug,
        df_mov,
        start_date = date(1900,1,1),
        end_date = date(2100,1,1),
        ):
    
    # The df_mov needs to have already the cumulative stock added

    df_drug.sort_values(by=['name'], inplace=True)
    df_drug = df_drug[df_drug['current_stock'] > 0]

    df_mov =df_mov[(df_mov['date_movement'] >= start_date) & (df_mov['date_movement'] <= end_date)]
    
    # Extract entry and exit
    df_mov['entry'] = df_mov.apply(lambda x: x['pieces_moved'] if x['movement_type'] == 'entry' else 0, axis=1)
    df_mov['exit'] = df_mov.apply(lambda x: x['pieces_moved'] if x['movement_type'] == 'exit' else 0, axis=1)

    # Compute total entry for groupby drug_id
    df_mov_entry = df_mov.groupby('drug_id')['entry'].sum().reset_index()
    
    # Compute total exit for groupby drug_id
    df_mov_exit = df_mov.groupby('drug_id')['exit'].sum().reset_index()

    # Merge entry and exit
    df_mov_agg = pd.merge(df_mov_entry, df_mov_exit, on='drug_id', how='outer')

    # Extract the latest available stock for each drug_id
    df_mov_stock = df_mov.groupby('drug_id')['stock_after_movement'].last().reset_index()

    # Rename column stock_after_movement to stock
    df_mov_stock.rename(columns={'stock_after_movement': 'stock'}, inplace=True)

    # Extract the date of latest available stock for each drug_id
    df_mov_date = df_mov.groupby('drug_id')['last_inventory_date'].last().reset_index()

    # Merge the latest available stock and date
    df_mov_stock_date = pd.merge(df_mov_stock, df_mov_date, on='drug_id', how='outer')

    # Merge the aggregated entry and exit with the latest available stock and date
    df_out = pd.merge(df_mov_agg, df_mov_stock_date, on='drug_id', how='outer')

    return df_out

def create_folders(base_folder_path = BASE_DIR):
    today = datetime.date.today()
    year_folder = os.path.join(base_folder_path, str(today.year))
    month_folder = os.path.join(year_folder, str(today.month))
    day_folder = os.path.join(month_folder, str(today.day))

    # Create year folder if it doesn't exist
    if not os.path.exists(year_folder):
        os.makedirs(year_folder)

    # Create month folder if it doesn't exist
    if not os.path.exists(month_folder):
        os.makedirs(month_folder)

    # Create day folder if it doesn't exist
    if not os.path.exists(day_folder):
        os.makedirs(day_folder)

    # Find the highest existing ID folder
    # Neglet the name of the smear_test
    id_folders = [f.rsplit("_",1)[0] for f in os.listdir(day_folder) if f.startswith("ID_")]
    if id_folders:
        last_id = max([int(f.split("_")[1]) for f in id_folders])
        new_id = str(last_id + 1).zfill(2)
    else:
        new_id = "01"

    # Create new ID folder
    id_folder = os.path.join(day_folder, 'ID_' + new_id  )
    os.makedirs(id_folder)

    # Create aggregation_ID folder
    os.makedirs(os.path.join(id_folder, 'aggregation_ID'))

    # Create aggregation_nome folder
    os.makedirs(os.path.join(id_folder, 'aggregation_nome'))

    return id_folder