```python
# generador-titulos-vt.spec
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Análisis del script principal
a = Analysis(
    ['main_v2.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('src/*', 'src'),
        ('components/*', 'components'),
        ('core/*', 'core'),
        ('utils/*', 'utils'),
        ('assets/*', 'assets')
    ],
    hiddenimports=[
        'ttkthemes',
        'PIL',
        'pandas',
        'openpyxl'  # Necesario para pandas.read_excel
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False
)
pyz = PYZ(a.pure, a.zipped_data)

# Crear ejecutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='generador-titulos-utn',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Suprimir consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
    # icon='assets\\icon.ico'  # Descomentar si se agrega un ícono
)
```