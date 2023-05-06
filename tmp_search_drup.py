import PySimpleGUI as sg
import sqlite3

# Connect to the database
conn = sqlite3.connect('example.db')
c = conn.cursor()

# Create a table and insert some data
c.execute('''CREATE TABLE drugs (id INTEGER PRIMARY KEY, name TEXT)''')
c.execute("INSERT INTO drugs (name) VALUES ('Aspirin')")
c.execute("INSERT INTO drugs (name) VALUES ('Ibuprofen')")
c.execute("INSERT INTO drugs (name) VALUES ('Paracetamol')")
conn.commit()

# Define the layout
layout = [
    [sg.Text('Enter a drug name:'), sg.Input(key='-IN-', enable_events=True)],
    [sg.Table(values=[], headings=['ID', 'Name'], key='-TABLE-')],
    [sg.Button('Exit')]
]

# Create the window
window = sg.Window('My Window', layout)

while True:
    event, values = window.read()

    # Exit if the user closes the window or clicks the Exit button
    if event == sg.WIN_CLOSED or event == 'Exit':
        break

    # If the user types into the input widget, search the database and update the table
    elif event == '-IN-':
        search_text = values['-IN-']
        c.execute(f"SELECT * FROM drugs WHERE name LIKE '{search_text}%'")
        rows = c.fetchall()
        table_data = [[row[0], row[1]] for row in rows]
        window['-TABLE-'].update(values=table_data)

# Close the window and the database connection
window.close()
conn.close()