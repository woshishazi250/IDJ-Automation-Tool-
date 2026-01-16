#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
截图工具模块
提供全屏截图、区域截图和窗口截图功能
"""

import sys
import os
import time
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QMessageBox, QSpinBox, QGroupBox
)
from PyQt5.QtCore import Qt, QRect, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen, QBrush, QColor, QCursor, QFont

import win32gui
import win32api
import win32con
import win32ui
from PIL import Image
import numpy as np
import cv2

logger = logging.getLogger(__name__)

class QuickScreenShotTool(QWidget):
    """快速区域截图工具 - 类似Windows Ctrl+Shift+S体验"""
    
    screenshot_taken = pyqtSignal(object)
    
    def __init__(self, parent=None, callback=None):
        super().__init__(parent)
        self.callback = callback
        self.setup_ui()
        self.start_capture()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("快速区域截图")
        # 设置窗口属性，确保能够正确捕获鼠标事件
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setGeometry(QApplication.desktop().availableGeometry())
        self.setWindowOpacity(0.2)
        
        self.screenshot_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()
    
    def start_capture(self):
        """开始截图"""
        self.setCursor(Qt.CrossCursor)
        # 确保窗口能够正确显示和捕获鼠标事件
        logger.debug("调用 show()")
        self.show()
        logger.debug("调用 showFullScreen()")
        self.showFullScreen()
        logger.debug("调用 raise_()")
        self.raise_()
        logger.debug("调用 activateWindow()")
        self.activateWindow()
        # 确保窗口获得焦点
        logger.debug("调用 setFocus()")
        self.setFocus()
        logger.debug(f"窗口可见性: {self.isVisible()}")
        logger.debug(f"窗口状态: {self.windowState()}")
        logger.debug(f"窗口几何信息: {self.geometry()}")
        logger.debug(f"窗口标志: {self.windowFlags()}")
        logger.debug(f"窗口透明度: {self.windowOpacity()}")
        logger.info("快速区域截图工具已启动")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        logger.debug(f"鼠标按下事件: {event.pos()}")
        if event.button() == Qt.LeftButton:
            self.start_point = event.pos()
            self.end_point = self.start_point
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        logger.debug(f"鼠标移动事件: {event.pos()}")
        self.end_point = event.pos()
        self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        logger.debug(f"鼠标释放事件: {event.pos()}")
        if event.button() == Qt.LeftButton:
            # 完成区域选择
            self.screenshot_rect = QRect(self.start_point, self.end_point)
            
            # 调整截图区域坐标
            if self.screenshot_rect.width() < 0:
                self.screenshot_rect.setLeft(self.end_point.x())
                self.screenshot_rect.setRight(self.start_point.x())
            if self.screenshot_rect.height() < 0:
                self.screenshot_rect.setTop(self.end_point.y())
                self.screenshot_rect.setBottom(self.start_point.y())
            
            # 确保截图区域有效
            if self.screenshot_rect.width() > 0 and self.screenshot_rect.height() > 0:
                try:
                    screen = QApplication.primaryScreen()
                    pixmap = screen.grabWindow(
                        QApplication.desktop().winId(),
                        self.screenshot_rect.x(),
                        self.screenshot_rect.y(),
                        self.screenshot_rect.width(),
                        self.screenshot_rect.height()
                    )
                    
                    logger.info("快速区域截图成功")
                    if self.callback:
                        self.callback(pixmap)
                    self.screenshot_taken.emit(pixmap)
                    self.cleanup_and_close()
                except Exception as e:
                    logger.error(f"快速区域截图失败: {e}")
                    QMessageBox.critical(self, "错误", f"截图失败: {str(e)}")
                    self.cleanup_and_close()
            else:
                logger.warning("未选择有效的截图区域")
                self.cleanup_and_close()
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        
        # 绘制半透明背景
        painter.setOpacity(0.2)
        painter.setBrush(QBrush(Qt.black))
        painter.drawRect(self.rect())
        
        # 绘制截图区域（高亮显示）
        painter.setOpacity(1.0)
        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
        painter.setBrush(QBrush(Qt.transparent))
        rect = QRect(self.start_point, self.end_point)
        painter.drawRect(rect)
        
        # 显示坐标信息
        rect_text = f"{rect.width()}x{rect.height()}"
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(self.start_point.x(), self.start_point.y() - 10, rect_text)
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Escape:
            logger.info("快速截图已取消")
            if self.callback:
                self.callback(None)  # 传递 None 表示取消
            self.cleanup_and_close()
    
    def cleanup_and_close(self):
        """清理资源并关闭窗口"""
        logger.debug("开始清理和关闭截图工具")
        try:
            # 确保所有信号连接断开
            self.screenshot_taken.disconnect()
        except Exception:
            pass
        
        # 确保窗口完全隐藏和关闭
        self.hide()
        
        logger.debug("截图工具已成功清理和关闭")


class ScreenShotTool(QWidget):
    """截图工具主类"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.reset_screenshot_state()
    
    def setup_ui(self):
        """设置界面"""
        self.setWindowTitle("截图工具")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setGeometry(QApplication.desktop().availableGeometry())
        
        # 设置半透明背景
        self.setWindowOpacity(0.3)
        
        # 截图区域
        self.screenshot_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()
        
        # 创建主布局
        layout = QVBoxLayout(self)
        
        # 控制面板
        control_group = QGroupBox("截图选项")
        control_layout = QHBoxLayout(control_group)
        
        # 截图类型选择
        self.full_screen_btn = QPushButton("全屏截图")
        self.full_screen_btn.clicked.connect(self.capture_full_screen)
        control_layout.addWidget(self.full_screen_btn)
        
        self.region_btn = QPushButton("区域截图")
        self.region_btn.clicked.connect(self.start_region_capture)
        control_layout.addWidget(self.region_btn)
        
        self.window_btn = QPushButton("窗口截图")
        self.window_btn.clicked.connect(self.capture_active_window)
        control_layout.addWidget(self.window_btn)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.close)
        control_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(control_group)
        
        # 预览标签
        self.preview_label = QLabel("预览区域")
        self.preview_label.setFixedSize(300, 200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ccc;")
        layout.addWidget(self.preview_label)
        
        # 图像编辑按钮
        edit_group = QGroupBox("图像编辑")
        edit_layout = QHBoxLayout(edit_group)
        
        self.crop_btn = QPushButton("裁剪")
        self.crop_btn.clicked.connect(self.start_crop_mode)
        self.crop_btn.setEnabled(False)
        edit_layout.addWidget(self.crop_btn)
        
        self.annotate_btn = QPushButton("标注")
        self.annotate_btn.clicked.connect(self.start_annotate_mode)
        self.annotate_btn.setEnabled(False)
        edit_layout.addWidget(self.annotate_btn)
        
        self.resize_btn = QPushButton("调整大小")
        self.resize_btn.clicked.connect(self.show_resize_dialog)
        self.resize_btn.setEnabled(False)
        edit_layout.addWidget(self.resize_btn)
        
        layout.addWidget(edit_group)
        
        # 操作按钮
        self.save_btn = QPushButton("保存截图")
        self.save_btn.clicked.connect(self.save_screenshot)
        self.save_btn.setEnabled(False)
        layout.addWidget(self.save_btn)
        
        self.copy_btn = QPushButton("复制到剪贴板")
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.copy_btn.setEnabled(False)
        layout.addWidget(self.copy_btn)
    
    def reset_screenshot_state(self):
        """重置截图状态"""
        self.screenshot_rect = QRect()
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.captured_image = None
        self.preview_label.clear()
        self.save_btn.setEnabled(False)
        self.copy_btn.setEnabled(False)
        self.crop_btn.setEnabled(False)
        self.annotate_btn.setEnabled(False)
        self.resize_btn.setEnabled(False)
        self.crop_mode = False
        self.annotate_mode = False
        self.crop_rect = QRect()
    
    def start_crop_mode(self):
        """开始裁剪模式"""
        if self.captured_image:
            self.crop_mode = True
            self.annotate_mode = False
            self.setWindowOpacity(0.1)
            self.setCursor(Qt.CrossCursor)
            self.crop_rect = QRect()
            logger.info("裁剪模式已启动")
            QMessageBox.information(self, "提示", "请在屏幕上选择裁剪区域")
    
    def start_annotate_mode(self):
        """开始标注模式"""
        if self.captured_image:
            self.annotate_mode = True
            self.crop_mode = False
            self.setWindowOpacity(0.1)
            self.setCursor(Qt.CrossCursor)
            logger.info("标注模式已启动")
            QMessageBox.information(self, "提示", "请在屏幕上选择标注区域")
    
    def show_resize_dialog(self):
        """显示调整大小对话框"""
        if self.captured_image:
            from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout
            
            dialog = QDialog(self)
            dialog.setWindowTitle("调整大小")
            dialog.setModal(True)
            
            layout = QVBoxLayout(dialog)
            
            # 宽度和高度输入
            size_layout = QHBoxLayout()
            
            width_label = QLabel("宽度:")
            size_layout.addWidget(width_label)
            self.width_edit = QLineEdit(str(self.captured_image.width()))
            size_layout.addWidget(self.width_edit)
            
            height_label = QLabel("高度:")
            size_layout.addWidget(height_label)
            self.height_edit = QLineEdit(str(self.captured_image.height()))
            size_layout.addWidget(self.height_edit)
            
            layout.addLayout(size_layout)
            
            # 按钮
            button_layout = QHBoxLayout()
            
            ok_btn = QPushButton("确定")
            ok_btn.clicked.connect(lambda: self.resize_image(dialog))
            button_layout.addWidget(ok_btn)
            
            cancel_btn = QPushButton("取消")
            cancel_btn.clicked.connect(dialog.close)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            dialog.exec_()
    
    def resize_image(self, dialog):
        """调整图像大小"""
        try:
            width = int(self.width_edit.text())
            height = int(self.height_edit.text())
            
            if width > 0 and height > 0:
                resized_pixmap = self.captured_image.scaled(
                    width, height, Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.captured_image = resized_pixmap
                self.display_preview(resized_pixmap)
                logger.info(f"图像调整大小成功: {width}x{height}")
                QMessageBox.information(self, "成功", "图像调整大小成功")
                dialog.close()
            else:
                QMessageBox.warning(self, "警告", "宽度和高度必须大于0")
        except ValueError:
            QMessageBox.warning(self, "警告", "请输入有效的数字")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self.crop_mode:
            self.start_point = event.pos()
            self.end_point = self.start_point
        elif self.annotate_mode:
            self.start_point = event.pos()
            self.end_point = self.start_point
        elif hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            self.start_point = event.pos()
            self.end_point = self.start_point
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.crop_mode:
            self.end_point = event.pos()
            self.update()
        elif self.annotate_mode:
            self.end_point = event.pos()
            self.update()
        elif hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            self.end_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.crop_mode:
            # 完成裁剪区域选择
            self.crop_rect = QRect(self.start_point, self.end_point)
            
            # 调整裁剪区域坐标
            if self.crop_rect.width() < 0:
                self.crop_rect.setLeft(self.end_point.x())
                self.crop_rect.setRight(self.start_point.x())
            if self.crop_rect.height() < 0:
                self.crop_rect.setTop(self.end_point.y())
                self.crop_rect.setBottom(self.start_point.y())
            
            # 裁剪图像
            try:
                cropped_pixmap = self.captured_image.copy(self.crop_rect)
                self.captured_image = cropped_pixmap
                self.display_preview(cropped_pixmap)
                self.crop_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
                logger.info("图像裁剪成功")
                QMessageBox.information(self, "成功", "图像裁剪成功")
            except Exception as e:
                logger.error(f"图像裁剪失败: {e}")
                QMessageBox.critical(self, "错误", f"图像裁剪失败: {str(e)}")
                self.crop_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
        elif self.annotate_mode:
            # 标注功能（简单实现：在截图上画矩形）
            try:
                painter = QPainter(self.captured_image)
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.setBrush(QBrush(QColor(255, 0, 0, 30)))
                rect = QRect(self.start_point, self.end_point)
                painter.drawRect(rect)
                painter.end()
                
                self.display_preview(self.captured_image)
                self.annotate_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
                logger.info("图像标注成功")
                QMessageBox.information(self, "成功", "图像标注成功")
            except Exception as e:
                logger.error(f"图像标注失败: {e}")
                QMessageBox.critical(self, "错误", f"图像标注失败: {str(e)}")
                self.annotate_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
        elif hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            # 完成区域选择
            self.screenshot_rect = QRect(self.start_point, self.end_point)
            
            # 调整截图区域坐标
            if self.screenshot_rect.width() < 0:
                self.screenshot_rect.setLeft(self.end_point.x())
                self.screenshot_rect.setRight(self.start_point.x())
            if self.screenshot_rect.height() < 0:
                self.screenshot_rect.setTop(self.end_point.y())
                self.screenshot_rect.setBottom(self.start_point.y())
            
            # 截图区域
            try:
                screen = QApplication.primaryScreen()
                self.captured_image = screen.grabWindow(
                    QApplication.desktop().winId(),
                    self.screenshot_rect.x(),
                    self.screenshot_rect.y(),
                    self.screenshot_rect.width(),
                    self.screenshot_rect.height()
                )
                
                self.display_preview(self.captured_image)
                self.region_capture_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
                
                logger.info("区域截图成功")
                
                # 调用回调函数
                if hasattr(self, 'screenshot_callback') and self.screenshot_callback:
                    self.screenshot_callback(self.captured_image)
                    self.close()
                else:
                    QMessageBox.information(self, "成功", "区域截图完成！")
                
            except Exception as e:
                logger.error(f"区域截图失败: {e}")
                QMessageBox.critical(self, "错误", f"区域截图失败: {str(e)}")
                self.region_capture_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        
        if self.crop_mode:
            # 绘制裁剪区域边框
            painter.setPen(QPen(Qt.green, 2, Qt.SolidLine))
            painter.setBrush(QBrush(QColor(0, 255, 0, 30)))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
        elif self.annotate_mode:
            # 绘制标注区域边框
            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
            painter.setBrush(QBrush(QColor(0, 0, 255, 30)))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
        elif hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            # 绘制截图区域边框
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.setBrush(QBrush(QColor(255, 0, 0, 30)))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
    
    def capture_full_screen(self):
        """全屏截图"""
        try:
            # 获取全屏尺寸
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(QApplication.desktop().winId())
            
            self.captured_image = pixmap
            self.display_preview(pixmap)
            
            logger.info("全屏截图成功")
            QMessageBox.information(self, "成功", "全屏截图完成！")
            
        except Exception as e:
            logger.error(f"全屏截图失败: {e}")
            QMessageBox.critical(self, "错误", f"全屏截图失败: {str(e)}")
    
    def start_region_capture(self):
        """开始区域截图"""
        self.reset_screenshot_state()
        self.setWindowOpacity(0.1)
        self.setCursor(Qt.CrossCursor)
        self.region_capture_mode = True
    
    def capture_active_window(self):
        """截图当前激活窗口"""
        try:
            # 获取当前激活窗口
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                # 获取窗口位置和尺寸
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top
                
                # 截图窗口
                screen = QApplication.primaryScreen()
                pixmap = screen.grabWindow(hwnd, 0, 0, width, height)
                
                self.captured_image = pixmap
                self.display_preview(pixmap)
                
                logger.info("窗口截图成功")
                QMessageBox.information(self, "成功", "窗口截图完成！")
            else:
                QMessageBox.warning(self, "警告", "未找到激活窗口")
                
        except Exception as e:
            logger.error(f"窗口截图失败: {e}")
            QMessageBox.critical(self, "错误", f"窗口截图失败: {str(e)}")
    
    def display_preview(self, pixmap):
        """显示截图预览"""
        # 缩放图像以适应预览标签
        scaled_pixmap = pixmap.scaled(
            self.preview_label.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.preview_label.setPixmap(scaled_pixmap)
        self.save_btn.setEnabled(True)
        self.copy_btn.setEnabled(True)
        self.crop_btn.setEnabled(True)
        self.annotate_btn.setEnabled(True)
        self.resize_btn.setEnabled(True)
    
    def save_screenshot(self):
        """保存截图"""
        if self.captured_image is None:
            QMessageBox.warning(self, "警告", "没有可保存的截图")
            return
        
        # 打开保存对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "保存截图",
            "",
            "PNG图片 (*.png);;JPG图片 (*.jpg);;BMP图片 (*.bmp)"
        )
        
        if file_path:
            try:
                self.captured_image.save(file_path)
                logger.info(f"截图保存成功: {file_path}")
                QMessageBox.information(self, "成功", "截图保存成功！")
            except Exception as e:
                logger.error(f"截图保存失败: {e}")
                QMessageBox.critical(self, "错误", f"保存失败: {str(e)}")
    
    def copy_to_clipboard(self):
        """复制截图到剪贴板"""
        if self.captured_image is None:
            QMessageBox.warning(self, "警告", "没有可复制的截图")
            return
        
        try:
            clipboard = QApplication.clipboard()
            clipboard.setPixmap(self.captured_image)
            logger.info("截图已复制到剪贴板")
            QMessageBox.information(self, "成功", "截图已复制到剪贴板！")
        except Exception as e:
            logger.error(f"复制失败: {e}")
            QMessageBox.critical(self, "错误", f"复制失败: {str(e)}")
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if self.crop_mode:
            self.start_point = event.pos()
            self.end_point = self.start_point
        elif self.annotate_mode:
            self.start_point = event.pos()
            self.end_point = self.start_point
        elif hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            self.start_point = event.pos()
            self.end_point = self.start_point
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.crop_mode:
            self.end_point = event.pos()
            self.update()
        elif self.annotate_mode:
            self.end_point = event.pos()
            self.update()
        elif hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            self.end_point = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.crop_mode:
            # 完成裁剪区域选择
            self.crop_rect = QRect(self.start_point, self.end_point)
            
            # 调整裁剪区域坐标
            if self.crop_rect.width() < 0:
                self.crop_rect.setLeft(self.end_point.x())
                self.crop_rect.setRight(self.start_point.x())
            if self.crop_rect.height() < 0:
                self.crop_rect.setTop(self.end_point.y())
                self.crop_rect.setBottom(self.start_point.y())
            
            # 裁剪图像
            try:
                cropped_pixmap = self.captured_image.copy(self.crop_rect)
                self.captured_image = cropped_pixmap
                self.display_preview(cropped_pixmap)
                self.crop_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
                logger.info("图像裁剪成功")
                QMessageBox.information(self, "成功", "图像裁剪成功")
            except Exception as e:
                logger.error(f"图像裁剪失败: {e}")
                QMessageBox.critical(self, "错误", f"图像裁剪失败: {str(e)}")
                self.crop_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
        elif self.annotate_mode:
            # 标注功能（简单实现：在截图上画矩形）
            try:
                painter = QPainter(self.captured_image)
                painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
                painter.setBrush(QBrush(QColor(255, 0, 0, 30)))
                rect = QRect(self.start_point, self.end_point)
                painter.drawRect(rect)
                painter.end()
                
                self.display_preview(self.captured_image)
                self.annotate_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
                logger.info("图像标注成功")
                QMessageBox.information(self, "成功", "图像标注成功")
            except Exception as e:
                logger.error(f"图像标注失败: {e}")
                QMessageBox.critical(self, "错误", f"图像标注失败: {str(e)}")
                self.annotate_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
        elif hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            # 完成区域选择
            self.screenshot_rect = QRect(self.start_point, self.end_point)
            
            # 调整截图区域坐标
            if self.screenshot_rect.width() < 0:
                self.screenshot_rect.setLeft(self.end_point.x())
                self.screenshot_rect.setRight(self.start_point.x())
            if self.screenshot_rect.height() < 0:
                self.screenshot_rect.setTop(self.end_point.y())
                self.screenshot_rect.setBottom(self.start_point.y())
            
            # 截图区域
            try:
                screen = QApplication.primaryScreen()
                self.captured_image = screen.grabWindow(
                    QApplication.desktop().winId(),
                    self.screenshot_rect.x(),
                    self.screenshot_rect.y(),
                    self.screenshot_rect.width(),
                    self.screenshot_rect.height()
                )
                
                self.display_preview(self.captured_image)
                self.region_capture_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
                
                logger.info("区域截图成功")
                
                # 调用回调函数
                if hasattr(self, 'screenshot_callback') and self.screenshot_callback:
                    self.screenshot_callback(self.captured_image)
                    self.close()
                else:
                    QMessageBox.information(self, "成功", "区域截图完成！")
                
            except Exception as e:
                logger.error(f"区域截图失败: {e}")
                QMessageBox.critical(self, "错误", f"区域截图失败: {str(e)}")
                self.region_capture_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
    
    def paintEvent(self, event):
        """绘制事件"""
        painter = QPainter(self)
        
        if hasattr(self, 'region_capture_mode') and self.region_capture_mode:
            # 绘制截图区域边框
            painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))
            painter.setBrush(QBrush(QColor(255, 0, 0, 30)))
            rect = QRect(self.start_point, self.end_point)
            painter.drawRect(rect)
    
    def keyPressEvent(self, event):
        """键盘事件"""
        if event.key() == Qt.Key_Escape:
            if hasattr(self, 'region_capture_mode') and self.region_capture_mode:
                self.region_capture_mode = False
                self.setWindowOpacity(0.3)
                self.setCursor(Qt.ArrowCursor)
                self.update()
            else:
                self.close()

class ScreenshotManager:
    """截图管理器"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.screenshot_tool = None
    
    def create_screenshot_tool(self):
        """创建截图工具"""
        self.screenshot_tool = ScreenShotTool(self.parent)
        return self.screenshot_tool
    
    def capture_region(self, callback=None):
        """捕获区域截图 - 使用快速截图工具"""
        tool = QuickScreenShotTool(self.parent, callback)
        return tool
    
    def capture_window(self, hwnd, save_path=None):
        """捕获指定窗口截图"""
        try:
            # 获取窗口位置和尺寸
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top
            
            # 使用PyQt5截图
            screen = QApplication.primaryScreen()
            pixmap = screen.grabWindow(hwnd, 0, 0, width, height)
            
            if save_path:
                pixmap.save(save_path)
            
            return pixmap
            
        except Exception as e:
            logger.error(f"窗口截图失败: {e}")
            return None
    
    def capture_screen(self, rect=None, save_path=None):
        """捕获屏幕截图"""
        try:
            screen = QApplication.primaryScreen()
            
            if rect:
                pixmap = screen.grabWindow(
                    QApplication.desktop().winId(),
                    rect.x(),
                    rect.y(),
                    rect.width(),
                    rect.height()
                )
            else:
                pixmap = screen.grabWindow(QApplication.desktop().winId())
            
            if save_path:
                pixmap.save(save_path)
            
            return pixmap
            
        except Exception as e:
            logger.error(f"屏幕截图失败: {e}")
            return None
