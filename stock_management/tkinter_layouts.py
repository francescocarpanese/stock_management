"""
Tkinter layouts for the GUI - migrated from PySimpleGUI
"""

import tkinter as tk
from tkinter import ttk
from tkcalendar import DateEntry
from datetime import date

# Increased font sizes for better readability
FONT_SIZE = 16
FONT = ("Arial", FONT_SIZE)
FONT_LABEL = ("Arial", FONT_SIZE, "bold")
FONT_BUTTON = ("Arial", 15, "bold")

# Button colors
COLOR_SAVE = "#4CAF50"  # Green
COLOR_EXIT = "#f44336"  # Red
COLOR_GENERATE = "#2196F3"  # Blue


def configure_button_styles():
    """Configure custom button styles"""
    style = ttk.Style()
    
    # Save button style (green)
    style.configure("Save.TButton",
                   background=COLOR_SAVE,
                   foreground="white",
                   font=FONT_BUTTON,
                   padding=10)
    style.map("Save.TButton",
             background=[("active", "#45a049")])
    
    # Exit button style (red)
    style.configure("Exit.TButton",
                   background=COLOR_EXIT,
                   foreground="white",
                   font=FONT_BUTTON,
                   padding=10)
    style.map("Exit.TButton",
             background=[("active", "#da190b")])
    
    # Generate button style (blue)
    style.configure("Generate.TButton",
                   background=COLOR_GENERATE,
                   foreground="white",
                   font=FONT_BUTTON,
                   padding=10)
    style.map("Generate.TButton",
             background=[("active", "#0b7dda")])


class NewDrugWindow(tk.Toplevel):
    """Window for adding or editing drugs"""
    
    def __init__(self, parent, drug=None):
        super().__init__(parent)
        self.title("Medicamento")
        self.result = None
        self.drug = drug
        self.values = None  # Store values before destroying window
        
        # Configure styles
        configure_button_styles()
        
        # Create widgets
        self._create_widgets()
        
        # Fill with existing drug data if editing
        if drug:
            self._fill_drug_data(drug)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        # Nome
        frame_nome = ttk.Frame(self, padding="5")
        frame_nome.pack(fill=tk.X)
        ttk.Label(frame_nome, text="Nome:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_drug_name = ttk.Entry(frame_nome, font=FONT, width=30)
        self.in_drug_name.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Dosagem
        frame_dosagem = ttk.Frame(self, padding="5")
        frame_dosagem.pack(fill=tk.X)
        ttk.Label(frame_dosagem, text="Dosagem:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_dosagem = ttk.Entry(frame_dosagem, font=FONT, width=10)
        self.in_dosagem.pack(side=tk.LEFT, padx=5)
        self.comb_dosagem = ttk.Combobox(
            frame_dosagem, 
            values=["", "l", "dl", "cl", "ml", "g", "mg"],
            font=FONT,
            width=5,
            state="readonly"
        )
        self.comb_dosagem.current(0)
        self.comb_dosagem.pack(side=tk.LEFT, padx=5)
        
        # Data de expiracao
        frame_exp = ttk.Frame(self, padding="5")
        frame_exp.pack(fill=tk.X)
        ttk.Label(frame_exp, text="Data de Expiracao:", font=FONT_LABEL).pack(side=tk.LEFT)
        # Set default date to today
        today = date.today()
        self.in_DATE = DateEntry(
            frame_exp,
            font=FONT,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=today.year,
            month=today.month,
            day=today.day,
            date_pattern='yyyy-mm-dd'
        )
        self.in_DATE.pack(side=tk.LEFT, padx=5)
        
        # Numero pexca dentro 1 caixa
        frame_pieces = ttk.Frame(self, padding="5")
        frame_pieces.pack(fill=tk.X)
        ttk.Label(frame_pieces, text="Numero pexca dentro 1 caixa:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_pieces_in_box = ttk.Entry(frame_pieces, font=FONT, width=10)
        self.in_pieces_in_box.insert(0, "0")
        self.in_pieces_in_box.pack(side=tk.LEFT, padx=5)
        
        # Forma
        frame_forma = ttk.Frame(self, padding="5")
        frame_forma.pack(fill=tk.X)
        ttk.Label(frame_forma, text="Forma:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.combo_forma = ttk.Combobox(
            frame_forma,
            values=["Comprimidos", "Ampolla", "Xerope", "Pumadas", "Frasca"],
            font=FONT,
            width=15,
            state="readonly"
        )
        self.combo_forma.pack(side=tk.LEFT, padx=5)
        
        # Lote
        frame_lote = ttk.Frame(self, padding="5")
        frame_lote.pack(fill=tk.X)
        ttk.Label(frame_lote, text="Lote:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_lote = ttk.Entry(frame_lote, font=FONT, width=20)
        self.in_lote.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Buttons
        frame_buttons = ttk.Frame(self, padding="10")
        frame_buttons.pack(fill=tk.X)
        self.but_save = tk.Button(
            frame_buttons, 
            text="Guarda", 
            command=self._on_save,
            bg=COLOR_SAVE,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_save.pack(side=tk.LEFT, padx=5)
        self.but_exit = tk.Button(
            frame_buttons, 
            text="Fecha", 
            command=self._on_exit,
            bg=COLOR_EXIT,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_exit.pack(side=tk.LEFT, padx=5)
    
    def _fill_drug_data(self, drug):
        """Fill the form with existing drug data"""
        self.in_drug_name.insert(0, drug.get("name", ""))
        self.in_dosagem.insert(0, drug.get("dose", ""))
        if drug.get("units"):
            try:
                idx = ["", "l", "dl", "cl", "ml", "g", "mg"].index(drug["units"])
                self.comb_dosagem.current(idx)
            except ValueError:
                pass
        if drug.get("expiration"):
            self.in_DATE.set_date(drug["expiration"])
        self.in_pieces_in_box.delete(0, tk.END)
        self.in_pieces_in_box.insert(0, str(drug.get("pieces_per_box", "0")))
        if drug.get("type"):
            try:
                idx = ["Comprimidos", "Ampolla", "Xerope", "Pumadas", "Frasca"].index(drug["type"])
                self.combo_forma.current(idx)
            except ValueError:
                pass
        self.in_lote.insert(0, drug.get("lote", ""))
    
    def _on_save(self):
        # Store values before destroying
        self.values = {
            "in_drug_name": self.in_drug_name.get(),
            "in_dosagem": self.in_dosagem.get(),
            "comb_dosagem": self.comb_dosagem.get(),
            "in_DATE": self.in_DATE.get_date().strftime("%Y-%m-%d"),
            "in_pieces_in_box": self.in_pieces_in_box.get(),
            "combo_forma": self.combo_forma.get(),
            "in_lote": self.in_lote.get(),
        }
        self.result = "save"
        self.destroy()
    
    def _on_exit(self):
        self.result = "exit"
        self.destroy()
    
    def get_values(self):
        """Get all form values as a dictionary"""
        return self.values if self.values else {}


class NewMovementWindow(tk.Toplevel):
    """Window for adding or editing movements"""
    
    def __init__(self, parent, drug, movement=None):
        super().__init__(parent)
        self.title("Movimento")
        self.result = None
        self.drug = drug
        self.movement = movement
        self.values = None  # Store values before destroying window
        
        # Configure styles
        configure_button_styles()
        
        # Create widgets
        self._create_widgets()
        
        # Fill with drug and movement data
        self._fill_drug_data(drug)
        if movement:
            self._fill_movement_data(movement)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        # Bind events for updating total pieces
        self.boxes_moved.bind("<KeyRelease>", self._update_total_pieces)
        self.pieces_moved.bind("<KeyRelease>", self._update_total_pieces)
    
    def _create_widgets(self):
        # Drug info section (read-only)
        frame_drug_info = ttk.LabelFrame(self, text="Informacao do Medicamento", padding="10")
        frame_drug_info.pack(fill=tk.X, padx=10, pady=5)
        
        # Row 1: Nome and Dosagem
        row1 = ttk.Frame(frame_drug_info)
        row1.pack(fill=tk.X, pady=2)
        ttk.Label(row1, text="Nome:", font=FONT_LABEL, width=25).pack(side=tk.LEFT)
        self.txt_drug_name = ttk.Label(row1, text="", font=FONT)
        self.txt_drug_name.pack(side=tk.LEFT, padx=5)
        ttk.Label(row1, text="Dosagem:", font=FONT_LABEL, width=15).pack(side=tk.LEFT, padx=(20, 0))
        self.txt_dosagem = ttk.Label(row1, text="", font=FONT)
        self.txt_dosagem.pack(side=tk.LEFT, padx=5)
        self.txt_dosagem_unit = ttk.Label(row1, text="", font=FONT)
        self.txt_dosagem_unit.pack(side=tk.LEFT)
        
        # Row 2: Expiracao and Numero pexca
        row2 = ttk.Frame(frame_drug_info)
        row2.pack(fill=tk.X, pady=2)
        ttk.Label(row2, text="Expiracao:", font=FONT_LABEL, width=25).pack(side=tk.LEFT)
        self.txt_DATE = ttk.Label(row2, text="", font=FONT)
        self.txt_DATE.pack(side=tk.LEFT, padx=5)
        ttk.Label(row2, text="Numero pexca dentro 1 caixa:", font=FONT_LABEL, width=25).pack(side=tk.LEFT, padx=(20, 0))
        self.txt_pieces_in_box = ttk.Label(row2, text="", font=FONT)
        self.txt_pieces_in_box.pack(side=tk.LEFT, padx=5)
        
        # Row 3: Forma and Lote
        row3 = ttk.Frame(frame_drug_info)
        row3.pack(fill=tk.X, pady=2)
        ttk.Label(row3, text="Forma:", font=FONT_LABEL, width=25).pack(side=tk.LEFT)
        self.txt_forma = ttk.Label(row3, text="", font=FONT)
        self.txt_forma.pack(side=tk.LEFT, padx=5)
        ttk.Label(row3, text="Lote:", font=FONT_LABEL, width=15).pack(side=tk.LEFT, padx=(20, 0))
        self.txt_lote = ttk.Label(row3, text="", font=FONT)
        self.txt_lote.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(self, orient="horizontal").pack(fill=tk.X, padx=10, pady=10)
        
        # Movement section
        frame_movement = ttk.Frame(self, padding="10")
        frame_movement.pack(fill=tk.BOTH, expand=True)
        
        # Data do movido
        frame_data = ttk.Frame(frame_movement)
        frame_data.pack(fill=tk.X, pady=2)
        ttk.Label(frame_data, text="Data do movido:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_data_movido = DateEntry(
            frame_data,
            font=FONT,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=2023,
            month=1,
            day=1,
            date_pattern='yyyy-mm-dd'
        )
        self.in_data_movido.pack(side=tk.LEFT, padx=5)
        
        # Origem/Destino
        frame_orig = ttk.Frame(frame_movement)
        frame_orig.pack(fill=tk.X, pady=2)
        ttk.Label(frame_orig, text="Origem/Destino:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_origin_destiny = ttk.Entry(frame_orig, font=FONT)
        self.in_origin_destiny.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Numero de caixinha completas
        frame_boxes = ttk.Frame(frame_movement)
        frame_boxes.pack(fill=tk.X, pady=2)
        ttk.Label(frame_boxes, text="Numero de caixinha completas:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.boxes_moved = ttk.Entry(frame_boxes, font=FONT, width=10)
        self.boxes_moved.insert(0, "0")
        self.boxes_moved.pack(side=tk.LEFT, padx=5)
        
        # Numero de pecas fora de caixina
        frame_pieces = ttk.Frame(frame_movement)
        frame_pieces.pack(fill=tk.X, pady=2)
        ttk.Label(frame_pieces, text="Numero de pecas fora de caixina:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.pieces_moved = ttk.Entry(frame_pieces, font=FONT, width=10)
        self.pieces_moved.insert(0, "0")
        self.pieces_moved.pack(side=tk.LEFT, padx=5)
        
        # Entrada/Saida/Inventario
        frame_type = ttk.Frame(frame_movement)
        frame_type.pack(fill=tk.X, pady=2)
        ttk.Label(frame_type, text="Entrada/Saida/Inventario:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.comb_type_mov = ttk.Combobox(
            frame_type,
            values=["Entrada", "Saida", "Inventario"],
            font=FONT,
            width=15,
            state="readonly"
        )
        self.comb_type_mov.pack(side=tk.LEFT, padx=5)
        
        # Assignatura
        frame_sign = ttk.Frame(frame_movement)
        frame_sign.pack(fill=tk.X, pady=2)
        ttk.Label(frame_sign, text="Assignatura:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_signature = ttk.Entry(frame_sign, font=FONT)
        self.in_signature.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Buttons
        frame_buttons = ttk.Frame(frame_movement)
        frame_buttons.pack(fill=tk.X, pady=10)
        self.but_save = tk.Button(
            frame_buttons, 
            text="Guarda", 
            command=self._on_save,
            bg=COLOR_SAVE,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_save.pack(side=tk.LEFT, padx=5)
        self.but_exit = tk.Button(
            frame_buttons, 
            text="Fecha", 
            command=self._on_exit,
            bg=COLOR_EXIT,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_exit.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(frame_movement, orient="horizontal").pack(fill=tk.X, pady=10)
        
        # Total pieces
        frame_total = ttk.Frame(frame_movement)
        frame_total.pack(fill=tk.X)
        ttk.Label(frame_total, text="Numero dos pecas movido:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.tot_pieces_moved = ttk.Label(frame_total, text="0", font=FONT)
        self.tot_pieces_moved.pack(side=tk.LEFT, padx=5)
    
    def _fill_drug_data(self, drug):
        """Fill the drug information section"""
        self.txt_drug_name.config(text=drug.get("name", ""))
        self.txt_dosagem.config(text=drug.get("dose", ""))
        self.txt_dosagem_unit.config(text=drug.get("units", ""))
        self.txt_DATE.config(text=str(drug.get("expiration", "")))
        self.txt_pieces_in_box.config(text=str(drug.get("pieces_per_box", "")))
        self.txt_forma.config(text=drug.get("type", ""))
        self.txt_lote.config(text=drug.get("lote", ""))
    
    def _fill_movement_data(self, movement):
        """Fill the form with existing movement data"""
        if movement.get("date_movement"):
            self.in_data_movido.set_date(movement["date_movement"])
        self.in_origin_destiny.insert(0, movement.get("destination_origin", ""))
        self.pieces_moved.delete(0, tk.END)
        self.pieces_moved.insert(0, str(movement.get("pieces_moved", "0")))
        
        # Set movement type
        mov_type = movement.get("movement_type", "")
        if mov_type == "entry":
            self.comb_type_mov.set("Entrada")
        elif mov_type == "exit":
            self.comb_type_mov.set("Saida")
        elif mov_type == "inventory":
            self.comb_type_mov.set("Inventario")
        
        self.in_signature.insert(0, movement.get("signature", ""))
        self._update_total_pieces()
    
    def _update_total_pieces(self, event=None):
        """Update the total pieces label"""
        try:
            boxes = int(self.boxes_moved.get() or 0)
        except ValueError:
            boxes = 0
        
        try:
            pieces = int(self.pieces_moved.get() or 0)
        except ValueError:
            pieces = 0
        
        pieces_per_box = self.drug.get("pieces_per_box", 0)
        total = boxes * pieces_per_box + pieces
        self.tot_pieces_moved.config(text=str(total))
    
    def _on_save(self):
        # Store values before destroying
        self.values = {
            "in_data_movido": self.in_data_movido.get_date().strftime("%Y-%m-%d"),
            "in_origin_destiny": self.in_origin_destiny.get(),
            "boxes_moved": self.boxes_moved.get(),
            "pieces_moved": self.pieces_moved.get(),
            "comb_type_mov": self.comb_type_mov.get(),
            "in_signature": self.in_signature.get(),
        }
        self.result = "save"
        self.destroy()
    
    def _on_exit(self):
        self.result = "exit"
        self.destroy()
    
    def get_values(self):
        """Get all form values as a dictionary"""
        return self.values if self.values else {}


class ReportWindow(tk.Toplevel):
    """Window for generating reports"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Report")
        self.result = None
        self.report_folder = None
        
        # Configure styles
        configure_button_styles()
        
        # Create widgets
        self._create_widgets()
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Center window
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        # Calculate default dates: start of previous month to today
        today = date.today()
        # Get first day of current month, then go back one day to get last day of previous month
        first_day_this_month = today.replace(day=1)
        # Calculate first day of previous month
        if first_day_this_month.month == 1:
            start_date = first_day_this_month.replace(year=first_day_this_month.year - 1, month=12)
        else:
            start_date = first_day_this_month.replace(month=first_day_this_month.month - 1)
        
        # Data do inicio
        frame_start = ttk.Frame(self, padding="10")
        frame_start.pack(fill=tk.X)
        ttk.Label(frame_start, text="Data do inicio:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_data_start = DateEntry(
            frame_start,
            font=FONT,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=start_date.year,
            month=start_date.month,
            day=start_date.day,
            date_pattern='yyyy-mm-dd'
        )
        self.in_data_start.pack(side=tk.LEFT, padx=5)
        
        # Data do fim
        frame_end = ttk.Frame(self, padding="10")
        frame_end.pack(fill=tk.X)
        ttk.Label(frame_end, text="Data do fim:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.in_data_end = DateEntry(
            frame_end,
            font=FONT,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            year=today.year,
            month=today.month,
            day=today.day,
            date_pattern='yyyy-mm-dd'
        )
        self.in_data_end.pack(side=tk.LEFT, padx=5)
        
        # Generate button
        frame_gen = ttk.Frame(self, padding="10")
        frame_gen.pack(fill=tk.X)
        self.but_generate = tk.Button(
            frame_gen, 
            text="Generate", 
            command=self._on_generate,
            bg=COLOR_GENERATE,
            fg="white",
            font=FONT_BUTTON,
            padx=20,
            pady=10,
            relief=tk.RAISED,
            cursor="hand2"
        )
        self.but_generate.pack(side=tk.LEFT, padx=5)
        
        # Link to folder
        frame_link = ttk.Frame(self, padding="10")
        frame_link.pack(fill=tk.X)
        ttk.Label(frame_link, text="Link reports:", font=FONT_LABEL).pack(side=tk.LEFT)
        self.txt_link_folder = ttk.Label(
            frame_link, 
            text="", 
            font=FONT, 
            foreground="blue",
            cursor="hand2"
        )
        self.txt_link_folder.pack(side=tk.LEFT, padx=5)
        self.txt_link_folder.bind("<Button-1>", self._on_link_click)
    
    def _on_generate(self):
        self.result = "generate"
    
    def _on_link_click(self, event):
        """Open the report folder"""
        import os
        import subprocess
        if self.report_folder and os.path.exists(self.report_folder):
            # Open folder based on OS
            if os.name == 'nt':  # Windows
                os.startfile(self.report_folder)
            elif os.name == 'posix':  # macOS and Linux
                subprocess.call(['xdg-open', self.report_folder])
    
    def set_report_folder(self, folder_path):
        """Set the report folder path and update the link"""
        self.report_folder = folder_path
        self.txt_link_folder.config(text=folder_path)
    
    def get_values(self):
        """Get all form values as a dictionary"""
        return {
            "in_data_start": self.in_data_start.get_date().strftime("%Y-%m-%d") if self.in_data_start.get_date() else "",
            "in_data_end": self.in_data_end.get_date().strftime("%Y-%m-%d") if self.in_data_end.get_date() else "",
        }
