import pandas as pd
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('example.db')

# Query the database and store the result in a pandas DataFrame
df = pd.read_sql('SELECT * FROM users', conn)

# Close the database connection
conn.close()

print(df.columns)