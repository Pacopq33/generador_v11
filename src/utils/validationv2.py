import os
import subprocess
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
            ("MiKTeX", self.verify_miktex_installed),
            ("Plantilla LaTeX", self.verify_template_exists),
            ("Permisos de escritura", self.verify_write_permissions),
            ("Directorio assets", self.verify_assets_directory),
            ("Imágenes disponibles", self.verify_images_available)
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

    def verify_miktex_installed(self):
        """Verificar que MiKTeX esté instalado y XeLaTeX esté en el PATH"""
        cache_key = "miktex_installed"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            result = subprocess.run(
                ['xelatex', '--version'],
                capture_output=True,
                text=True,
                check=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            self.logger.success(f"XeLaTeX verificado: {result.stdout.splitlines()[0]}")
            self._cache[cache_key] = True
            return True
        except FileNotFoundError:
            self.logger.error("XeLaTeX no encontrado. Asegúrese de que MiKTeX o TeX Live esté instalado y en el PATH.")
            self._cache[cache_key] = False
            return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error al ejecutar XeLaTeX: {e.stderr}")
            self._cache[cache_key] = False
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado al verificar XeLaTeX: {type(e).__name__}: {str(e)}")
            self._cache[cache_key] = False
            return False

    def verify_template_exists(self):
        """Verificar que la plantilla LaTeX exista"""
        cache_key = "template_exists"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        template_path = get_resource_path(os.path.join("assets", "plantilla6.tex"))
        result = os.path.exists(template_path) and os.path.isfile(template_path)
        if not result:
            self.logger.error(f"Plantilla LaTeX no encontrada en: {template_path}")
        self._cache[cache_key] = result
        return result

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

    def verify_images_available(self):
        """Verificar que al menos una imagen esté disponible"""
        cache_key = "images_available"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        assets_dir = get_resource_path("assets")
        image_files = ['logomejor.png', 'logov2.png']
        
        for image_file in image_files:
            image_path = os.path.join(assets_dir, image_file)
            if os.path.exists(image_path):
                self._cache[cache_key] = True
                return True
                
        self.logger.error(f"No se encontraron imágenes en: {assets_dir}")
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