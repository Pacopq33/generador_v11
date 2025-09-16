import os
import re
import tempfile
import subprocess
import shutil
from ..utils.loggerv2 import AppLogger
from ..utils.resource_utils import get_resource_path

class LaTeXProcessor:
    """Procesador para compilación LaTeX"""
    
    ETIQUETAS_LATEX = [
        '{{NOMBRE_APELLIDO}}',
        '{{DNI}}',
        '{{CARRERA}}',
        '{{DISPO}}',
        '{{DIA}}',
        '{{MES}}'
    ]
    
    def __init__(self):
        self.logger = AppLogger()
        self.template_path = os.path.join("assets", "plantilla6.tex")
        self.image_filename = "logomejor.png"
        self.image_source_subdir = "assets"
        # Verificar XeLaTeX al inicializar
        if not self.verify_miktex():
            raise RuntimeError("XeLaTeX no está disponible. No se puede continuar.")

    def load_template(self):
        """Cargar plantilla LaTeX"""
        try:
            full_template_path = get_resource_path(self.template_path)
            if not os.path.exists(full_template_path):
                raise FileNotFoundError(f"Plantilla no encontrada: {full_template_path}")
            with open(full_template_path, 'r', encoding='utf-8') as file:
                self.logger.success(f"Plantilla cargada: {full_template_path}")
                return file.read()
        except Exception as e:
            self.logger.error(f"Error cargando plantilla: {type(e).__name__}: {str(e)}")
            raise

    def replace_placeholders(self, data):
        """Reemplazar placeholders en la plantilla"""
        try:
            self.logger.debug(f"Datos de entrada para reemplazo: {data}")
            template = self.load_template()
            replacements = {
                '{{NOMBRE_APELLIDO}}': self.escape_latex(data.get('nombre_apellido', '')),
                '{{DNI}}': str(data.get('dni', '')),
                '{{CARRERA}}': self.escape_latex(data.get('carrera', '')),
                '{{DISPO}}': str(data.get('dispo', '')),
                '{{DIA}}': str(data.get('dia', '')),
                '{{MES}}': self.escape_latex(data.get('mes', ''))
            }
            for placeholder, value in replacements.items():
                template = template.replace(placeholder, value)
            self.logger.success("Placeholders reemplazados correctamente")
            self.logger.debug(f"Contenido .tex generado:\n{template}")
            return template
        except Exception as e:
            self.logger.error(f"Error reemplazando placeholders: {type(e).__name__}: {str(e)}")
            raise

    def escape_latex(self, text):
        """Escapar caracteres especiales para LaTeX"""
        if not text:
            return ''
        text = str(text)
        latex_special_chars = {
            '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#', '^': r'\textasciicircum{}',
            '_': r'\_', '{': r'\{', '}': r'\}', '~': r'\textasciitilde{}', '\\': r'\textbackslash{}'
        }
        for char, replacement in latex_special_chars.items():
            text = text.replace(char, replacement)
        return text

    def compile_latex(self, tex_content, output_dir, filename):
        """Compilar LaTeX a PDF"""
        temp_tex_path = None
        temp_image_path = None
        try:
            temp_tex_path = os.path.join(output_dir, f"temp_latex_input_{os.getpid()}_{os.urandom(8).hex()}.tex")
            with open(temp_tex_path, 'w', encoding='utf-8') as temp_file:
                temp_file.write(tex_content)
            self.logger.info(f"Archivo .tex temporal creado en: {temp_tex_path}")

            source_image_path = get_resource_path(os.path.join(self.image_source_subdir, self.image_filename))
            self.logger.info(f"Intentando copiar imagen desde: {source_image_path}")
            temp_image_path = os.path.join(os.path.dirname(temp_tex_path), self.image_filename)

            if not os.path.exists(source_image_path):
                self.logger.error(f"Imagen '{source_image_path}' no encontrada. No se copiará.")
            else:
                shutil.copy(source_image_path, temp_image_path)
                self.logger.info(f"Imagen '{source_image_path}' copiada a '{temp_image_path}'")

            success = self.compile_latex_silent(temp_tex_path, output_dir, filename)
            if success:
                self.logger.success(f"PDF compilado: {os.path.join(output_dir, filename)}")
                return True
            else:
                self.logger.error(f"Error compilando PDF: {filename}")
                return False

        except Exception as e:
            self.logger.error(f"Error en compilación LaTeX: {type(e).__name__}: {str(e)}")
            return False
        finally:
            if temp_tex_path and os.path.exists(temp_tex_path):
                os.unlink(temp_tex_path)
                self.logger.info(f"Archivo temporal eliminado: {temp_tex_path}")  # Cambiado de debug a info
            if temp_image_path and os.path.exists(temp_image_path):
                os.unlink(temp_image_path)
                self.logger.info(f"Imagen temporal eliminada: {temp_image_path}")  # Cambiado de debug a info

    def compile_latex_silent(self, tex_file, output_dir, filename):
        """Compilar LaTeX de forma silenciosa"""
        try:
            if not os.path.exists(tex_file):
                self.logger.error(f"Archivo .tex no encontrado: {tex_file}")
                return False

            cmd = [
                'xelatex',
                '-interaction=nonstopmode',
                '-output-directory', output_dir,
                '-jobname', filename.replace('.pdf', ''),
                tex_file
            ]
            self.logger.info(f"Ejecutando comando: {' '.join(cmd)}")

            # Verificar si xelatex está disponible
            try:
                result = subprocess.run(
                    ['xelatex', '--version'],
                    capture_output=True,
                    text=True,
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                self.logger.info(f"XeLaTeX verificado: {result.stdout.splitlines()[0]}")
            except FileNotFoundError:
                self.logger.error("XeLaTeX no encontrado en el PATH. Asegúrese de que MiKTeX esté instalado.")
                return False
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Error verificando XeLaTeX: {e.stderr}")
                return False

            # Ejecutar xelatex con timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,  # Timeout de 30 segundos
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            self.cleanup_aux_files(output_dir, filename.replace('.pdf', ''))

            if result.returncode != 0:
                self.logger.error(f"XeLaTeX falló con código {result.returncode}.")
                self.logger.error(f"STDOUT: {result.stdout}")
                self.logger.error(f"STDERR: {result.stderr}")
                log_file = os.path.join(output_dir, f"{filename.replace('.pdf', '')}.log")
                if os.path.exists(log_file):
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                        self.logger.error(f"Contenido del log de XeLaTeX:\n{log_content[-2000:]}")
                return False

            return True

        except FileNotFoundError:
            self.logger.error("Error: 'xelatex' no encontrado. Asegúrese de que MiKTeX o TeX Live esté instalado y en su PATH.")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("XeLaTeX se bloqueó o excedió el tiempo de espera (30 segundos).")
            return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error ejecutando XeLaTeX (CalledProcessError): {e}")
            self.logger.error(f"STDOUT: {e.stdout}")
            self.logger.error(f"STDERR: {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado en compilación (compile_latex_silent): {type(e).__name__}: {str(e)}")
            return False

    def cleanup_aux_files(self, output_dir, base_name):
        """Limpiar archivos auxiliares de LaTeX"""
        aux_extensions = ['.aux', '.log', '.fls', '.fdb_latexmk', '.synctex.gz', '.out']
        for ext in aux_extensions:
            aux_file = os.path.join(output_dir, f"{base_name}{ext}")
            if os.path.exists(aux_file):
                try:
                    os.unlink(aux_file)
                    self.logger.debug(f"Archivo auxiliar limpiado: {aux_file}")
                except Exception as e:
                    self.logger.warning(f"No se pudo limpiar el archivo auxiliar {aux_file}: {e}")

    def verify_miktex(self):
        """Verificar que MiKTeX esté instalado y XeLaTeX esté en el PATH"""
        try:
            result = subprocess.run(
                ['xelatex', '--version'],
                capture_output=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                check=True
            )
            self.logger.success(f"XeLaTeX verificado: {result.stdout.splitlines()[0]}")
            return True
        except FileNotFoundError:
            self.logger.error("Error: 'xelatex' no encontrado. Asegúrese de que MiKTeX o TeX Live esté instalado y en su PATH.")
            return False
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error al verificar XeLaTeX (código {e.returncode}): {e.stderr}")
            return False
        except Exception as e:
            self.logger.error(f"Error inesperado al verificar XeLaTeX: {type(e).__name__}: {str(e)}")
            return False