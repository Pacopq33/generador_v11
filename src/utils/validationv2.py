import importlib
import os
import tempfile

from .loggerv2 import AppLogger
from .resource_utils import get_resource_path  # Importar desde resource_utils

class SystemValidator:
    """Clase para manejar validaciones del sistema con caché"""
    
    def __init__(self):
        self._cache = {}
        self.logger = AppLogger()

    def validate_system(self):
        """Validar que el sistema esté listo para funcionar"""
        checks = [
            ("Librería ReportLab", self.verify_reportlab_available),
            ("Directorio assets", self.verify_assets_directory),
            ("Logo del certificado", self.verify_logo_available),
            ("Permisos de escritura", self.verify_write_permissions),
        ]
        
        all_passed = True
        
        for check_name, check_function in checks:
            try:
                if check_function():
                    self.logger.success(f"✓ {check_name}: OK")
                else:
                    self.logger.error(f"✗ {check_name}: FALLO")
                    all_passed = False
            except Exception as e:
                self.logger.error(f"✗ {check_name}: ERROR - {e}")
                all_passed = False
                
        return all_passed

    def verify_reportlab_available(self):
        """Verificar que ReportLab esté instalado."""
        cache_key = "reportlab_available"
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            importlib.import_module("reportlab")
            self._cache[cache_key] = True
            return True
        except ModuleNotFoundError as exc:
            self.logger.error(
                f"ReportLab no está disponible: {exc}. Instale las dependencias con 'pip install -r requirements.txt'."
            )
            self._cache[cache_key] = False
            return False
        except Exception as exc:  # pragma: no cover
            self.logger.error(f"Error al comprobar ReportLab: {type(exc).__name__}: {exc}")
            self._cache[cache_key] = False
            return False

    def verify_write_permissions(self):
        """Verificar permisos de escritura en directorio temporal"""
        cache_key = "write_permissions"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            with tempfile.NamedTemporaryFile(delete=True) as temp_file:
                temp_file.write(b"test")
                self._cache[cache_key] = True
                return True
        except Exception as e:
            self.logger.error(f"Error al verificar permisos de escritura: {e}")
            self._cache[cache_key] = False
            return False

    def verify_assets_directory(self):
        """Verificar que el directorio assets exista"""
        cache_key = "assets_directory"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        assets_dir = get_resource_path("assets")
        result = os.path.exists(assets_dir) and os.path.isdir(assets_dir)
        if not result:
            self.logger.error(f"Directorio assets no encontrado en: {assets_dir}")
        self._cache[cache_key] = result
        return result

    def verify_logo_available(self):
        """Verificar que el logo principal esté disponible"""
        cache_key = "logo_available"
        if cache_key in self._cache:
            return self._cache[cache_key]

        assets_dir = get_resource_path("assets")
        logo_path = os.path.join(assets_dir, "logomejor.png")

        if os.path.exists(logo_path):
            self._cache[cache_key] = True
            return True

        self.logger.error(f"Logo del certificado no encontrado en: {logo_path}")
        self._cache[cache_key] = False
        return False

def validate_excel_file(file_path):
    """Validar archivo Excel"""
    logger = AppLogger()
    if not os.path.exists(file_path):
        logger.error(f"Validación de archivo Excel fallida: Archivo no encontrado - {file_path}")
        return False, "Archivo no encontrado"
        
    if not file_path.lower().endswith(('.xlsx', '.xls')):
        logger.error(f"Validación de archivo Excel fallida: Formato no válido - {file_path}")
        return False, "Formato de archivo no válido"
        
    try:
        import pandas as pd
        df = pd.read_excel(file_path, nrows=1)
        logger.success(f"Validación de archivo Excel exitosa: {file_path}")
        return True, "Archivo válido"
    except Exception as e:
        logger.error(f"Error leyendo archivo Excel: {e}")
        return False, f"Error leyendo archivo: {e}"

def validate_output_directory(dir_path):
    """Validar directorio de salida"""
    logger = AppLogger()
    if not os.path.exists(dir_path):
        logger.error(f"Validación de directorio fallida: Directorio no existe - {dir_path}")
        return False, "Directorio no existe"
        
    if not os.path.isdir(dir_path):
        logger.error(f"Validación de directorio fallida: No es un directorio - {dir_path}")
        return False, "La ruta no es un directorio"
        
    if not os.access(dir_path, os.W_OK):
        logger.error(f"Validación de directorio fallida: Sin permisos de escritura - {dir_path}")
        return False, "Sin permisos de escritura"
        
    logger.success(f"Validación de directorio exitosa: {dir_path}")
    return True, "Directorio válido"

def validate_data_completeness(data):
    """Validar completitud de datos"""
    logger = AppLogger()
    required_fields = ['nombre_apellido', 'dni', 'carrera', 'dispo', 'dia', 'mes']
    
    missing_fields = []
    for field in required_fields:
        if field not in data or not data[field] or str(data[field]).strip() == '':
            missing_fields.append(field)
            
    if missing_fields:
        logger.error(f"Validación de datos fallida: Campos faltantes - {', '.join(missing_fields)}")
        return False, f"Campos faltantes: {', '.join(missing_fields)}"
        
    logger.success("Validación de datos exitosa: Todos los campos completos")
    return True, "Datos completos"
