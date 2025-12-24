# -*- mode: python ; coding: utf-8 -*-
"""
Booker - PyInstaller Spec File
Builds the Booker application into a standalone Windows executable.
"""

import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all data files from customtkinter (themes, etc.)
ctk_datas = collect_data_files('customtkinter')

# Hidden imports for all dependencies
hidden_imports = [
    # CustomTkinter
    *collect_submodules('customtkinter'),
    
    # Pillow
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageTk',
    
    # EbookLib
    'ebooklib',
    'ebooklib.epub',
    
    # PyMuPDF
    'fitz',
    
    # BeautifulSoup
    'bs4',
    'lxml',
    'html.parser',
    
    # Standard library modules that might be missed
    'sqlite3',
    'threading',
    'queue',
    'io',
    're',
    'json',
    'base64',
    'hashlib',
    'urllib',
    'html',
    'xml',
    'xml.etree.ElementTree',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=ctk_datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Booker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico' if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='Booker',
)
