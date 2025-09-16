# Generador de Certificados Académicos

Aplicación de escritorio desarrollada en Python para generar certificados académicos en PDF a partir de datos de Excel utilizando plantillas LaTeX.

## 🚀 Características

- **Interfaz Gráfica Moderna**: Desarrollada con CustomTkinter
- **Procesamiento por Lotes**: Genera múltiples certificados automáticamente
- **Validación Robusta**: Verifica datos y formato antes de procesar
- **Logging Visual**: Consola de logs con colores por tipo de mensaje
- **Progreso en Tiempo Real**: Barra de progreso durante la generación
- **Limpieza Automática**: Elimina archivos temporales automáticamente

## 📋 Requisitos del Sistema

### Software Requerido
- **Windows 10+**
- **Python 3.8+**
- **MiKTeX** (distribución LaTeX para Windows)

### Dependencias Python
\`\`\`
customtkinter==5.2.0
pandas==2.0.3
openpyxl==3.1.2
Pillow==10.0.0
\`\`\`

## 🛠️ Instalación

### 1. Instalar MiKTeX
1. Descargar desde [miktex.org](https://miktex.org/download)
2. Ejecutar el instalador
3. Verificar instalación ejecutando \`pdflatex --version\` en CMD

### 2. Instalar Dependencias Python
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Ejecutar Aplicación
\`\`\`bash
python main.py
\`\`\`

## 📊 Formato de Datos Excel

El archivo Excel debe contener las siguientes columnas **exactas**:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| \`nombre_apellido\` | Nombre completo | "Juan Pérez" |
| \`dni\` | DNI con puntos | "22.222.222" |
| \`carrera\` | Nombre de la carrera | "Ingeniería Informática" |
| \`dispo\` | Número de disposición | "123/2024" |
| \`dia\` | Día de emisión | "15" |
| \`mes\` | Mes de emisión | "marzo" |

### ⚠️ Importante
- Los nombres de columnas deben ser **exactos** (minúsculas, con guiones bajos)
- El DNI debe mantener el formato con puntos
- No debe haber filas completamente vacías

## 🎯 Uso de la Aplicación

### 1. Cargar Datos
1. Hacer clic en **"📄 Cargar Excel"**
2. Seleccionar archivo Excel con el formato correcto
3. Verificar que los datos aparezcan en la tabla

### 2. Validar Datos
1. Hacer clic en **"Validar Datos"** para verificar formato
2. Revisar mensajes en la consola de logs
3. Corregir errores si es necesario

### 3. Seleccionar Salida
1. Hacer clic en **"📁 Carpeta Salida"**
2. Elegir carpeta donde guardar los PDFs

### 4. Generar Certificados
1. Seleccionar filas a procesar (checkboxes en tabla)
2. Hacer clic en **"GENERAR CERTIFICADOS"**
3. Monitorear progreso en tiempo real
4. Revisar logs para verificar éxito

## 🔧 Empaquetado

Para crear un ejecutable independiente:

\`\`\`bash
# Ejecutar script de empaquetado
build.bat
\`\`\`

El ejecutable se generará en la carpeta \`dist/\`.

## 📁 Estructura del Proyecto

\`\`\`
certificados_app/
├── main.py                    # Punto de entrada
├── src/
│   ├── gui/                   # Interfaz gráfica
│   │   ├── main_window.py     # Ventana principal
│   │   ├── components/        # Componentes UI
│   │   └── styles.py          # Estilos y colores
│   ├── core/                  # Lógica de negocio
│   │   ├── excel_handler.py   # Manejo de Excel
│   │   ├── latex_processor.py # Procesamiento LaTeX
│   │   └── pdf_generator.py   # Generación PDF
│   └── utils/                 # Utilidades
│       ├── validation.py      # Validaciones
│       └── logger.py          # Sistema de logging
├── assets/
│   ├── logoapp.png           # Logo de la aplicación
│   └── plantilla.tex         # Plantilla LaTeX
├── requirements.txt          # Dependencias
├── build.bat                # Script de empaquetado
└── README.md                # Documentación
\`\`\`

## 🎨 Personalización

### Modificar Plantilla
Editar \`assets/plantilla.tex\` para cambiar:
- Diseño del certificado
- Colores institucionales
- Logo y encabezados
- Formato de texto

### Cambiar Colores de Interfaz
Modificar \`src/gui/styles.py\`:
\`\`\`python
COLORS = {
    'PRIMARY': '#1f538d',
    'SUCCESS': '#4CAF50',
    'ERROR': '#F44336',
    # ...
}
\`\`\`

## 🐛 Solución de Problemas

### Error: "MiKTeX no encontrado"
- Verificar que MiKTeX esté instalado
- Agregar MiKTeX al PATH del sistema
- Reiniciar la aplicación

### Error: "Columnas faltantes"
- Verificar nombres exactos de columnas en Excel
- Usar formato: \`nombre_apellido\`, \`dni\`, etc.
- No usar espacios ni mayúsculas

### Error: "Sin permisos de escritura"
- Ejecutar como administrador
- Cambiar carpeta de salida
- Verificar permisos de la carpeta

### PDFs no se generan
- Verificar plantilla LaTeX
- Revisar caracteres especiales en datos
- Consultar logs para errores específicos

## 📞 Soporte

Para reportar problemas o solicitar características:
1. Revisar logs en la consola de la aplicación
2. Verificar formato de datos Excel
3. Consultar esta documentación

## 📄 Licencia

Este proyecto es de uso interno institucional.

---

**Versión**: 1.0  
**Última actualización**: 2024
