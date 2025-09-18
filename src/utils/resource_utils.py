import sys
import os

def get_resource_path(relative_path):
    """Obtiene la ruta correcta para recursos empaquetados con PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
