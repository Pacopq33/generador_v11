import os
from .latex_processorv2 import LaTeXProcessor
from ..utils.loggerv2 import AppLogger  # Cambiado a AppLogger

class PDFGenerator:
    """Generador de certificados PDF"""
    
    def __init__(self):
        self.logger = AppLogger()
        self.latex_processor = LaTeXProcessor()
        
    def generate_certificate(self, data, output_dir):
        """Generar un certificado individual"""
        try:
            self.logger.info(f"Generando certificado para: {data.get('nombre_apellido', 'Desconocido')}")
            tex_content = self.latex_processor.replace_placeholders(data)  # Corregido: solo pasar data
            filename = self.generate_filename(data)
            
            self.logger.info(f"Compilando archivo: {filename} en {output_dir}")
            success = self.latex_processor.compile_latex(tex_content, output_dir, filename)
            
            if success:
                pdf_path = os.path.join(output_dir, filename)
                if os.path.exists(pdf_path):
                    self.logger.success(f"Certificado generado: {pdf_path}")
                    return True
                else:
                    self.logger.error(f"PDF no encontrado después de compilación: {pdf_path}")
                    return False
            else:
                self.logger.error(f"Error compilando certificado: {filename}")
                return False
        except Exception as e:
            self.logger.error(f"Error generando certificado para {data.get('nombre_apellido', 'Desconocido')}: {type(e).__name__}: {str(e)}")
            return False
            
    def generate_filename(self, data):
        """Generar nombre de archivo para el certificado"""
        try:
            nombre = str(data.get('nombre_apellido', 'Sin_Nombre'))
            dni = str(data.get('dni', 'Sin_DNI'))
            
            nombre = self.clean_filename(nombre)
            dni = self.clean_filename(dni)
            
            return f"{nombre}_{dni}.pdf"
            
        except Exception as e:
            self.logger.warning(f"Error generando nombre de archivo: {e}")
            return "certificado.pdf"
            
    def clean_filename(self, filename):
        """Limpiar nombre de archivo de caracteres problemáticos"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        
        cleaned = filename
        for char in invalid_chars:
            cleaned = cleaned.replace(char, '_')
            
        cleaned = cleaned.replace(' ', '_')
        cleaned = cleaned.replace('ñ', 'n')
        cleaned = cleaned.replace('Ñ', 'N')
        
        accents = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U'
        }
        
        for accented, plain in accents.items():
            cleaned = cleaned.replace(accented, plain)
            
        return cleaned
        
    def generate_batch(self, data_list, output_dir, progress_callback=None):
        """Generar certificados por lotes"""
        results = {
            'total': len(data_list),
            'success': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, data in enumerate(data_list):
            try:
                self.logger.processing(f"Procesando certificado {i+1}/{results['total']}")  # Añadido processing
                success = self.generate_certificate(data, output_dir)
                
                if success:
                    results['success'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Error generando: {data.get('nombre_apellido', 'Desconocido')}")
                    
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f"Error procesando {data.get('nombre_apellido', 'Desconocido')}: {e}")
                
            if progress_callback:
                progress_callback(i + 1, results['total'])
                
        self.logger.success(f"Generación por lotes completada: {results['success']}/{results['total']} certificados")  # Cambiado a success
        return results