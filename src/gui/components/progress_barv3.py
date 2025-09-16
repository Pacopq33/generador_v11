import tkinter as tk
from tkinter import ttk

class ProgressBar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.total = 0
        self.current = 0

        self.grid_columnconfigure(0, weight=1)

        self.progress_label = ttk.Label(self, text="Listo para procesar")
        self.progress_label.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))

        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=5, pady=2)

        self.percentage_label = ttk.Label(self, text="0%")
        self.percentage_label.grid(row=2, column=0, sticky="e", padx=5, pady=(2, 5))

    def set_total(self, total):
        self.total = total
        self.current = 0
        self.progress_bar['maximum'] = total
        self.progress_bar['value'] = 0
        self.update_labels()

    def update_progress(self, current):
        self.current = current
        self.progress_bar['value'] = current
        self.update_labels()

    def update_labels(self):
        if self.total > 0:
            percentage = int((self.current / self.total) * 100)
            self.progress_label.config(text=f"Procesando: {self.current} de {self.total}")
            self.percentage_label.config(text=f"{percentage}%")
        else:
            self.progress_label.config(text="Listo para procesar")
            self.percentage_label.config(text="0%")

    def reset(self):
        self.total = 0
        self.current = 0
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Listo para procesar")
        self.percentage_label.config(text="0%")
