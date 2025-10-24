"""
Script to add 30 test drug entries to the database
"""
import sqlite3
from datetime import date, timedelta

DB_PATH = "database.db"

# Sample drug data
DRUGS = [
    {"name": "Paracetamol", "dose": "500", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE001", "stock": 100},
    {"name": "Ibuprofeno", "dose": "200", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE002", "stock": 85},
    {"name": "Amoxicilina", "dose": "500", "units": "mg", "pieces_per_box": 10, "type": "Comprimidos", "lote": "LOTE003", "stock": 45},
    {"name": "Azitromicina", "dose": "500", "units": "mg", "pieces_per_box": 6, "type": "Comprimidos", "lote": "LOTE004", "stock": 30},
    {"name": "Omeprazol", "dose": "20", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE005", "stock": 120},
    {"name": "Levotiroxina", "dose": "75", "units": "mcg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE006", "stock": 60},
    {"name": "Metformina", "dose": "500", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE007", "stock": 150},
    {"name": "Atorvastatina", "dose": "20", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE008", "stock": 90},
    {"name": "Lisinopril", "dose": "10", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE009", "stock": 75},
    {"name": "Cetirizina", "dose": "10", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE010", "stock": 0},
    {"name": "Dipirona", "dose": "500", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE011", "stock": 200},
    {"name": "Losartana", "dose": "50", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE012", "stock": 110},
    {"name": "Fluoxetina", "dose": "20", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE013", "stock": 40},
    {"name": "Sertralina", "dose": "50", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE014", "stock": 55},
    {"name": "Venlafaxina", "dose": "75", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE015", "stock": 25},
    {"name": "Clopidogrel", "dose": "75", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE016", "stock": 65},
    {"name": "Enoxaparina", "dose": "40", "units": "mg", "pieces_per_box": 10, "type": "Ampolla", "lote": "LOTE017", "stock": 35},
    {"name": "Insulina Regular", "dose": "100", "units": "U/ml", "pieces_per_box": 1, "type": "Frasca", "lote": "LOTE018", "stock": 15},
    {"name": "Glicose", "dose": "5", "units": "g", "pieces_per_box": 50, "type": "Comprimidos", "lote": "LOTE019", "stock": 180},
    {"name": "Vitamina C", "dose": "1000", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE020", "stock": 95},
    {"name": "Vitamina D", "dose": "1000", "units": "UI", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE021", "stock": 70},
    {"name": "Cálcio com Vitamina D", "dose": "500/200", "units": "mg/UI", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE022", "stock": 0},
    {"name": "Ferro", "dose": "325", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE023", "stock": 50},
    {"name": "Ácido Fólico", "dose": "5", "units": "mg", "pieces_per_box": 30, "type": "Comprimidos", "lote": "LOTE024", "stock": 88},
    {"name": "Vitamina B12", "dose": "1000", "units": "mcg", "pieces_per_box": 12, "type": "Ampolla", "lote": "LOTE025", "stock": 42},
    {"name": "Prednisona", "dose": "5", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE026", "stock": 35},
    {"name": "Dexametasona", "dose": "4", "units": "mg", "pieces_per_box": 20, "type": "Comprimidos", "lote": "LOTE027", "stock": 20},
    {"name": "Tramadol", "dose": "50", "units": "mg", "pieces_per_box": 10, "type": "Comprimidos", "lote": "LOTE028", "stock": 0},
    {"name": "Paracetamol Infantil", "dose": "250", "units": "mg", "pieces_per_box": 20, "type": "Xerope", "lote": "LOTE029", "stock": 12},
    {"name": "Ibuprofeno Infantil", "dose": "100", "units": "mg/5ml", "pieces_per_box": 1, "type": "Xerope", "lote": "LOTE030", "stock": 8},
]

def add_test_drugs():
    """Add 30 test drugs to the database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    today = date.today()
    
    for idx, drug in enumerate(DRUGS):
        # Vary expiration dates between future and past dates for testing
        if idx % 5 == 0:
            # Some expired drugs
            exp_date = today - timedelta(days=30)
        elif idx % 5 == 1:
            # Some expiring soon
            exp_date = today + timedelta(days=7)
        else:
            # Most have reasonable expiration
            exp_date = today + timedelta(days=365)
        
        c.execute(
            """INSERT INTO drugs (name, dose, units, expiration, pieces_per_box, type, lote, current_stock)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (drug['name'], drug['dose'], drug['units'], exp_date, drug['pieces_per_box'], 
             drug['type'], drug['lote'], drug['stock'])
        )
    
    conn.commit()
    conn.close()
    print(f"✅ Successfully added 30 test drugs to {DB_PATH}")

if __name__ == "__main__":
    add_test_drugs()
