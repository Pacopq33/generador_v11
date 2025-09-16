import tkinter as tk
from tkinter import ttk, filedialog

class FileSelector(ttk.Frame):
    def __init__(self, parent, callback):
        super().__init__(parent)

        self.callback = callback

        self.grid_columnconfigure(1, weight=1)

        self.label = ttk.Label(self, text="Archivo Excel:")
        self.label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(self, textvariable=self.entry_var, state="readonly")
        self.entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        self.button = ttk.Button(self, text="📁 Cargar archivo", command=self.select_file)
        self.button.grid(row=1, column=0, columnspan=2, sticky="ew", padx=5, pady=5)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx *.xls")]
        )
        if file_path:
            self.entry_var.set(file_path)
            self.callback(file_path)

    def clear_selection(self):
        self.entry_var.set("")
