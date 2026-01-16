#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包脚本 - 将IDJ脚本自动化软件打包为exe
"""

import os
import subprocess
import sys

def build():
    """执行打包"""
    # PyInstaller 命令
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--name=IDJ脚本自动化',
        '--windowed',  # 无控制台窗口
        '--onefile',   # 打包成单个exe
        '--icon=favicon.ico',
        '--add-data=src;src',  # 包含src目录
        '--add-data=favicon.ico;.',  # 包含图标
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        '--hidden-import=PIL',
        '--hidden-import=pyautogui',
        '--hidden-import=win32gui',
        '--hidden-import=win32con',
        '--hidden-import=win32api',
        '--hidden-import=psutil',
        '--hidden-import=pynput',
        '--hidden-import=pynput.mouse',
        '--hidden-import=pynput.keyboard',
        '--collect-all=pynput',
        '--noconfirm',
        'main.py'
    ]
    
    print("开始打包...")
    print(f"命令: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))
    
    if result.returncode == 0:
        print("\n打包成功！")
        print("exe文件位于: dist/IDJ脚本自动化.exe")
    else:
        print("\n打包失败！")
        sys.exit(1)

if __name__ == '__main__':
    build()
