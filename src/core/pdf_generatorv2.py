import io
import os
import tempfile
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from .latex_processorv2 import LaTeXProcessor
from ..utils.loggerv2 import AppLogger  # Cambiado a AppLogger

class PDFGenerator:
    """Generador de certificados PDF"""

    FRAME_MARGIN_CM = 0.2
    FRAME_LINE_WIDTH_PT = 0.5

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
                    if self.add_decorative_frame(pdf_path):
                        self.logger.success(f"Certificado generado: {pdf_path}")
                        return True
                    else:
                        self.logger.error(f"No se pudo aplicar el marco decorativo al PDF: {pdf_path}")
                        return False
                else:
                    self.logger.error(f"PDF no encontrado después de compilación: {pdf_path}")
                    return False
            else:
                self.logger.error(f"Error compilando certificado: {filename}")
                return False
        except Exception as e:
            self.logger.error(f"Error generando certificado para {data.get('nombre_apellido', 'Desconocido')}: {type(e).__name__}: {str(e)}")
            return False

    def add_decorative_frame(self, pdf_path):
        """Agregar un marco decorativo al PDF generado."""
        temp_output_path = None
        try:
            if not os.path.exists(pdf_path):
                self.logger.error(f"Archivo PDF no encontrado para aplicar marco: {pdf_path}")
                return False

            temp_dir = os.path.dirname(pdf_path) or '.'

            with open(pdf_path, 'rb') as pdf_file:
                reader = PdfReader(pdf_file)
                writer = PdfWriter()
                overlays = []

                for page_number, page in enumerate(reader.pages, start=1):
                    width = float(page.mediabox.width)
                    height = float(page.mediabox.height)
                    overlay_reader = self.create_frame_overlay(width, height)
                    overlays.append(overlay_reader)
                    overlay_page = overlay_reader.pages[0]
                    page.merge_page(overlay_page)
                    writer.add_page(page)
                    self.logger.debug(
                        f"Marco decorativo aplicado a la página {page_number} ({width:.2f}x{height:.2f} pt)"
                    )

                if reader.metadata:
                    try:
                        metadata = {
                            key: str(value)
                            for key, value in reader.metadata.items()
                            if isinstance(key, str) and value is not None
                        }
                        if metadata:
                            writer.add_metadata(metadata)
                    except Exception:
                        self.logger.debug("No fue posible copiar los metadatos del PDF original.")

            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', dir=temp_dir) as temp_output:
                writer.write(temp_output)
                temp_output_path = temp_output.name

            os.replace(temp_output_path, pdf_path)
            self.logger.info(f"Marco decorativo agregado correctamente en: {pdf_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error agregando marco decorativo a {pdf_path}: {type(e).__name__}: {str(e)}")
            if temp_output_path and os.path.exists(temp_output_path):
                try:
                    os.unlink(temp_output_path)
                except OSError:
                    self.logger.debug(f"No se pudo eliminar el archivo temporal del marco: {temp_output_path}")
            return False

    def create_frame_overlay(self, width, height):
        """Crear un PDF temporal con el marco decorativo."""
        margin = self.cm_to_points(self.FRAME_MARGIN_CM)

        packet = io.BytesIO()
        frame_canvas = canvas.Canvas(packet, pagesize=(width, height))
        frame_canvas.setLineWidth(self.FRAME_LINE_WIDTH_PT)
        frame_canvas.rect(margin, margin, width - 2 * margin, height - 2 * margin)
        frame_canvas.save()
        packet.seek(0)
        return PdfReader(packet)

    @staticmethod
    def cm_to_points(cm_value):
        """Convertir centímetros a puntos tipográficos."""
        return cm_value * 28.3464567

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