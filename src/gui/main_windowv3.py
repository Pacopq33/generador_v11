import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from ttkthemes import ThemedTk
import os
import threading
from PIL import Image, ImageTk  # Añadido para redimensionar la imagen

from src.gui.components.file_selectorv3 import FileSelector
from src.gui.components.data_tablev3 import DataTable
from src.gui.components.log_consolev3 import LogConsole
from src.gui.components.progress_barv3 import ProgressBar
from src.core.excel_handlerv2 import ExcelHandler
from src.core.pdf_generatorv2 import PDFGenerator
from src.utils.loggerv2 import AppLogger
from src.utils.validationv2 import SystemValidator
from src.utils.resource_utils import get_resource_path  # Añadido para logo.png

class MainWindow:
    def __init__(self, root: ThemedTk, logger: AppLogger):
        self.logger = logger
        self.logger.info("Iniciando MainWindow.__init__")
        
        self.root = root
        self.excel_handler = ExcelHandler()
        self.logger.info("ExcelHandler inicializado")
        self.pdf_generator = PDFGenerator()
        self.logger.info("PDFGenerator inicializado")
        
        self.excel_file_path = None
        self.output_folder = None
        self.processing = False
        self.cancel_processing = False
        self.environment_ok = False

        self.logger.info("Configurando GUI...")
        self.setup_gui()
        self.logger.info("GUI configurada, estableciendo consola de logs")
        self.logger.set_gui_console(self.log_console)
        self.logger.info("Iniciando verificación inicial del sistema")
        self._initial_system_check()
        self.logger.info("Verificación inicial del sistema completada")

        self.root.bind('<Control-o>', lambda e: self.file_selector.select_file())
        self.root.bind('<Control-g>', lambda e: self.generate_certificates() if self.btn_generate['state'] == 'normal' else None)
        self.root.bind('<Control-l>', lambda e: self.clear_data())

    def setup_gui(self):
        """Configura la interfaz gráfica de la ventana principal"""
        self.logger.info("Inicio de setup_gui")
        # Establecer título y tamaño inicial de la ventana
        self.root.title("Generador de Certificados Académicos")
        # Definir tamaño de la ventana
        window_width, window_height = 1200, 650
        # Obtener dimensiones de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        # Calcular coordenadas para centrar la ventana
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2 - 45
        # Establecer tamaño y posición centrada
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(1000, 450)

        # Configurar el layout principal con grid para responsividad
        self.root.grid_columnconfigure(1, weight=3)  # Panel derecho más ancho
        self.root.grid_columnconfigure(0, weight=1)  # Panel izquierdo fijo
        self.root.grid_rowconfigure(0, weight=1)    # Expandir verticalmente

        # Crear panel izquierdo
        self.logger.info("Creando panel izquierdo")
        self.left_panel = ttk.Frame(self.root)
        self.left_panel.grid(row=0, column=0, sticky="ns", padx=10, pady=10)
        self.left_panel.grid_columnconfigure(0, weight=1)

        # Crear panel derecho
        self.logger.info("Creando panel derecho")
        self.right_panel = ttk.Frame(self.root)
        self.right_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(1, weight=1)  # DataTable expande
        self.right_panel.grid_rowconfigure(2, weight=1)  # LogConsole expande

        # === Panel izquierdo ===
        self.logger.info("Creando FileSelector")
        self.file_selector = FileSelector(self.left_panel, self._load_excel_data)
        self.file_selector.pack(fill="x", pady=5)

        self.logger.info("Creando etiquetas de archivo y carpeta")
        self.excel_label = ttk.Label(self.left_panel, text="Archivo: Ninguno")
        self.excel_label.pack(fill="x", pady=2)

        self.output_label = ttk.Label(self.left_panel, text="Carpeta: Ninguna")
        self.output_label.pack(fill="x", pady=2)

        self.logger.info("Creando botones del panel izquierdo")
        self.btn_output_folder = ttk.Button(self.left_panel, text="📁 Carpeta Salida", command=self.select_output_folder)
        self.btn_output_folder.pack(fill="x", pady=2)

        self.btn_generate = ttk.Button(self.left_panel, text="GENERAR CERTIFICADOS", command=self.generate_certificates, state="disabled")
        self.btn_generate.pack(fill="x", pady=2)

        self.btn_cancel = ttk.Button(self.left_panel, text="CANCELAR", command=self.cancel_generation, state="disabled")
        self.btn_cancel.pack(fill="x", pady=2)

        # Mover btn_validate al panel izquierdo
        self.btn_validate = ttk.Button(self.left_panel, text="Validar Datos", command=self.validate_data)
        self.btn_validate.pack(fill="x", pady=2)

        # Mover btn_clear al panel izquierdo
        self.btn_clear = ttk.Button(self.left_panel, text="Limpiar Todo", command=self.clear_data)
        self.btn_clear.pack(fill="x", pady=2)

        self.logger.info("Creando ProgressBar")
        self.progress_bar = ProgressBar(self.left_panel)
        self.progress_bar.pack(fill="x", pady=10)

        # Crear cuadro para el logo que ocupa el espacio libre
        self.logger.info("Creando cuadro para logo.png")
        try:
            # Obtener la ruta del logo usando get_resource_path
            logo_path = get_resource_path(os.path.join("assets", "logov2.png"))
            self.logger.info(f"Intentando cargar logo desde: {logo_path}")
            # Cargar la imagen con PIL para redimensionarla sin deformar
            logo_image = Image.open(logo_path)
            # Calcular tamaño para ajustar al panel (máximo 200x150 para balance)
            max_width, max_height = 200, 150
            logo_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)  # Mantener relación de aspecto
            logo_photo = ImageTk.PhotoImage(logo_image)
            # Crear etiqueta para el logo
            self.logo_label = ttk.Label(self.left_panel, image=logo_photo, background="#f0f0f0", anchor="center")
            self.logo_label.image = logo_photo  # Mantener referencia
            # Colocar al final, ocupando el espacio libre
            self.logo_label.pack(fill="both", expand=True, pady=10)
            self.logger.info("Logo cargado y mostrado en el panel izquierdo")
        except Exception as e:
            # Mostrar mensaje de error si no se puede cargar el logo
            self.logger.error(f"Error cargando logo: {e}")
            error_label = ttk.Label(
                self.left_panel,
                text=f"Error cargando logo: {str(e)}",
                font=("Arial", 10),
                foreground="red"
            )
            error_label.pack(fill="both", expand=True, pady=10)

        self.logger.info("Creando etiqueta de versión")
        self.footer_label = ttk.Label(self.left_panel, text="Versión 1.0")
        self.footer_label.pack(side="bottom", pady=10)

        # === Panel derecho ===
        self.logger.info("Creando elementos del panel derecho")
        self.title_label = ttk.Label(self.right_panel, text="Generador de Títulos - UTN - INSPT", font=("Arial", 14, "bold"))
        self.title_label.pack(pady=10)

        self.logger.info("Creando DataTable")
        self.data_table = DataTable(self.right_panel)
        self.data_table.pack(fill="both", expand=True, pady=5)

        self.logger.info("Creando StatusLabel")
        self.status_label = ttk.Label(self.right_panel, text="Iniciando...", anchor="w")
        self.status_label.pack(fill="x")

        self.logger.info("Creando LogConsole")
        self.log_console = LogConsole(self.right_panel)
        self.log_console.pack(fill="both", expand=True)

        self.logger.info("Fin de setup_gui")

    def _initial_system_check(self):
        self.logger.info("Inicio de _initial_system_check")
        self.status_label.config(text="Verificando recursos del sistema...")
        self.root.update_idletasks()

        validator = SystemValidator()
        if validator.validate_system():
            self.environment_ok = True
            self.logger.success("Validación de recursos completada. Sistema listo.")
            self.status_label.config(text="Recursos listos")
        else:
            self.environment_ok = False
            self.logger.error("Faltan recursos para generar certificados.")
            self.status_label.config(text="Recursos incompletos")
            self.root.after(0, lambda: messagebox.showerror(
                "Recursos faltantes",
                "No se encontraron todos los recursos necesarios.\nRevise el log para más detalles."
            ))

        self.logger.info("Verificando estado de generación")
        self.check_ready_to_generate()
        self.logger.info("Fin de _initial_system_check")

    def _load_excel_data(self, file_path):
        self.logger.info(f"Inicio de _load_excel_data: {file_path}")
        if not file_path:
            self.logger.info("Selección de archivo cancelada.")
            return

        def update_ui(data, error=None):
            if data is not None:
                self.data_table.load_data(data)
                self.excel_file_path = file_path
                self.excel_label.config(text=f"Archivo: {os.path.basename(file_path)}")
                self.logger.success(f"Excel cargado: {len(data)} registros")
                self.status_label.config(text="Excel Cargado")
            else:
                self.status_label.config(text="Error al cargar Excel")
                messagebox.showerror("Error", f"No se pudo cargar el archivo Excel:\n{error}")
            self.check_ready_to_generate()

        try:
            self.status_label.config(text="Cargando Excel...")
            self.root.update()
            data = self.excel_handler.load_excel(file_path)
            self.root.after(0, update_ui, data)
        except Exception as e:
            self.root.after(0, update_ui, None, str(e))
        self.logger.info("Fin de _load_excel_data")

    def select_output_folder(self):
        self.logger.info("Inicio de select_output_folder")
        folder_path = filedialog.askdirectory(title="Seleccionar carpeta de salida")
        if folder_path:
            self.output_folder = folder_path
            self.output_label.config(text=f"Carpeta: {os.path.basename(folder_path)}")
            self.logger.info(f"Carpeta seleccionada: {folder_path}")
            self.check_ready_to_generate()
        self.logger.info("Fin de select_output_folder")

    def check_ready_to_generate(self):
        self.logger.info("Inicio de check_ready_to_generate")
        ready = (
            self.excel_file_path is not None and
            self.output_folder is not None and
            self.data_table.has_data() and
            not self.processing and
            self.environment_ok
        )
        self.btn_generate.config(state="normal" if ready else "disabled")
        self.btn_cancel.config(state="normal" if self.processing else "disabled")
        self.logger.info(f"Estado de generación: {'Listo' if ready else 'No listo'}")
        return ready

    def generate_certificates(self):
        self.logger.info("Inicio de generate_certificates")
        if self.processing:
            self.logger.warning("Generación ya en curso")
            return

        selected_data = self.data_table.get_selected_data()
        if not selected_data:
            messagebox.showwarning("Advertencia", "No hay registros seleccionados.")
            self.logger.warning("No hay registros seleccionados")
            return

        self.logger.info(f"Datos seleccionados: {len(selected_data)} registros")
        self.processing = True
        self.cancel_processing = False
        self.btn_generate.config(state="disabled")
        self.btn_cancel.config(state="normal")
        self.progress_bar.set_total(len(selected_data))
        self.status_label.config(text="Generando Certificados...")
        try:
            self._generate_certificates_thread(selected_data)  # Ejecutar directamente
            self.logger.info("Generación finalizada")
        except Exception as e:
            self.logger.error(f"Error crítico en generate_certificates: {type(e).__name__}: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error Crítico", f"Error en la generación: {str(e)}"))
        finally:
            self._restore_interface()

    def _generate_certificates_thread(self, data):
        self.logger.info("Inicio de _generate_certificates_thread")
        try:
            total = len(data)
            generated = 0

            for i, row in enumerate(data):
                if self.cancel_processing:
                    self.logger.warning("Cancelación solicitada por el usuario.")
                    break

                try:
                    self.logger.info(f"Procesando certificado {i+1}/{total}: {row.get('nombre_apellido', 'Desconocido')}")
                    if self.pdf_generator.generate_certificate(row, self.output_folder):
                        generated += 1
                        self.logger.success(f"Certificado generado: {row['nombre_apellido']}")
                    else:
                        self.logger.error(f"Error generando certificado: {row['nombre_apellido']}")
                except Exception as e:
                    self.logger.error(f"Error al generar certificado para {row.get('nombre_apellido', 'Desconocido')}: {type(e).__name__}: {str(e)}")
                    self.root.after(0, lambda: messagebox.showerror(
                        "Error",
                        f"Error generando certificado para {row.get('nombre_apellido', 'Desconocido')}: {str(e)}"
                    ))

                self.progress_bar.update_progress(i + 1)

            if not self.cancel_processing:
                self.logger.success(f"Generación completada: {generated}/{total}")
                self.root.after(0, lambda: messagebox.showinfo(
                    "Completado",
                    f"{generated} de {total} certificados generados."
                ))
            else:
                self.logger.info("Proceso cancelado por el usuario.")
        except Exception as e:
            self.logger.error(f"Error crítico en _generate_certificates_thread: {type(e).__name__}: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Error Crítico", f"Error en la generación: {str(e)}"))
        finally:
            self.logger.info("Fin de _generate_certificates_thread")

    def _restore_interface(self):
        self.logger.info("Inicio de _restore_interface")
        self.processing = False
        self.btn_generate.config(state="normal" if self.check_ready_to_generate() else "disabled")
        self.btn_cancel.config(state="disabled")
        self.status_label.config(text="Sistema Listo")
        self.logger.info("Fin de _restore_interface")

    def cancel_generation(self):
        self.logger.info("Inicio de cancel_generation")
        self.cancel_processing = True
        self.logger.warning("Cancelación en curso...")
        self.logger.info("Fin de cancel_generation")

    def clear_data(self):
        self.logger.info("Inicio de clear_data")
        self.data_table.clear_data()
        self.log_console.clear_logs()
        self.excel_file_path = None
        self.output_folder = None
        self.excel_label.config(text="Archivo: Ninguno")
        self.output_label.config(text="Carpeta: Ninguna")
        self.file_selector.clear_selection()
        self.check_ready_to_generate()
        self.logger.info("Datos limpiados.")
        self.logger.info("Fin de clear_data")

    def validate_data(self):
        self.logger.info("Inicio de validate_data")
        if not self.data_table.has_data():
            messagebox.showwarning("Advertencia", "No hay datos para validar.")
            self.logger.warning("No hay datos para validar")
            return

        try:
            data = self.data_table.get_all_data()
            result = self.excel_handler.validate_data(data)

            if result['valid']:
                self.logger.success("Datos válidos.")
                messagebox.showinfo("Validación", "Todos los datos son correctos.")
            else:
                errors = result['errors']
                msg = "\n".join(errors[:10])
                if len(errors) > 10:
                    msg += f"\n... y {len(errors)-10} más."
                self.logger.warning(f"Errores encontrados: {len(errors)}")
                messagebox.showwarning("Errores de Validación", msg)
        except Exception as e:
            self.logger.error(str(e))
            messagebox.showerror("Error", str(e))
        self.logger.info("Fin de validate_data")