# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec文件 - IDJ脚本自动化软件
使用方法: pyinstaller IDJ.spec
"""

import sys
import os

block_cipher = None

CURRENT_DIR = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['main.py'],
    pathex=[CURRENT_DIR],
    binaries=[],
    datas=[
        ('src', 'src'),
        ('favicon.ico', '.'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.sip',
        'cv2',
        'numpy',
        'numpy.core._methods',
        'numpy.lib.format',
        'PIL',
        'PIL.Image',
        'PIL._imaging',
        'pyautogui',
        'pyautogui._pyautogui_win',
        'win32gui',
        'win32con',
        'win32api',
        'win32process',
        'win32ui',
        'win32com',
        'win32com.client',
        'pythoncom',
        'pywintypes',
        'psutil',
        'json',
        'logging',
        'time',
        're',
        'threading',
        'pynput',
        'pynput.mouse',
        'pynput.keyboard',
        'pynput.mouse._win32',
        'pynput.keyboard._win32',
        'scipy',
        'scipy.ndimage',
        'pytesseract',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'torch',
        'torchvision',
        'yolov5',
        'matplotlib',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='IDJ脚本自动化',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(CURRENT_DIR, 'favicon.ico'),
    version=os.path.join(CURRENT_DIR, 'version_info.txt'),
)
