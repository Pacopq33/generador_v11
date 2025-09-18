# Generador de Certificados Académicos

Aplicación de escritorio desarrollada en Python que genera certificados en PDF a partir de datos contenidos en un archivo Excel. El PDF se compone íntegramente con [ReportLab](https://www.reportlab.com/), por lo que ya no es necesario instalar MiKTeX ni mantener plantillas LaTeX externas.

## 🚀 Características

- **Interfaz gráfica moderna** basada en Tk/ttkthemes.
- **Renderizado PDF nativo** con ReportLab: sin procesos externos ni compilaciones LaTeX.
- **Procesamiento por lotes** con seguimiento en tiempo real desde la UI.
- **Validaciones de datos y del sistema** previas a la generación.
- **Logging unificado** en consola, archivo y panel dentro de la aplicación.

## 📋 Requisitos del Sistema

### Software necesario
- Windows 10 o superior.
- Python 3.9 o superior.

### Dependencias Python
Instale todas las dependencias con:

```bash
pip install -r requirements.txt
```

El archivo incluye:

- `pandas`, `openpyxl` para trabajar con Excel.
- `reportlab` para el renderizado del certificado.
- `ttkthemes` y `Pillow` para la interfaz.
- `pyinstaller` para generar ejecutables (opcional en desarrollo).

### Recursos opcionales
En `assets/fonts/` puede colocar versiones TrueType de Garamond y Arial Narrow si desea replicar la estética institucional. El motor utiliza fuentes estándar (Times/Helvetica) cuando no están disponibles.

## 🛠️ Instalación y uso

1. **Clonar o copiar** el repositorio en su equipo.
2. **Instalar dependencias** con `pip install -r requirements.txt` dentro del entorno deseado.
3. **Ejecutar la aplicación**:
   ```bash
   python main_v2.py
   ```
4. **Flujo en la interfaz**:
   - Cargue el Excel desde el botón `📄 Cargar Excel`.
   - Seleccione la carpeta de salida (`📁 Carpeta Salida`).
   - Valide los datos si lo desea (`Validar Datos`).
   - Seleccione los registros y pulse `GENERAR CERTIFICADOS`.

## 📊 Formato del archivo Excel

El Excel debe incluir al menos las siguientes columnas:

| Columna            | Descripción                        | Ejemplo               |
|--------------------|------------------------------------|-----------------------|
| `nombre_apellido`  | Nombre completo de la persona      | "Juan Pérez"         |
| `dni`              | Documento con puntos               | "22.222.222"         |
| `carrera`          | Curso o carrera aprobada           | "Tecnicatura ..."    |
| `dispo`            | Número de disposición              | "123/2024"           |
| `dia`              | Día de emisión                     | "15"                 |
| `mes`              | Mes de emisión (texto)             | "marzo"              |

Las columnas pueden contener otros campos adicionales; se ignoran durante la generación.

## 🎨 Personalización del certificado

Todo el layout se define en `src/core/reportlab_renderer.py`. Allí puede ajustar:

- Márgenes y posiciones del contenido.
- Tipografías utilizadas.
- Textos estáticos (por ejemplo, leyendas y firmas).
- Lógica para tomar campos adicionales del Excel (por ejemplo, un año configurable).

Al modificar el archivo no es necesario regenerar plantillas; basta con reiniciar la aplicación.

## 🔧 Empaquetado

Para crear un ejecutable de Windows con PyInstaller y empaquetarlo con NSIS:

1. Ejecute PyInstaller con el spec incluido (`generador-titulos-utn.spec`).
2. Ejecute el script NSIS `generador-titulos-utn.nsi` para construir el instalador. El script ya no solicita MiKTeX.

## 📁 Estructura relevante

```
.
├── main_v2.py                  # Punto de entrada de la aplicación
├── assets/                     # Logos, fuentes opcionales y prototipos
├── src/
│   ├── core/
│   │   ├── excel_handlerv2.py  # Lectura y validación de Excel
│   │   ├── pdf_generatorv2.py  # Orquestador de generación PDF
│   │   └── reportlab_renderer.py # Renderizado del certificado
│   ├── gui/                    # Componentes de la interfaz
│   └── utils/                  # Logger, validaciones y utilidades
└── requirements.txt
```

## 🐛 Solución de problemas

- **"ReportLab no está disponible"**: ejecute `pip install -r requirements.txt` e intente nuevamente.
- **"Logo del certificado no encontrado"**: verifique que `assets/logomejor.png` exista y sea accesible.
- **"Sin permisos de escritura"**: ejecute la aplicación con permisos elevados o seleccione otra carpeta de destino.
- **"Columnas faltantes"**: revise los encabezados del Excel según la tabla anterior.

## 📄 Prototipo de certificado

Se incluye `assets/certificate_prototype.pdf` como referencia del diseño generado con ReportLab.

## 📞 Soporte

En caso de incidentes:
1. Revise los mensajes de la consola en la aplicación.
2. Consulte el archivo `logs/app.log` para más detalles.
3. Valide el formato del Excel con el botón "Validar Datos" antes de generar.

---

**Versión**: 1.1  
**Última actualización**: 2025
