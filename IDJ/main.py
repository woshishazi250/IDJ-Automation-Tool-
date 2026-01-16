#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IDJ - 脚本自动化软件
功能完整的脚本自动化软件，支持积木模式和代码模式
"""

import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# 添加项目路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.append(src_dir)

from ui.main_window import MainWindow

# 设置日志 - 只输出到控制台，不写入文件
logging.basicConfig(
    level=logging.WARNING,  # 只记录警告和错误
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置全局字体，确保支持中文显示
    font = QFont()
    try:
        # 优先使用微软雅黑
        font.setFamily("Microsoft YaHei")
    except:
        try:
            # 尝试宋体
            font.setFamily("SimSun")
        except:
            # 最后使用系统默认字体
            pass
    app.setFont(font)
    
    # 设置应用程序信息
    app.setApplicationName("IDJ 脚本自动化软件")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("IDJ")
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    logger.info("IDJ 脚本自动化软件启动成功")
    
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
