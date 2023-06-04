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
    # For each group, sort by date the different movements before computing the cumulative stock
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

def add_cum_stock_df(df, groupby_cols):
    ''' Add the cumulative stock to the df
    - df is usually the merging of df_drug and df_mov on drug_id
    '''

    # Group the DataFrame by a specific column(s)
    grouped_df = df.groupby(groupby_cols)
    df['stock_after_movement'] = 0
    df['last_inventory_date'] = date(1900,1,1)
    
    # Iterate over each group and apply the custom function
    for group_name, group_df in grouped_df:
    
        # Extract the indices for the group
        indices  = group_df.index
        # Apply the custom function to the group
        group_df = add_cum_stock_group(group_df.copy())

        # Update the group in the original DataFrame with the computed values
        df.loc[indices, 'last_inventory_date'] = group_df.loc[indices,'last_inventory_date']
        df.loc[indices, 'stock_after_movement'] = group_df.loc[indices,'stock_after_movement']
        df.loc[indices, 'last_inventory_stock'] = group_df.loc[indices,'last_inventory_stock']

    return df

def save_txt_mov_per_ID(df_drug, df_mov, folder_path, file_name='mov_per_ID.txt'):
    # This has to be fildered by date already
    file_path = os.path.join(folder_path, file_name)
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
        df_consumption_ID,
        folder_path,
        mask=None,
        file_name='consumption_per_ID.txt',
        col_mask_drug = None,
        col_mask_mov = None,
        ):
    

    # df_consumption_ID needs to have already the cumulative stock added
    df_drug.sort_values(by=['name'], inplace=True)

    # Applying masks
    if mask is not None:
        df_consumption_ID = df_consumption_ID[mask]
    
    # Display all columns if no mask is provided
    if col_mask_drug is None:
        col_mask_drug = df_drug.columns

    if col_mask_mov is None:
        col_mask_mov = df_consumption_ID.columns

    # Compose the output path
    out_path = os.path.join(folder_path, file_name)

    with open(out_path, 'w') as f:
        for index, row in df_drug.iterrows():
            # Extrac the movements for each drug_id
            df_consumption_drug_id = df_consumption_ID[df_consumption_ID['drug_id'] == index]
            row_df = pd.DataFrame([row], columns=df_drug.columns)
            table_row = tabulate(row_df[col_mask_drug], headers='keys', tablefmt='simple', showindex=False)
            f.write(table_row)
            f.write('\n')
            table_mov = tabulate(df_consumption_drug_id[col_mask_mov], headers='keys', tablefmt='psql', showindex=False)
            f.write(table_mov)
            f.write('\n\n')

def save_xlsx_agg_per_ID(
        df_drug,
        df_consumption_ID,
        folder_path,
        mask=None,
        file_name='consumption_per_ID.xlsx',
        col_mask_drug = None,
        col_mask_mov = None,
        ):
    

    # df_consumption_ID needs to have already the cumulative stock added
    df_drug.sort_values(by=['name'], inplace=True)

    # Applying masks
    if mask is not None:
        df_consumption_ID = df_consumption_ID[mask]
    
    # Display all columns if no mask is provided
    if col_mask_drug is None:
        col_mask_drug = df_drug.columns

    if col_mask_mov is None:
        col_mask_mov = df_consumption_ID.columns

    # Compose the output path
    out_path = os.path.join(folder_path, file_name)

    # Add drug_id from index in df_drug
    df_drug['drug_id'] = df_drug.index
    df_drug.drop(columns=['last_inventory_date'], inplace=True)

    # Replace 
    df_merged = pd.merge(df_drug, df_consumption_ID, on='drug_id', how='outer')

    # Select columns to display
    df_merged = df_merged[col_mask_drug + col_mask_mov]
    
    # Create a Pandas Excel writer object
    writer = pd.ExcelWriter(out_path, engine='xlsxwriter')

    # Write the DataFrame to the Excel file
    df_merged.to_excel(writer, index=False, sheet_name='Sheet1')

    # Apply formatting to the file
    format_xlsx(df_merged, writer)

    # Save the Excel file
    writer.close()


def compute_consumption_group(
        df_cum,
        start_date = date(1900,1,1),
        end_date = date(2100,1,1),
        groupby_cols = ['drug_id',],
        ):
    
    # Define output columns
    output_cols = groupby_cols + ['entry', 'exit', 'stock', 'last_inventory_date', 'last_inventory_stock']

    # Init for safe exit
    df_out = pd.DataFrame([],columns= output_cols)
    
    # Filter by date
    df_cum =df_cum[(df_cum['date_movement'] >= start_date) & (df_cum['date_movement'] <= end_date)]
    
    # Return if no movements are available
    if df_cum.empty:
        return df_out

    # Extract entry, exit and inventory
    df_cum['entry'] = df_cum.apply(lambda x: x['pieces_moved'] if x['movement_type'] == 'entry' else 0, axis=1)
    df_cum['exit'] = df_cum.apply(lambda x: x['pieces_moved'] if x['movement_type'] == 'exit' else 0, axis=1)
    df_cum['inventory'] = df_cum.apply(lambda x: x['pieces_moved'] if x['movement_type'] == 'inventory' else 0, axis=1)

    # Group dataset
    df_cum_grouped = df_cum.groupby(groupby_cols)

    # Loop for groups
    for group_name, group_df in df_cum_grouped:

        entry = group_df['entry'].sum()
        exit = group_df['exit'].sum()
        latest_mov_date = group_df['date_movement'].max()
        latest_last_inventory_date = group_df['last_inventory_date'].max()

        # Get the inventory on the latest last inventory date
        inventory_on_last_inventory_date = group_df.loc[(group_df['date_movement'] == latest_last_inventory_date)
                                                        & (group_df['movement_type'] == 'inventory')
                                                        ,
                                                         'stock_after_movement'].min()
        

        # Get indices of dates with the latest date_movement
        idx_latest_mov_date = group_df[group_df['date_movement'] == latest_mov_date].index
        # Get the max of the entry_datetime for the latest date_movement
        max_entry_datetime = group_df.loc[idx_latest_mov_date, 'entry_datetime'].max()
        # Typically entry datatime are unique. However, when generating the db for testing they might be
        # created on the same second. In such a case the stock is considered as the minumum of the stock_after_movement
        stock = group_df.loc[(group_df['date_movement'] == latest_mov_date) & (group_df['entry_datetime'] == max_entry_datetime),
                         'stock_after_movement'].min()
        
        
        df_tmp = pd.DataFrame(            {
                'entry': entry,
                'exit': exit,
                'stock': stock,
                'last_inventory_date': latest_last_inventory_date,
                'last_inventory_stock': inventory_on_last_inventory_date,
             }, index=[0])
        
        for col in groupby_cols:
            df_tmp[col] = group_name[groupby_cols.index(col)]

        df_out  = pd.concat([df_out, df_tmp], ignore_index=True)

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
    report_folders = [f for f in os.listdir(day_folder) if f.startswith("ID_")]
    if report_folders:
        last_id = max([int(f.split("_")[1]) for f in report_folders])
        new_id = str(last_id + 1).zfill(2)
    else:
        new_id = "01"

    # Create new ID folder
    report_folder_path = os.path.join(day_folder, 'ID_' + new_id  )
    os.makedirs(report_folder_path)

    
    # Create aggregation_ID folder
    agg_ID_folder_path = os.path.join(report_folder_path, 'aggregation_ID')
    os.makedirs(agg_ID_folder_path)

    # Create aggregation_nome folder
    agg_name_folder_path = os.path.join(report_folder_path, 'aggregation_nome')
    os.makedirs(agg_name_folder_path)

    return report_folder_path, agg_ID_folder_path, agg_name_folder_path



def format_xlsx(df, writer):

    (max_row, max_col) = df.shape

    # Get the workbook and worksheet objects
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    for i, column in enumerate(df.columns):
        max_len = max(df[column].astype(str).map(len).max(), len(column))
        worksheet.set_column(i, i, max_len + 5)

    # Add the autofilter
    worksheet.autofilter(0, 0, max_row, max_col - 1)

def computed_cum_res(df_drugs, df_movs, groupby_cols):
    df_drugs.reset_index(inplace=True)
    df_drugs.rename(columns={'id':'drug_id'}, inplace=True)
    df_merged = pd.merge(df_movs, df_drugs, on='drug_id', how='left')
    return reports_utils.add_cum_stock_df(df_merged, groupby_cols=groupby_cols)
