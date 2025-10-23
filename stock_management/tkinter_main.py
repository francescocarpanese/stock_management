"""
Main application file using Tkinter
Migrated from PySimpleGUI
"""

import tkinter as tk
from tkinter import ttk
import sqlite3
import os
from stock_management.create_tables import create_all_tables
import stock_management.sql_utils as sql_utils
import stock_management.tkinter_main_win_utils as main_win_utils
import stock_management.tkinter_drugs_win_utils as drugs_win_utils
import stock_management.tkinter_movement_win_utils as movement_win_utils
import stock_management.tkinter_report_win_utils as report_win_utils
from stock_management.tkinter_layouts import NewDrugWindow, NewMovementWindow, ReportWindow

# Increased font sizes for better readability
FONT_SIZE = 16
FONT = ("Arial", FONT_SIZE)
FONT_LABEL = ("Arial", FONT_SIZE, "bold")
FONT_BUTTON = ("Arial", 15, "bold")

# Button colors for main window
COLOR_NEW_MOVEMENT = "#FF9800"  # Orange
COLOR_CORRECT_DRUG = "#9C27B0"  # Purple
COLOR_NEW_DRUG = "#4CAF50"      # Green
COLOR_REPORT = "#2196F3"        # Blue


class StockManagementApp:
    """Main application window"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Gestao de Stock - Main")
        
        # Create database if not existing
        self.path_to_database = "database.db"
        if not os.path.exists(self.path_to_database):
            create_all_tables(self.path_to_database)
        
        # Connect to database
        self.conn = sqlite3.connect(self.path_to_database)
        
        # Current rows displayed in table
        self.rows = []
        
        # Create UI
        self._create_widgets()
        
        # Load initial data
        self._load_all_drugs()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Top frame with search and filters
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        # Nome search
        ttk.Label(top_frame, text="Nome:", font=FONT_LABEL).pack(side=tk.LEFT, padx=5)
        self.in_name = ttk.Entry(top_frame, font=FONT, width=20)
        self.in_name.pack(side=tk.LEFT, padx=5)
        self.in_name.bind("<KeyRelease>", self._on_search_changed)
        
        # Checkboxes - using custom style for larger font
        checkbox_style = ttk.Style()
        checkbox_style.configure("Custom.TCheckbutton", font=FONT)
        
        self.chx_expired_var = tk.BooleanVar(value=True)
        self.chx_expired = ttk.Checkbutton(
            top_frame,
            text="Expirado",
            variable=self.chx_expired_var,
            command=self._on_filter_changed,
            style="Custom.TCheckbutton"
        )
        self.chx_expired.pack(side=tk.LEFT, padx=5)
        
        self.chx_out_stock_var = tk.BooleanVar(value=False)
        self.chx_out_stock = ttk.Checkbutton(
            top_frame,
            text="Esgotados",
            variable=self.chx_out_stock_var,
            command=self._on_filter_changed,
            style="Custom.TCheckbutton"
        )
        self.chx_out_stock.pack(side=tk.LEFT, padx=5)
        
        self.chx_present_var = tk.BooleanVar(value=True)
        self.chx_present = ttk.Checkbutton(
            top_frame,
            text="Presente",
            variable=self.chx_present_var,
            command=self._on_filter_changed,
            style="Custom.TCheckbutton"
        )
        self.chx_present.pack(side=tk.LEFT, padx=5)
        
        # Table frame
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Configure table style with larger font
        table_style = ttk.Style()
        table_style.configure("Custom.Treeview", 
                             font=FONT,
                             rowheight=30)  # Increased row height for larger font
        table_style.configure("Custom.Treeview.Heading", 
                             font=FONT_LABEL)
        
        # Create treeview (table)
        columns = ("Nome", "Dosagem", "Units", "Expiracao", "Pecas por caixa", "Forma", "Lote", "Stock presente")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20, style="Custom.Treeview")
        
        # Define column headings and widths
        col_widths = [200, 80, 50, 100, 120, 100, 100, 120]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=tk.W)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout for table and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Configure alternating row colors
        self.tree.tag_configure('oddrow', background='white')
        self.tree.tag_configure('evenrow', background='lightgray')
        
        # Buttons frame
        buttons_frame = ttk.Frame(self.root, padding="10")
        buttons_frame.pack(fill=tk.X)
        
        self.but_new_mov = tk.Button(
            buttons_frame,
            text="Nuovo Movimento",
            command=self._on_new_movement,
            bg=COLOR_NEW_MOVEMENT,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_new_mov.pack(side=tk.LEFT, padx=5)
        
        self.but_correct_drug = tk.Button(
            buttons_frame,
            text="Correccao Medicamento",
            command=self._on_correct_drug,
            bg=COLOR_CORRECT_DRUG,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_correct_drug.pack(side=tk.LEFT, padx=5)
        
        self.but_new_drug = tk.Button(
            buttons_frame,
            text="Nuovo Medicamento",
            command=self._on_new_drug,
            bg=COLOR_NEW_DRUG,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_new_drug.pack(side=tk.LEFT, padx=5)
        
        self.but_report = tk.Button(
            buttons_frame,
            text="Report",
            command=self._on_report,
            bg=COLOR_REPORT,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=12,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_report.pack(side=tk.LEFT, padx=5)
    
    def _load_all_drugs(self):
        """Load all drugs from database and display in table"""
        self.rows = main_win_utils.get_all_drugs(self.conn)
        self._display_table(self.rows)
    
    def _display_table(self, rows):
        """Display rows in the table"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Format rows for display
        formatted_rows = main_win_utils.format_table_rows(rows)
        
        # Insert new items with alternating colors
        for idx, row in enumerate(formatted_rows):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=row, tags=(tag,))
    
    def _on_search_changed(self, event=None):
        """Handle search text change"""
        search_text = self.in_name.get()
        self.rows = main_win_utils.search_drug(
            self.conn,
            search_text,
            self.chx_expired_var.get(),
            self.chx_out_stock_var.get(),
            self.chx_present_var.get()
        )
        self._display_table(self.rows)
    
    def _on_filter_changed(self):
        """Handle filter checkbox change"""
        self._on_search_changed()
    
    def _on_new_drug(self):
        """Open window to create a new drug"""
        drug_window = NewDrugWindow(self.root)
        self.root.wait_window(drug_window)
        
        if drug_window.result == "save":
            values = drug_window.get_values()
            if drugs_win_utils.save_drug(values, self.conn):
                # Clear the search field
                self.in_name.delete(0, tk.END)
                
                # Reset filters to default
                self.chx_expired_var.set(True)
                self.chx_out_stock_var.set(False)
                self.chx_present_var.set(True)
                
                # Reload all drugs
                self._load_all_drugs()
    
    def _on_correct_drug(self):
        """Open window to edit selected drug"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get the index of selected item
        selected_idx = self.tree.index(selected_items[0])
        
        # Get drug from database
        drug_id = self.rows[selected_idx][0]
        row = sql_utils.get_row(self.conn, "drugs", drug_id)
        drug_dict = sql_utils.parse_drug(self.conn, "drugs", row)
        
        # Open drug window with existing data
        drug_window = NewDrugWindow(self.root, drug=drug_dict)
        self.root.wait_window(drug_window)
        
        if drug_window.result == "save":
            values = drug_window.get_values()
            if drugs_win_utils.save_drug(values, self.conn, id=drug_dict["id"]):
                # Reload table
                self._on_search_changed()
    
    def _on_new_movement(self):
        """Open window to create a new movement for selected drug"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        # Get the index of selected item
        selected_idx = self.tree.index(selected_items[0])
        
        # Get drug from database
        drug_id = self.rows[selected_idx][0]
        row = sql_utils.get_row(self.conn, "drugs", drug_id)
        drug_dict = sql_utils.parse_drug(self.conn, "drugs", row)
        
        # Open movement window
        mov_window = NewMovementWindow(self.root, drug=drug_dict)
        self.root.wait_window(mov_window)
        
        if mov_window.result == "save":
            values = mov_window.get_values()
            if movement_win_utils.save_move(values, self.conn, drug_dict, None):
                # Refresh the table to show updated stock
                self._on_search_changed()
    
    def _on_report(self):
        """Open window to generate reports"""
        report_window = ReportWindow(self.root)
        
        # Keep window open until explicitly closed
        while report_window.winfo_exists():
            if report_window.result == "generate":
                values = report_window.get_values()
                report_win_utils.save_report(values, self.conn, report_window)
                report_window.result = None  # Reset result
            self.root.update()
    
    def _on_closing(self):
        """Handle application close"""
        self.conn.close()
        self.root.destroy()


def main():
    """Main entry point"""
    root = tk.Tk()
    app = StockManagementApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
