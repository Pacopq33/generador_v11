import logging
import sys
from datetime import datetime

# Logger global
_logger = None

def setup_logger():
    """Configurar logger principal (solo el logger base de Python)"""
    global _logger
    
    if _logger is None:
        _logger = logging.getLogger('CertificadosApp')
        _logger.setLevel(logging.DEBUG)
        
        # Handler para consola
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Crear directorio logs si no existe
        import os
        log_dir = 'logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Handler para archivo persistente
        file_handler = logging.FileHandler(os.path.join(log_dir, 'app.log'), encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # Formato
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        _logger.addHandler(console_handler)
        _logger.addHandler(file_handler)
        
    return _logger

def get_logger():
    """Obtener logger configurado (el logger base de Python)"""
    if _logger is None:
        return setup_logger()
    return _logger

class GUILogHandler(logging.Handler):
    """Handler personalizado para logging en GUI"""
    
    def __init__(self, gui_console):
        super().__init__()
        self.gui_console = gui_console
        
    def emit(self, record):
        """Emitir log a la consola GUI"""
        try:
            # Solo enviar al GUI si gui_console está inicializado
            if self.gui_console is None:
                # Redirigir al logger de consola si el GUI no está listo
                console_handler = logging.StreamHandler(sys.stdout)
                console_handler.setFormatter(logging.Formatter('%(message)s'))
                console_handler.emit(record)
                return
            
            # Formatear el mensaje sin el timestamp y nivel
            message_content = str(record.message)
            log_type = self.get_log_type(record.levelname, message_content)
            
            # Usar el método add_log de la consola GUI en el hilo principal
            self.gui_console.text_widget.after(0, self.gui_console.add_log, message_content, log_type)
                
        except Exception as e:
            # Loggear error al handler de consola por defecto
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - ERROR - GUILogHandler error: %(message)s'))
            console_handler.emit(logging.LogRecord(
                name=record.name,
                level=logging.ERROR,
                pathname=record.pathname,
                lineno=record.lineno,
                msg=f"Error in GUILogHandler: {e}",
                args=(),
                exc_info=None
            ))
            
    def get_log_type(self, level, message_content):
        """Mapear nivel de logging a tipo de GUI"""
        mapping = {
            'DEBUG': 'INFO',
            'INFO': 'INFO',
            'WARNING': 'WARN',
            'ERROR': 'ERROR',
            'CRITICAL': 'ERROR'
        }
        # Extraer el tipo de log personalizado si existe
        if "SUCCESS:" in message_content:
            return 'OK'
        if "PROCESSING:" in message_content:
            return 'PROC'
        return mapping.get(level, 'INFO')

class AppLogger:
    """Logger de aplicación con soporte GUI y métodos personalizados"""
    
    def __init__(self):
        self.logger = get_logger()
        self.gui_console = None
        
    def set_gui_console(self, console):
        """Establecer consola GUI y añadir el handler"""
        self.gui_console = console
        
        # Remover handlers GUI existentes para evitar duplicados
        for handler in self.logger.handlers[:]:
            if isinstance(handler, GUILogHandler):
                self.logger.removeHandler(handler)

        # Agregar handler GUI
        if console:
            gui_handler = GUILogHandler(console)
            gui_handler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(message)s')
            gui_handler.setFormatter(formatter)
            self.logger.addHandler(gui_handler)
        
    def info(self, message):
        self.logger.info(message)
            
    def warning(self, message):
        self.logger.warning(message)
            
    def error(self, message):
        self.logger.error(message)
            
    def success(self, message):
        self.logger.info(f"SUCCESS: {message}")

    def debug(self, message):
        self.logger.debug(message)
            
    def processing(self, message):
        self.logger.info(f"PROCESSING: {message}")