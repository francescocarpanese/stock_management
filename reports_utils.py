import sql_utils
from movement_win_utils import update_stock, compute_new_stock
from datetime import date
import os
from tabulate import tabulate
import pandas as pd


BASE_DIR = 'reports'

def add_cum_stock_group(df):
    df.sort_values(by=['date_movement'], inplace=True)
    #df.reset_index(drop=True, inplace=True)
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


def extract_date(df, start_date, end_date):
    return df[(df['date_movement'] >= start_date) & (df['date_movement'] <= end_date)]
    

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


def comput_out_stock_movement(df_movement):
    pass

