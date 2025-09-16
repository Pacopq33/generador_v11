import tkinter as tk
from tkinter import ttk
from datetime import datetime

class LogConsole(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.title_frame = ttk.Frame(self)
        self.title_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)

        self.title_label = ttk.Label(self.title_frame, text="Consola de Logs", font=("Arial", 11, "bold"))
        self.title_label.pack(side="left")

        self.clear_button = ttk.Button(self.title_frame, text="Limpiar", command=self.clear_logs)
        self.clear_button.pack(side="right")

        self.text_frame = ttk.Frame(self)
        self.text_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.text_frame.grid_columnconfigure(0, weight=1)
        self.text_frame.grid_rowconfigure(0, weight=1)

        self.scrollbar = ttk.Scrollbar(self.text_frame)
        self.scrollbar.pack(side="right", fill="y")

        # Note: tk.Text is used as ttk.Text doesn't exist, but theme is applied via ttkthemes
        self.text_widget = tk.Text(
            self.text_frame,
            wrap=tk.WORD,
            yscrollcommand=self.scrollbar.set,
            font=("Courier New", 10),
            bg="#2E2E2E",  # Dark background for better contrast
            fg="white",
            insertbackground="white",
            state=tk.DISABLED,
            relief="flat"
        )
        self.text_widget.pack(fill="both", expand=True)
        self.scrollbar.config(command=self.text_widget.yview)

        self.setup_tags()

    def setup_tags(self):
        self.text_widget.tag_configure("INFO", foreground="#AAAAAA")
        self.text_widget.tag_configure("OK", foreground="#00FF00")
        self.text_widget.tag_configure("PROC", foreground="#00CED1")
        self.text_widget.tag_configure("ERROR", foreground="#FF5555")
        self.text_widget.tag_configure("WARN", foreground="#FFA500")
        self.text_widget.tag_configure("TIMESTAMP", foreground="#666666")

    def add_log(self, message, log_type="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, f"[{timestamp}] ", "TIMESTAMP")
        self.text_widget.insert(tk.END, f"{message}\n", log_type)
        self.text_widget.config(state=tk.DISABLED)
        self.text_widget.see(tk.END)

    def clear_logs(self):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.delete(1.0, tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def info(self, message):
        self.add_log(message, "INFO")

    def success(self, message):
        self.add_log(message, "OK")

    def warning(self, message):
        self.add_log(message, "WARN")

    def error(self, message):
        self.add_log(message, "ERROR")

    def processing(self, message):
        self.add_log(message, "PROC")
