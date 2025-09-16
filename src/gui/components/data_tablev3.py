import tkinter as tk
from tkinter import ttk
import pandas as pd

class DataTable(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.data = None
        self.selected_items = set()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_label = ttk.Label(self, text="Datos del Excel", font=("Arial", 12, "bold"))
        self.title_label.grid(row=0, column=0, sticky="w", padx=5, pady=(5, 2))

        self.table_frame = ttk.Frame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.tree_scroll_y = ttk.Scrollbar(self.table_frame)
        self.tree_scroll_y.pack(side="right", fill="y")

        self.tree_scroll_x = ttk.Scrollbar(self.table_frame, orient="horizontal")
        self.tree_scroll_x.pack(side="bottom", fill="x")

        self.columns = ['✓', 'Nombre y Apellido', 'DNI', 'Carrera', 'Disposición', 'Día', 'Mes']

        self.tree = ttk.Treeview(
            self.table_frame,
            columns=self.columns,
            show='headings',
            yscrollcommand=self.tree_scroll_y.set,
            xscrollcommand=self.tree_scroll_x.set,
            selectmode="none"
        )

        self.tree_scroll_y.config(command=self.tree.yview)
        self.tree_scroll_x.config(command=self.tree.xview)

        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100, anchor="center")

        self.tree.pack(fill="both", expand=True)

        self.tree.bind('<Button-1>', self.on_click)

    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x, event.y)
            if column == '#1':
                item = self.tree.identify_row(event.y)
                if item:
                    self.toggle_selection(item)

    def toggle_selection(self, item):
        if item in self.selected_items:
            self.selected_items.remove(item)
            self.tree.set(item, '✓', '')
        else:
            self.selected_items.add(item)
            self.tree.set(item, '✓', '✓')

    def load_data(self, data):
        self.clear_data()
        self.data = data

        for index, row in data.iterrows():
            item = self.tree.insert('', 'end', values=(
                '✓',
                row.get('nombre_apellido', ''),
                row.get('dni', ''),
                row.get('carrera', ''),
                row.get('dispo', ''),
                row.get('dia', ''),
                row.get('mes', '')
            ))
            self.selected_items.add(item)

    def clear_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.selected_items.clear()
        self.data = None

    def has_data(self):
        return self.data is not None and not self.data.empty

    def get_selected_data(self):
        if not self.has_data():
            return []

        selected_data = []
        for item in self.selected_items:
            try:
                item_index = self.tree.index(item)
                if item_index < len(self.data):
                    selected_data.append(self.data.iloc[item_index].to_dict())
            except:
                continue

        return selected_data

    def get_all_data(self):
        return self.data if self.has_data() else pd.DataFrame()

    def select_all(self):
        for item in self.tree.get_children():
            if item not in self.selected_items:
                self.selected_items.add(item)
                self.tree.set(item, '✓', '✓')

    def deselect_all(self):
        for item in self.tree.get_children():
            if item in self.selected_items:
                self.selected_items.remove(item)
                self.tree.set(item, '✓', '')
