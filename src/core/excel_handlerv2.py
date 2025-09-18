import pandas as pd
import re
from ..utils.loggerv2 import AppLogger  # Cambiado a AppLogger

class ExcelHandler:
    """Manejador para archivos Excel"""
    
    COLUMNAS_REQUERIDAS = [
        'nombre_apellido',
        'dni',
        'carrera',
        'dispo',
        'dia',
        'mes'
    ]
    
    def __init__(self):
        self.logger = AppLogger()
        
    def load_excel(self, file_path):
        """Cargar archivo Excel y validar estructura"""
        try:
            df = pd.read_excel(file_path)
            self.logger.info(f"Excel leído: {len(df)} filas")
            
            missing_columns = self.validate_columns(df.columns.tolist())
            if missing_columns:
                error_msg = f"Columnas faltantes: {', '.join(missing_columns)}"
                self.logger.error(error_msg)
                raise ValueError(error_msg)
                
            df = self.clean_data(df)
            
            self.logger.success("Excel cargado y validado correctamente")
            return df
            
        except Exception as e:
            self.logger.error(f"Error cargando Excel: {e}")
            raise
            
    def validate_columns(self, columns):
        """Validar que existan todas las columnas requeridas"""
        columns_lower = [col.lower().strip() for col in columns]
        missing = []
        
        for required_col in self.COLUMNAS_REQUERIDAS:
            if required_col.lower() not in columns_lower:
                missing.append(required_col)
                
        return missing
        
    def clean_data(self, df):
        """Limpiar y normalizar datos"""
        df.columns = [col.lower().strip() for col in df.columns]
        
        df = df.dropna(how='all')
        
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.strip()
                
        if 'dni' in df.columns:
            df['dni'] = df['dni'].apply(self.normalize_dni)
            
        return df
        
    def normalize_dni(self, dni):
        """Normalizar formato de DNI manteniendo puntos"""
        if pd.isna(dni):
            return ''
            
        dni_str = str(dni).strip()
        
        if '.' in dni_str:
            return dni_str
            
        if dni_str.isdigit() and len(dni_str) >= 7:
            if len(dni_str) == 8:
                return f"{dni_str[:2]}.{dni_str[2:5]}.{dni_str[5:]}"
            elif len(dni_str) == 7:
                return f"{dni_str[:1]}.{dni_str[1:4]}.{dni_str[4:]}"
                
        return dni_str
        
    def validate_data(self, df):
        """Validar datos del DataFrame"""
        errors = []
        
        for index, row in df.iterrows():
            row_errors = self.validate_row(row, index + 1)
            errors.extend(row_errors)
            
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
        
    def validate_row(self, row, row_number):
        """Validar una fila individual"""
        errors = []
        
        for col in self.COLUMNAS_REQUERIDAS:
            if col not in row or pd.isna(row[col]) or str(row[col]).strip() == '':
                errors.append(f"Fila {row_number}: Campo '{col}' está vacío")
                
        if 'dni' in row and not pd.isna(row['dni']):
            dni = str(row['dni']).strip()
            if not self.validate_dni_format(dni):
                errors.append(f"Fila {row_number}: DNI '{dni}' tiene formato incorrecto")
                
        return errors
        
    def validate_dni_format(self, dni):
        """Validar formato de DNI"""
        pattern = r'^\d{1,2}\.\d{3}\.\d{3}$'
        return bool(re.match(pattern, dni))

    # La validación de caracteres especiales ya no es necesaria con ReportLab.
