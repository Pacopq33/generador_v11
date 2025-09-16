#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Certificados Académicos
Aplicación de escritorio para generar certificados en PDF desde datos Excel
"""

import sys
import os
import time
import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from src.gui.main_windowv3 import MainWindow
from src.utils.loggerv2 import AppLogger
from src.utils.validationv2 import SystemValidator
from src.utils.resource_utils import get_resource_path

def show_splash_screen(root, logger):
    """Muestra una ventana de carga con logo, título y barra de progreso determinada"""
    # Registrar inicio de la función para depuración
    logger.info("Iniciando show_splash_screen")
    try:
        # Crear una ventana Toplevel para el splash screen
        splash = tk.Toplevel(root)
        # Eliminar bordes y barra de título para un diseño limpio
        splash.overrideredirect(True)
        # Establecer tamaño de 400x350 píxeles y centrar en la pantalla
        splash.geometry("400x350+{}+{}".format(
            root.winfo_screenwidth() // 2 - 200,
            root.winfo_screenheight() // 2 - 175
        ))
        
        # Configurar fondo negro para la ventana
        splash.configure(bg="#000000")
        logger.info("Ventana splash creada con fondo negro")
        
        # Crear etiqueta para el título "Iniciando aplicación"
        title_label = ttk.Label(
            splash,
            text="Iniciando aplicación",
            font=("Arial", 14, "bold"),
            anchor="center",
            foreground="#FFFFFF",  # Letras blancas
            background="#000000"   # Fondo negro
        )
        # Colocar el título en la parte superior con un margen
        title_label.pack(pady=10)
        logger.info("Título de splash screen creado (blanco sobre negro)")
        
        # Crear etiqueta para el subtítulo "Iniciando aplicación"
        subtitle_label = ttk.Label(
            splash,
            text="hecho por Fede de la UTN",
            font=("Times", 12, "italic", "bold"),
            anchor="center",
            foreground="#FFFFFF",  # Letras blancas
            background="#000000"   # Fondo negro
        )
        # Colocar el título en la parte superior con un margen
        subtitle_label.pack(pady=10)
        logger.info("Título de splash screen creado (blanco sobre negro)")
        
        # Cargar y mostrar el logo
        try:
            # Obtener la ruta del logo usando get_resource_path
            logo_path = get_resource_path(os.path.join("assets", "logov2.png"))
            logger.info(f"Intentando cargar logo desde: {logo_path}")
            # Cargar la imagen PNG
            logo_img = tk.PhotoImage(file=logo_path)
            # Redimensionar la imagen si es demasiado grande (máximo 200x100)
            if logo_img.width() > 200 or logo_img.height() > 100:
                logo_img = logo_img.subsample(2, 2)  # Reducir a la mitad
                logger.info("Logo redimensionado para ajustarse al splash")
            # Crear etiqueta para mostrar el logo
            logo_label = ttk.Label(splash, image=logo_img, background="#000000")
            # Mantener referencia para evitar recolección de basura
            logo_label.image = logo_img
            # Colocar el logo centrado con un margen
            logo_label.pack(pady=10, expand=False)
            logger.info("Logo cargado y mostrado correctamente")
        except Exception as e:
            # Registrar error si no se puede cargar el logo
            logger.error(f"Error cargando logo: {e}")
            # Mostrar mensaje de error en la ventana
            error_label = ttk.Label(
                splash,
                text=f"Error cargando logo: {str(e)}",
                font=("Arial", 10),
                foreground="#FFFFFF",
                background="#000000"
            )
            error_label.pack(pady=10)
        
        # Configurar estilo personalizado para la barra de progreso
        style = ttk.Style()
        # Crear un estilo para la barra de progreso con color azul
        style.configure("blue.Horizontal.TProgressbar",
                       troughcolor="#000000",  # Fondo del trough negro
                       background="#1E90FF",   # Barra azul
                       bordercolor="#000000")
        # Crear barra de progreso en modo determinado
        progress = ttk.Progressbar(
            splash,
            mode="determinate",
            style="blue.Horizontal.TProgressbar",
            maximum=100  # Valor máximo para el progreso
        )
        # Colocar la barra de progreso en la parte inferior con márgenes
        progress.pack(fill="x", padx=20, pady=20)
        logger.info("Barra de progreso determinada creada")
        
        # Forzar actualización de la ventana para asegurar renderizado
        splash.update()
        logger.info("Ventana splash actualizada")
        
        # Devolver la ventana splash y la barra de progreso para actualizarla
        return splash, progress
    except Exception as e:
        # Registrar cualquier error crítico
        logger.error(f"Error crítico en show_splash_screen: {e}")
        raise
    finally:
        # Registrar fin de la función
        logger.info("Fin de show_splash_screen")

def main():
    """Función principal de la aplicación"""
    try:
        # Configurar logging
        app_logger = AppLogger()
        app_logger.info("Iniciando Generador de Certificados Académicos")
        
        # Crear ventana raíz oculta inicialmente
        root = ThemedTk(theme="arc")
        root.withdraw()
        app_logger.info("Ventana raíz creada y oculta")
        
        # Mostrar splash screen y obtener la barra de progreso
        app_logger.info("Mostrando ventana de carga")
        splash, progress = show_splash_screen(root, app_logger)
        root.update_idletasks()
        app_logger.info("Ventana de carga mostrada")
        
        # Actualizar progreso: 20% después de crear el splash
        progress["value"] = 20
        splash.update()
        app_logger.info("Progreso actualizado: 20%")
        
        # Validar sistema antes de iniciar
        validator = SystemValidator()
        app_logger.info("Ejecutando validación del sistema...")
        system_valid = validator.validate_system()
        app_logger.info("Validación del sistema completada")
        
        # Actualizar progreso: 50% después de la validación
        progress["value"] = 50
        splash.update()
        app_logger.info("Progreso actualizado: 50%")
        
        # Cargar ventana principal en el hilo principal
        try:
            app_logger.info("Inicio de load_main_window")
            app = MainWindow(root, app_logger)
            app_logger.info("MainWindow creado exitosamente")
            
            # Actualizar progreso: 100% después de inicializar MainWindow
            progress["value"] = 100
            splash.update()
            app_logger.info("Progreso actualizado: 100%")
            
            # Retardo final para mostrar el progreso completo
            time.sleep(0.5)
            
            def on_closing():
                app_logger.info("Cerrando aplicación")
                root.destroy()
            
            root.protocol("WM_DELETE_WINDOW", on_closing)
            
            # Mostrar ventana principal y cerrar splash
            app_logger.info("Mostrando ventana principal y cerrando splash")
            progress.stop()  # Detener cualquier animación residual
            root.deiconify()
            splash.destroy()
            app_logger.info("Ventana principal mostrada, splash destruido")
            
            # Mostrar mensaje si la validación falló
            if not system_valid:
                app_logger.error("Validación del sistema falló. Revise los requisitos.")
                root.after(0, lambda: messagebox.showerror(
                    "Error de Configuración",
                    "No se cumplieron todos los requisitos del sistema. Revise los logs para más detalles."
                ))
            
            root.mainloop()
        except Exception as e:
            import traceback
            app_logger.error(f"Error crítico al crear ventana principal: {e}")
            traceback.print_exc(file=sys.stderr)
            if 'splash' in locals():
                progress.stop()  # Detener barra antes de cerrar
                splash.destroy()
            root.destroy()
            app_logger.info("Aplicación terminada debido a un error. Presione Enter para salir...")
            input("Presione Enter para salir...")
        
    except Exception as e:
        import traceback
        app_logger.error(f"Error crítico al iniciar la aplicación: {e}")
        traceback.print_exc(file=sys.stderr)
        if 'splash' in locals():
            progress.stop()  # Detener barra antes de cerrar
            splash.destroy()
        root.destroy()
        app_logger.info("Aplicación terminada debido a un error. Presione Enter para salir...")
        input("Presione Enter para salir...")

if __name__ == "__main__":
    main()