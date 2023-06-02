import pandas as pd
from stock_management.create_tables import create_all_tables
from sql_utils import add_drug, add_movement, get_last_row_id
import os
import sqlite3
from stock_management.common_utils import clear_string, parse_dose_units

path_to_excel = 'test_data/Maio.xlsx'

debug = True

df_lista = pd.read_excel(path_to_excel, sheet_name='Lista')

df_lista = df_lista[df_lista['Nome'].notna()]

# lower case the names
df_lista['Nome'] = df_lista['Nome'].apply(lambda x: clear_string(x))

if debug:
    print('Lista')
    print(df_lista.head())

df_stock = pd.read_excel(path_to_excel, sheet_name='Stock presente')

# Clean the stock dataframe
df_stock = df_stock[df_stock['Nome'].notna()]
# crop to zero negative values
df_stock['Stock de peças total presente'] = df_stock['Stock de peças total presente'].apply(lambda x: 0 if x < 0 else x)


if debug:
    print('Stock')
    print(df_stock.head())

df_lista = df_lista[df_lista['Nome'] != '']

df_merged = pd.merge(df_lista, df_stock[['ID','Stock de peças total presente']], on='ID', how='left')

print('Merged')
print(df_merged.head())


def store_db(df):
    path_to_database = 'test_migration.db'

    # Remove the databse is already existing
    if os.path.exists(path_to_database):
        os.remove(path_to_database)

    # Fresh create the tables
    create_all_tables(path_to_database)

    conn =  sqlite3.connect(path_to_database)

    for index, row in df.iterrows():
        try:
            name, dose, units = parse_dose_units(row['Nome'])
            add_drug(
                conn=conn,
                name=name,
                dose=dose,
                units=units,
                expiration=row['Expiraçao'].date(),
                pieces_per_box=row['Número total de peças dentro 1 caixinhas'],
                drug_type=row['Forma'],
                lote=row['Lote'],
                stock=row['Stock de peças total presente'],
                    )
        except Exception as e:
            print(e)
            print(row)

store_db(df_merged)
