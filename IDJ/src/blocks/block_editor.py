#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
                                        ?                                                                                                                            ?"""

import sys
import os
import json
import logging
import time
import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QListWidget, QTreeWidget, QTreeWidgetItem, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QScrollArea, QTabWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem, QDialog, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import QFont, QColor, QPen, QBrush, QCursor

logger = logging.getLogger(__name__)

class BlockItem(QGraphicsRectItem):
    """                                    """
    
    def __init__(self, block_name, block_type, properties=None, parent=None):
        super().__init__(parent)
        self.block_name = block_name
        self.block_type = block_type
        self.properties = properties or {}
        
        self.setup_block_visual()
        self.setFlags(QGraphicsItem.ItemIsSelectable | 
                     QGraphicsItem.ItemIsMovable |
                     QGraphicsItem.ItemSendsGeometryChanges)
        
        self.is_connected = False
        self.is_dragging = False  # 添加拖拽状态属性
        self.connected_blocks = []
        self.connected_to = None  #                                         ?
        self.connected_from = None  #                                         ?    
    def paint(self, painter, option, widget):
        """绘制简单的圆角矩形积木"""
        from PyQt5.QtGui import QLinearGradient
        
        rect = self.rect()
        block_color = self.brush().color()
        
        # 创建柔和的渐变背景
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, block_color.lighter(108))
        gradient.setColorAt(1, block_color.darker(105))
        
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(block_color.darker(120), 1.5))
        painter.drawRoundedRect(rect, 8, 8)
        
        # 绘制连接小白条（顶部凹槽和底部凸起）
        self.draw_connection_tabs(painter, rect)
        
        # 绘制文字和参数框
        self.draw_parameter_boxes(painter, rect, block_color)
    
    def draw_connection_tabs(self, painter, rect):
        """绘制连接小白条（左侧，与积木形状凹槽对齐）"""
        from PyQt5.QtGui import QPainterPath
        
        tab_width = 30
        tab_height = 5
        # 连接点在左侧，与积木形状中的凹槽位置对齐
        notch_offset = 15
        tab_x = notch_offset
        
        # 检查连接状态
        has_top_connection = hasattr(self, 'connected_to') and self.connected_to is not None
        has_bottom_connection = hasattr(self, 'connected_from') and self.connected_from is not None
        
        # 顶部凹槽（除了开始积木）
        if self.block_type != "start":
            if has_top_connection:
                # 已连接 - 绿色
                painter.setBrush(QBrush(QColor(100, 220, 100, 220)))
                painter.setPen(QPen(QColor(60, 180, 60), 1))
            else:
                # 未连接 - 白色
                painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
                painter.setPen(QPen(QColor(200, 200, 200), 1))
            top_tab = QRectF(tab_x, 0, tab_width, tab_height)
            painter.drawRoundedRect(top_tab, 2, 2)
        
        # 底部凸起
        if has_bottom_connection:
            # 已连接 - 绿色
            painter.setBrush(QBrush(QColor(100, 220, 100, 220)))
            painter.setPen(QPen(QColor(60, 180, 60), 1))
        else:
            # 未连接 - 白色
            painter.setBrush(QBrush(QColor(255, 255, 255, 180)))
            painter.setPen(QPen(QColor(200, 200, 200), 1))
        bottom_tab = QRectF(tab_x, rect.height() - 1, tab_width, tab_height)
        painter.drawRoundedRect(bottom_tab, 2, 2)
    
    def draw_parameter_boxes(self, painter, rect, block_color):
        """绘制内嵌的参数框"""
        from PyQt5.QtGui import QPainterPath
        
        # 根据积木类型决定是否绘制参数框
        param_value = None
        param_label_before = ""
        param_label_after = ""
        
        if self.block_type == "loop":
            loop_type = self.properties.get('loop_type', 'count')
            if loop_type == 'count':
                param_value = str(self.properties.get('count', 10))
                param_label_before = "重复"
                param_label_after = "次"
            elif loop_type == 'forever':
                param_label_before = "重复执行"
            elif loop_type == 'until':
                param_label_before = "重复直到"
        elif self.block_type == "wait" or self.block_type == "delay":
            param_value = str(self.properties.get('time', 1))
            param_label_before = "等待"
            param_label_after = "秒"
        elif self.block_type == "mouse_click":
            param_label_before = "鼠标点击"
        elif self.block_type == "mouse_move":
            x = self.properties.get('x', 0)
            y = self.properties.get('y', 0)
            param_value = f"{x},{y}"
            param_label_before = "移动到"
        elif self.block_type == "mouse_drag":
            param_label_before = "鼠标拖拽"
        elif self.block_type == "keyboard_input":
            text = self.properties.get('text', 'Hello World')
            if len(text) > 8:
                text = text[:8] + "..."
            param_value = text
            param_label_before = "输入"
        elif self.block_type == "keyboard_key":
            key = self.properties.get('key', 'enter')
            param_value = key
            param_label_before = "按键"
        elif self.block_type == "find_image":
            param_label_before = "查找图像"
        elif self.block_type == "find_text":
            text = self.properties.get('text', '')
            if len(text) > 6:
                text = text[:6] + "..."
            if text:
                param_value = text
            param_label_before = "查找文字"
        elif self.block_type == "find_color":
            color = self.properties.get('color', '')
            if color:
                param_value = color
            param_label_before = "查找颜色"
        elif self.block_type == "image_match":
            param_label_before = "图像匹配"
        elif self.block_type == "run_script":
            script_name = self.properties.get('script_name', '未选择')
            if len(script_name) > 8:
                script_name = script_name[:8] + "..."
            param_value = script_name
            param_label_before = "执行脚本"
        elif self.block_type == "broadcast":
            msg = self.properties.get('message', '消息1')
            if len(msg) > 6:
                msg = msg[:6] + "..."
            param_value = msg
            param_label_before = "广播"
        elif self.block_type == "receive":
            msg = self.properties.get('message', '消息1')
            if len(msg) > 6:
                msg = msg[:6] + "..."
            param_value = msg
            param_label_before = "当收到"
        elif self.block_type == "start":
            param_label_before = "开始"
        elif self.block_type == "if":
            param_label_before = "如果"
        elif self.block_type == "function":
            param_label_before = "函数"
        elif self.block_type == "jump":
            param_label_before = "跳转"
        elif self.block_type == "and":
            param_label_before = "与"
        elif self.block_type == "or":
            param_label_before = "或"
        elif self.block_type == "not":
            param_label_before = "非"
        else:
            # 默认显示积木名称
            param_label_before = self.block_name
        
        # 设置字体
        from PyQt5.QtGui import QFontMetrics
        try:
            font = QFont("Microsoft YaHei", 11, QFont.Bold)
        except:
            font = QFont("Arial", 11, QFont.Bold)
        painter.setFont(font)
        fm = QFontMetrics(font)
        
        # 计算文字位置
        text_y = rect.height() / 2 + fm.height() / 4
        current_x = 15
        
        # 计算所需的总宽度
        needed_width = 15  # 左边距
        if param_label_before:
            needed_width += fm.width(param_label_before) + 8
        if param_value is not None:
            param_text_width = fm.width(param_value)
            param_box_width = max(param_text_width + 20, 40)
            needed_width += param_box_width + 8
        if param_label_after:
            needed_width += fm.width(param_label_after)
        needed_width += 15  # 右边距
        
        # 如果需要的宽度大于当前积木宽度，更新积木宽度
        if needed_width > rect.width():
            self.setRect(0, 0, needed_width, rect.height())
            rect = self.rect()  # 更新rect引用
        
        # 绘制前置标签
        if param_label_before:
            painter.setPen(QPen(QColor(60, 60, 60)))  # 深灰色文字
            painter.drawText(int(current_x), int(text_y), param_label_before)
            current_x += fm.width(param_label_before) + 8
        
        # 绘制参数框
        if param_value is not None:
            param_text_width = fm.width(param_value)
            param_width = max(param_text_width + 20, 40)
            param_height = rect.height() - 10
            param_y = 5
            
            # 确保参数框不超出积木右边界
            max_param_width = rect.width() - current_x - 15
            if param_width > max_param_width:
                param_width = max_param_width
            
            # 保存参数框位置用于点击检测
            self.param_box_rect = QRectF(current_x, param_y, param_width, param_height)
            
            # 绘制白色圆角矩形背景
            param_path = QPainterPath()
            param_radius = param_height / 2
            param_rect = QRectF(current_x, param_y, param_width, param_height)
            param_path.addRoundedRect(param_rect, param_radius, param_radius)
            
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.drawPath(param_path)
            
            # 绘制参数值（深色文字），如果太长则截断
            display_value = param_value
            while fm.width(display_value) > param_width - 10 and len(display_value) > 3:
                display_value = display_value[:-4] + "..."
            
            painter.setPen(QPen(QColor(80, 80, 80)))
            text_x = current_x + (param_width - fm.width(display_value)) / 2
            painter.drawText(int(text_x), int(text_y), display_value)
            
            current_x += param_width + 8
        else:
            self.param_box_rect = None
        
        # 绘制后置标签
        if param_label_after:
            painter.setPen(QPen(QColor(60, 60, 60)))  # 深灰色文字
            painter.drawText(int(current_x), int(text_y), param_label_after)
        
    def draw_shadow(self, painter, rect):
        """绘制积木阴影"""
        from PyQt5.QtGui import QColor
        
        shadow_offset = 2
        shadow_rect = rect.adjusted(shadow_offset, shadow_offset, shadow_offset, shadow_offset)
        
        # 设置阴影颜色
        shadow_color = QColor(0, 0, 0, 40)  # 半透明黑色
        painter.setBrush(QBrush(shadow_color))
        painter.setPen(Qt.NoPen)
        
        # 绘制阴影形状
        self.draw_block_shape(painter, shadow_rect, is_shadow=True)
        
    def draw_scratch_block(self, painter, rect, color):
        """绘制Scratch风格的积木形状"""
        # 创建渐变效果
        from PyQt5.QtGui import QLinearGradient
        gradient = QLinearGradient(0, 0, 0, rect.height())
        gradient.setColorAt(0, color.lighter(115))
        gradient.setColorAt(0.5, color)
        gradient.setColorAt(1, color.darker(115))
        
        # 设置画笔和画刷
        painter.setBrush(QBrush(gradient))
        painter.setPen(QPen(color.darker(130), 1.5))
        
        # 绘制积木形状
        self.draw_block_shape(painter, rect, is_shadow=False)
        
        # 绘制高光
        self.draw_highlight(painter, rect, color)
        
    def draw_block_shape(self, painter, rect, is_shadow=False):
        """绘制积木的基本形状"""
        from PyQt5.QtGui import QPainterPath
        
        path = QPainterPath()
        
        # 积木的基本参数
        corner_radius = 4
        notch_width = 10
        notch_height = 3
        tab_width = 10
        tab_height = 3
        
        # 根据积木类型调整形状
        if self.block_type == "start":
            # 帽子形状的开始积木
            self.draw_hat_shape(path, rect, corner_radius)
        elif self.block_type in ["loop", "if", "function"]:
            # C形状的容器积木
            self.draw_c_shape(path, rect, corner_radius, notch_width, notch_height)
        else:
            # 普通的拼图形状积木
            self.draw_puzzle_shape(path, rect, corner_radius, notch_width, notch_height, tab_width, tab_height)
        
        # 绘制路径
        painter.drawPath(path)
        
    def draw_hat_shape(self, path, rect, corner_radius):
        """绘制帽子形状（开始积木）- 连接点在左侧"""
        # 更精确的参数
        corner_radius = 8
        hat_height = 12  # 帽子的弧形高度
        tab_width = 30
        tab_height = 4
        notch_offset = 15  # 凸起距离左边缘的距离
        
        # 开始绘制帽子的弧形顶部
        path.moveTo(corner_radius, hat_height)
        
        # 帽子的弧形部分
        path.arcTo(0, 0, rect.width(), hat_height * 2, 180, 180)
        
        # 右侧
        path.lineTo(rect.width(), rect.height() - corner_radius)
        path.arcTo(rect.width() - corner_radius * 2, rect.height() - corner_radius * 2, 
                  corner_radius * 2, corner_radius * 2, 0, -90)
        
        # 底部右侧到凸起（凸起在左侧）
        path.lineTo(notch_offset + tab_width, rect.height())
        
        # 底部凸起（在左侧）
        path.lineTo(notch_offset + tab_width - 2, rect.height() + tab_height)
        path.lineTo(notch_offset + 2, rect.height() + tab_height)
        path.lineTo(notch_offset, rect.height())
        
        # 底部左侧到左下角
        path.lineTo(corner_radius, rect.height())
        path.arcTo(0, rect.height() - corner_radius * 2, corner_radius * 2, corner_radius * 2, 270, -90)
        
        # 左侧回到起点
        path.lineTo(0, hat_height)
        
    def draw_c_shape(self, path, rect, corner_radius, notch_width, notch_height):
        """绘制C形状（容器积木）- 连接点在左侧"""
        # 更精确的参数
        corner_radius = 8
        notch_width = 30
        notch_height = 4
        inner_indent = 15  # 内部缩进
        inner_corner = 4   # 内部圆角
        notch_offset = 15  # 凹槽距离左边缘的距离
        
        # 开始绘制路径
        path.moveTo(corner_radius, 0)
        
        # 顶部左圆角到凹槽（凹槽在左侧）
        path.lineTo(notch_offset, 0)
        
        # 顶部凹槽（在左侧）
        path.lineTo(notch_offset + 2, notch_height)
        path.lineTo(notch_offset + notch_width - 2, notch_height)
        path.lineTo(notch_offset + notch_width, 0)
        
        # 顶部右侧到右上角
        path.lineTo(rect.width() - corner_radius, 0)
        path.arcTo(rect.width() - corner_radius * 2, 0, corner_radius * 2, corner_radius * 2, 90, -90)
        
        # 右侧外边缘到内部凹陷开始
        inner_top = 30
        path.lineTo(rect.width(), inner_top)
        
        # 内部凹陷的右上角
        path.arcTo(rect.width() - inner_corner * 2, inner_top, inner_corner * 2, inner_corner * 2, 0, -90)
        path.lineTo(rect.width() - inner_indent, inner_top + inner_corner)
        
        # 内部凹陷的底部
        inner_bottom = rect.height() - 30
        path.lineTo(rect.width() - inner_indent, inner_bottom - inner_corner)
        
        # 内部凹陷的右下角
        path.arcTo(rect.width() - inner_corner * 2, inner_bottom - inner_corner * 2, inner_corner * 2, inner_corner * 2, 270, -90)
        path.lineTo(rect.width(), inner_bottom)
        
        # 右侧外边缘到右下角
        path.lineTo(rect.width(), rect.height() - corner_radius)
        path.arcTo(rect.width() - corner_radius * 2, rect.height() - corner_radius * 2, 
                  corner_radius * 2, corner_radius * 2, 0, -90)
        
        # 底部右侧到凸起（凸起在左侧）
        path.lineTo(notch_offset + notch_width, rect.height())
        
        # 底部凸起（在左侧）
        path.lineTo(notch_offset + notch_width - 2, rect.height() + notch_height)
        path.lineTo(notch_offset + 2, rect.height() + notch_height)
        path.lineTo(notch_offset, rect.height())
        
        # 底部左侧到左下角
        path.lineTo(corner_radius, rect.height())
        
        # 左下角
        path.arcTo(0, rect.height() - corner_radius * 2, corner_radius * 2, corner_radius * 2, 270, -90)
        
        # 左侧
        path.lineTo(0, corner_radius)
        
        # 左上角
        path.arcTo(0, 0, corner_radius * 2, corner_radius * 2, 180, -90)
        
    def draw_puzzle_shape(self, path, rect, corner_radius, notch_width, notch_height, tab_width, tab_height):
        """绘制拼图形状（普通积木）- 连接点在左侧"""
        # 更精确的参数
        corner_radius = 8
        notch_width = 30
        notch_height = 4
        tab_width = 30
        tab_height = 4
        notch_offset = 15  # 凹槽距离左边缘的距离
        
        # 开始绘制路径
        path.moveTo(corner_radius, 0)
        
        # 顶部左圆角到凹槽（凹槽在左侧）
        path.lineTo(notch_offset, 0)
        
        # 顶部凹槽（在左侧，接收上一个积木的凸起）
        path.lineTo(notch_offset + 2, notch_height)
        path.lineTo(notch_offset + notch_width - 2, notch_height)
        path.lineTo(notch_offset + notch_width, 0)
        
        # 顶部右侧到右上角
        path.lineTo(rect.width() - corner_radius, 0)
        path.arcTo(rect.width() - corner_radius * 2, 0, corner_radius * 2, corner_radius * 2, 90, -90)
        
        # 右侧
        path.lineTo(rect.width(), rect.height() - corner_radius)
        
        # 右下角
        path.arcTo(rect.width() - corner_radius * 2, rect.height() - corner_radius * 2, 
                  corner_radius * 2, corner_radius * 2, 0, -90)
        
        # 底部右侧到凸起（凸起在左侧）
        path.lineTo(notch_offset + tab_width, rect.height())
        
        # 底部凸起（在左侧，连接下一个积木）
        path.lineTo(notch_offset + tab_width - 2, rect.height() + tab_height)
        path.lineTo(notch_offset + 2, rect.height() + tab_height)
        path.lineTo(notch_offset, rect.height())
        
        # 底部左侧到左下角
        path.lineTo(corner_radius, rect.height())
        path.arcTo(0, rect.height() - corner_radius * 2, corner_radius * 2, corner_radius * 2, 270, -90)
        
        # 左侧
        path.lineTo(0, corner_radius)
        
        # 左上角
        path.arcTo(0, 0, corner_radius * 2, corner_radius * 2, 180, -90)
        
    def draw_highlight(self, painter, rect, color):
        """绘制积木高光"""
        from PyQt5.QtGui import QLinearGradient
        
        # 顶部高光
        highlight_gradient = QLinearGradient(0, 0, 0, 6)
        highlight_gradient.setColorAt(0, color.lighter(140))
        highlight_gradient.setColorAt(1, Qt.transparent)
        
        painter.setBrush(QBrush(highlight_gradient))
        painter.setPen(Qt.NoPen)
        
        # 绘制高光矩形
        highlight_rect = rect.adjusted(2, 2, -2, -rect.height() + 6)
        painter.drawRoundedRect(highlight_rect, 2, 2)
        
    def setup_block_visual(self):
        """设置积木的视觉外观 - Scratch风格胶囊形状"""
        # 根据积木类型和内容计算宽度
        width = self.calculate_block_width()
        
        if self.block_type in ["loop", "if", "function"]:
            height = 42
        else:
            height = 36
        
        block_color = self.get_block_color(self.block_type)
        self.setRect(0, 0, width, height)
        self.setBrush(QBrush(block_color))
        self.setPen(QPen(block_color.darker(130), 2))
        self.setAcceptedMouseButtons(Qt.LeftButton)
        
        # 不再使用单独的文字项，文字在paint方法中绘制
        self.text_item = None
        
        # 不再使用连接点图形项，连接通过位置检测
        self.top_connection = None
        self.bottom_connection = None
        self.input_connection = None
        
        if self.block_type in ["loop", "if", "function"]:
            self.contain_area = QGraphicsRectItem(30, height, width - 60, 100, self)
            self.contain_area.setBrush(QBrush(QColor(0, 0, 0, 0)))
            self.contain_area.setPen(QPen(QColor(0, 0, 0, 0), 1, Qt.DashLine))
            self.contain_area.setZValue(-1)
    
    def calculate_block_width(self):
        """根据积木内容计算合适的宽度"""
        from PyQt5.QtGui import QFontMetrics
        
        try:
            font = QFont("Microsoft YaHei", 11, QFont.Bold)
        except:
            font = QFont("Arial", 11, QFont.Bold)
        fm = QFontMetrics(font)
        
        # 基础宽度（左右边距）
        base_width = 30
        
        # 根据积木类型计算所需宽度
        label_width = 0
        param_width = 0
        suffix_width = 0
        
        if self.block_type == "loop":
            loop_type = self.properties.get('loop_type', 'count')
            if loop_type == 'count':
                count = str(self.properties.get('count', 10))
                label_width = fm.width("重复") + 8
                param_width = max(fm.width(count) + 20, 40) + 8
                suffix_width = fm.width("次")
            elif loop_type == 'forever':
                label_width = fm.width("重复执行")
            else:
                label_width = fm.width("重复直到")
        elif self.block_type == "wait" or self.block_type == "delay":
            time_val = str(self.properties.get('time', 1))
            label_width = fm.width("等待") + 8
            param_width = max(fm.width(time_val) + 20, 40) + 8
            suffix_width = fm.width("秒")
        elif self.block_type == "mouse_click":
            label_width = fm.width("鼠标点击")
        elif self.block_type == "mouse_move":
            x = self.properties.get('x', 0)
            y = self.properties.get('y', 0)
            coord_text = f"{x},{y}"
            label_width = fm.width("移动到") + 8
            param_width = max(fm.width(coord_text) + 20, 40)
        elif self.block_type == "keyboard_input":
            text = self.properties.get('text', 'Hello World')
            # 显示时会截断，但计算宽度时用完整文本
            display_text = text[:8] + "..." if len(text) > 8 else text
            label_width = fm.width("输入") + 8
            param_width = max(fm.width(display_text) + 20, 60)
        elif self.block_type == "keyboard_key":
            key = self.properties.get('key', 'enter')
            label_width = fm.width("按键") + 8
            param_width = max(fm.width(key) + 20, 40)
        elif self.block_type == "find_image":
            label_width = fm.width("查找图像")
        elif self.block_type == "find_text":
            text = self.properties.get('text', '')
            display_text = text[:6] + "..." if len(text) > 6 else text
            label_width = fm.width("查找文字") + 8
            if text:
                param_width = max(fm.width(display_text) + 20, 40)
        elif self.block_type == "find_color":
            color = self.properties.get('color', '')
            label_width = fm.width("查找颜色") + 8
            if color:
                param_width = max(fm.width(color) + 20, 40)
        elif self.block_type == "run_script":
            script_name = self.properties.get('script_name', '未选择')
            display_name = script_name[:8] + "..." if len(script_name) > 8 else script_name
            label_width = fm.width("执行脚本") + 8
            param_width = max(fm.width(display_name) + 20, 60)
        elif self.block_type == "broadcast":
            msg = self.properties.get('message', '消息1')
            display_msg = msg[:6] + "..." if len(msg) > 6 else msg
            label_width = fm.width("广播") + 8
            param_width = max(fm.width(display_msg) + 20, 40)
        elif self.block_type == "receive":
            msg = self.properties.get('message', '消息1')
            display_msg = msg[:6] + "..." if len(msg) > 6 else msg
            label_width = fm.width("当收到") + 8
            param_width = max(fm.width(display_msg) + 20, 40)
        elif self.block_type == "start":
            label_width = fm.width("开始")
        elif self.block_type == "if":
            label_width = fm.width("如果")
        else:
            label_width = fm.width(self.block_name)
        
        total_width = base_width + label_width + param_width + suffix_width
        return max(total_width, 100)

    def get_block_color(self, block_type):
        """根据积木类型返回柔和的颜色"""
        color_map = {
            # 事件积木 - 柔和黄色
            "start": QColor(255, 213, 128),
            "broadcast": QColor(255, 213, 128),
            "receive": QColor(255, 213, 128),
            
            # 控制积木 - 柔和橙色
            "loop": QColor(255, 179, 128),
            "if": QColor(255, 179, 128),
            "function": QColor(255, 179, 128),
            "wait": QColor(255, 179, 128),
            "delay": QColor(255, 179, 128),
            "jump": QColor(255, 179, 128),

            # 动作积木 - 柔和蓝色
            "mouse_move": QColor(128, 179, 255),
            "mouse_click": QColor(128, 179, 255),
            "mouse_drag": QColor(128, 179, 255),
            
            # 键盘积木 - 柔和天蓝色
            "keyboard_input": QColor(153, 204, 255),
            "keyboard_key": QColor(153, 204, 255),
            
            # 图像识别积木 - 柔和紫色
            "find_image": QColor(191, 153, 255),
            "find_text": QColor(191, 153, 255),
            "find_color": QColor(191, 153, 255),
            "image_match": QColor(191, 153, 255),
            
            # 脚本积木 - 柔和青色
            "run_script": QColor(128, 230, 230),
            
            # 逻辑积木 - 柔和绿色
            "and": QColor(153, 230, 153),
            "or": QColor(153, 230, 153),
            "not": QColor(153, 230, 153)
        }
        
        return color_map.get(block_type, QColor(180, 180, 180))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            #                                                 
            self.setSelected(True)
            
            #                                     
            scene = self.scene()
            if hasattr(scene, 'on_block_selected'):
                scene.on_block_selected(self)
            elif hasattr(scene, 'parent') and hasattr(scene.parent, 'on_block_selected'):
                scene.parent.on_block_selected(self)
                
            #                                                                                                 
            self.drag_start_pos = event.scenePos()
            
            self.original_pos = self.pos()
            
            self._collect_child_offsets()
            
            #                                                                                                 
            logger.info(f"             {self.block_name}                       ?-                         : ({self.original_pos.x():.1f}, {self.original_pos.y():.1f})")
            
            
        super().mousePressEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """双击编辑参数"""
        if event.button() == Qt.LeftButton:
            # 检查是否点击在参数框内
            click_pos = event.pos()
            
            if hasattr(self, 'param_box_rect') and self.param_box_rect and self.param_box_rect.contains(click_pos):
                self.edit_parameter()
            else:
                # 双击积木本身也可以编辑
                self.edit_parameter()
        
        super().mouseDoubleClickEvent(event)
    
    def edit_parameter(self):
        """弹出对话框编辑参数"""
        from PyQt5.QtWidgets import QInputDialog
        
        if self.block_type == "loop":
            loop_type = self.properties.get('loop_type', 'count')
            if loop_type == 'count':
                current = self.properties.get('count', 10)
                value, ok = QInputDialog.getInt(None, "编辑循环次数", "循环次数:", current, 1, 10000)
                if ok:
                    self.properties['count'] = value
                    self.update_block_size()
        elif self.block_type in ["wait", "delay"]:
            current = self.properties.get('time', 1.0)
            value, ok = QInputDialog.getDouble(None, "编辑等待时间", "等待时间(秒):", current, 0.1, 3600, 1)
            if ok:
                self.properties['time'] = value
                self.update_block_size()
        elif self.block_type == "mouse_move":
            current_x = self.properties.get('x', 0)
            current_y = self.properties.get('y', 0)
            x, ok1 = QInputDialog.getInt(None, "编辑X坐标", "X坐标:", current_x, 0, 10000)
            if ok1:
                y, ok2 = QInputDialog.getInt(None, "编辑Y坐标", "Y坐标:", current_y, 0, 10000)
                if ok2:
                    self.properties['x'] = x
                    self.properties['y'] = y
                    self.update_block_size()
        elif self.block_type == "keyboard_input":
            current = self.properties.get('text', 'Hello World')
            text, ok = QInputDialog.getText(None, "编辑输入文字", "输入文字:", text=current)
            if ok:
                self.properties['text'] = text
                self.update_block_size()
        elif self.block_type == "keyboard_key":
            current = self.properties.get('key', 'enter')
            keys = ['enter', 'tab', 'space', 'backspace', 'delete', 'escape', 
                    'up', 'down', 'left', 'right', 'home', 'end', 'pageup', 'pagedown',
                    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12',
                    'ctrl', 'alt', 'shift', 'win']
            try:
                current_index = keys.index(current)
            except:
                current_index = 0
            key, ok = QInputDialog.getItem(None, "选择按键", "按键:", keys, current_index, False)
            if ok:
                self.properties['key'] = key
                self.update_block_size()
        elif self.block_type == "broadcast":
            current = self.properties.get('message', '消息1')
            msg, ok = QInputDialog.getText(None, "编辑广播消息", "消息名称:", text=current)
            if ok:
                self.properties['message'] = msg
                self.update_block_size()
        elif self.block_type == "receive":
            current = self.properties.get('message', '消息1')
            msg, ok = QInputDialog.getText(None, "编辑接收消息", "消息名称:", text=current)
            if ok:
                self.properties['message'] = msg
                self.update_block_size()
        elif self.block_type == "find_text":
            current = self.properties.get('text', '')
            text, ok = QInputDialog.getText(None, "编辑查找文字", "查找文字:", text=current)
            if ok:
                self.properties['text'] = text
                self.update_block_size()
        elif self.block_type == "find_color":
            # 启动取色器
            self.start_color_picker()
        elif self.block_type == "run_script":
            # 选择或录制脚本
            self.edit_run_script()
    
    def start_color_picker(self):
        """启动取色器"""
        from PyQt5.QtWidgets import QMessageBox
        
        # 隐藏主窗口
        scene = self.scene()
        if scene and hasattr(scene, 'views') and scene.views():
            main_window = scene.views()[0].window()
            if main_window:
                main_window.hide()
        
        try:
            from modules.script_recorder import ColorPicker
            
            self.color_picker = ColorPicker()
            
            def on_color_picked(color):
                self.properties['color'] = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                self.properties['color_rgb'] = color
                self.update_block_size()
                # 显示主窗口
                if main_window:
                    main_window.show()
                    
            def on_cancelled():
                if main_window:
                    main_window.show()
                    
            self.color_picker.color_picked.connect(on_color_picked)
            self.color_picker.picking_cancelled.connect(on_cancelled)
            self.color_picker.start_picking()
            
        except Exception as e:
            logger.error(f"启动取色器失败: {e}")
            if main_window:
                main_window.show()
    
    def edit_run_script(self):
        """编辑执行脚本积木"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QListWidget, QMessageBox
        
        dialog = QDialog()
        dialog.setWindowTitle("选择或录制脚本")
        dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # 当前脚本
        current_script = self.properties.get('script_path', '')
        current_label = QLabel(f"当前脚本: {current_script or '未选择'}")
        layout.addWidget(current_label)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        
        # 选择已有脚本
        select_btn = QPushButton("选择脚本文件")
        def select_script():
            file_path, _ = QFileDialog.getOpenFileName(
                dialog, "选择脚本文件", "", "脚本文件 (*.json)"
            )
            if file_path:
                import os
                self.properties['script_path'] = file_path
                self.properties['script_name'] = os.path.basename(file_path)
                current_label.setText(f"当前脚本: {file_path}")
                self.update_block_size()
        select_btn.clicked.connect(select_script)
        btn_layout.addWidget(select_btn)
        
        # 录制新脚本
        record_btn = QPushButton("录制新脚本")
        def record_script():
            dialog.hide()
            self.start_script_recording(dialog)
        record_btn.clicked.connect(record_script)
        btn_layout.addWidget(record_btn)
        
        layout.addLayout(btn_layout)
        
        # 确定取消按钮
        bottom_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(dialog.reject)
        bottom_layout.addWidget(ok_btn)
        bottom_layout.addWidget(cancel_btn)
        layout.addLayout(bottom_layout)
        
        dialog.exec_()
    
    def start_script_recording(self, parent_dialog=None):
        """开始录制脚本"""
        from PyQt5.QtWidgets import QMessageBox
        import os
        
        # 隐藏主窗口
        scene = self.scene()
        main_window = None
        if scene and hasattr(scene, 'views') and scene.views():
            main_window = scene.views()[0].window()
            if main_window:
                main_window.hide()
        
        try:
            from modules.script_recorder import ScriptRecorder
            
            self.script_recorder = ScriptRecorder()
            
            # 显示提示
            QMessageBox.information(None, "开始录制", 
                "脚本录制已开始！\n\n"
                "- 您的鼠标点击、拖拽和键盘输入将被记录\n"
                "- 按 ESC 键停止录制\n\n"
                "点击确定后开始录制...")
            
            def on_recording_stopped():
                # 保存脚本
                actions = self.script_recorder.recorded_actions
                if actions:
                    # 保存到文件
                    scripts_dir = "scripts"
                    if not os.path.exists(scripts_dir):
                        os.makedirs(scripts_dir)
                    
                    import time
                    script_name = f"script_{int(time.time())}.json"
                    script_path = os.path.join(scripts_dir, script_name)
                    
                    self.script_recorder.save_script(script_path)
                    
                    self.properties['script_path'] = script_path
                    self.properties['script_name'] = script_name
                    self.update_block_size()
                    
                    QMessageBox.information(None, "录制完成", 
                        f"脚本已保存到: {script_path}\n共录制 {len(actions)} 个动作")
                
                # 显示主窗口
                if main_window:
                    main_window.show()
                if parent_dialog:
                    parent_dialog.show()
            
            self.script_recorder.recording_stopped.connect(on_recording_stopped)
            self.script_recorder.start_recording()
            
        except Exception as e:
            logger.error(f"启动脚本录制失败: {e}")
            if main_window:
                main_window.show()
            if parent_dialog:
                parent_dialog.show()
    
    def update_block_size(self):
        """更新积木大小并重绘"""
        width = self.calculate_block_width()
        height = self.rect().height()
        self.setRect(0, 0, width, height)
        self.update()
        
    def _collect_child_offsets(self):
        """收集所有子积木相对于当前积木的偏移量，确保移动时子积木跟随移动"""
        self.child_offsets = {}
        
        # 只收集当前积木下方连接的子积木，不收集父积木
        # connected_from 是连接在当前积木下方的积木（子积木）
        # connected_to 是当前积木连接到的积木（父积木）- 不应该跟随移动
        
        # 使用集合避免重复处理
        processed = set()
        processed.add(self)
        
        # 使用队列实现广度优先遍历
        from collections import deque
        queue = deque()
        
        # 只添加子积木到队列
        # 1. connected_from - 连接在当前积木下方的积木
        if hasattr(self, 'connected_from') and self.connected_from:
            queue.append(self.connected_from)
        
        # 2. connected_blocks - 容器内部的积木
        if hasattr(self, 'connected_blocks') and self.connected_blocks:
            for child in self.connected_blocks:
                queue.append(child)
        
        while queue:
            current_block = queue.popleft()
            
            if current_block in processed:
                continue
                
            processed.add(current_block)
            
            # 记录子积木的偏移量
            offset = current_block.pos() - self.pos()
            self.child_offsets[current_block] = offset
            
            # 继续收集该子积木的子积木
            if hasattr(current_block, 'connected_from') and current_block.connected_from:
                if current_block.connected_from not in processed:
                    queue.append(current_block.connected_from)
                    
            if hasattr(current_block, 'connected_blocks') and current_block.connected_blocks:
                for child in current_block.connected_blocks:
                    if child not in processed:
                        queue.append(child)
        
        logger.debug(f"积木 {self.block_name} 收集到 {len(self.child_offsets)} 个子积木")
        
    def mouseMoveEvent(self, event):
        if self.isSelected() and event.buttons() == Qt.LeftButton and hasattr(self, 'drag_start_pos'):
            distance = (event.scenePos() - self.drag_start_pos).manhattanLength()
            
            is_dragging = False
            if hasattr(self, 'is_dragging') and self.is_dragging:
                is_dragging = True
            elif distance > 5:
                self.is_dragging = True
                is_dragging = True
                
            if is_dragging:
                delta = event.scenePos() - self.drag_start_pos
                new_pos = self.original_pos + delta
                new_pos = self._apply_boundary_constraints(new_pos)
                
                self.setPos(new_pos)
                
                # 移动所有子积木
                for child, offset in getattr(self, 'child_offsets', {}).items():
                    child.setPos(new_pos + offset)
                
                # 注意：移动时不检查断开连接，因为子积木是跟随移动的
                # 只有在释放鼠标后才检查是否需要断开
                    
                # 强制更新场景，避免拖动痕迹
                scene = self.scene()
                if scene:
                    scene.update()
                
                
        
    def _apply_boundary_constraints(self, pos):
        """应用边界约束，防止积木移出场景范围"""
        scene = self.scene()
        if not scene:
            return pos
        
        # 获取场景的实际大小
        scene_rect = scene.sceneRect()
        block_rect = self.sceneBoundingRect()
        
        # 确保积木不会移出场景边界
        constrained_pos = QPointF(
            max(scene_rect.left(), min(pos.x(), scene_rect.right() - block_rect.width())),
            max(scene_rect.top(), min(pos.y(), scene_rect.bottom() - block_rect.height()))
        )
        
        return constrained_pos
        
    def _update_drag_visual_feedback(self):
        """                                                                        """
        #                                                             
        if not hasattr(self, 'original_pen'):
            self.original_pen = self.pen()
            
        highlight_pen = QPen(Qt.yellow, 3)
        self.setPen(highlight_pen)
        
        # 更新连接的子积木的高亮
        for child in getattr(self, 'connected_blocks', []):
            if not hasattr(child, 'original_pen'):
                child.original_pen = child.pen()
            child.setPen(highlight_pen)
        
    def mouseReleaseEvent(self, event):
        """                                     -                         """
        if event.button() == Qt.LeftButton:
            final_pos = self.pos()
            
            #                                     
            dragged = False
            if hasattr(self, 'is_dragging') and self.is_dragging:
                dragged = True
            elif hasattr(self, 'original_pos'):
                delta_x = final_pos.x() - self.original_pos.x()
                delta_y = final_pos.y() - self.original_pos.y()
                distance = ((delta_x ** 2) + (delta_y ** 2)) ** 0.5
                
                logger.info(f"             {self.block_name}                          -                         : ({self.original_pos.x():.1f}, {self.original_pos.y():.1f}), "
                           f"                        : ({final_pos.x():.1f}, {final_pos.y():.1f}), "
                           f"            : (    x={delta_x:.1f},     y={delta_y:.1f}),             : {distance:.1f}px")
                
                # 如果移动距离超过阈值，也视为拖拽
                if distance > 5:
                    dragged = True
            
            #                                                 
            if hasattr(self, 'original_pen'):
                self.setPen(self.original_pen)
                
            for child in getattr(self, 'child_offsets', {}).keys():
                if hasattr(child, 'original_pen'):
                    child.setPen(child.original_pen)
                    
            # 重置拖拽状态而不是删除属性，避免属性未定义错误
            self.is_dragging = False
            if hasattr(self, 'drag_start_pos'):
                delattr(self, 'drag_start_pos')
            if hasattr(self, 'original_pos'):
                delattr(self, 'original_pos')
            if hasattr(self, 'child_offsets'):
                delattr(self, 'child_offsets')
                
            if dragged:
                logger.debug(f"积木 {self.block_name} 被拖拽")
                # 先检查是否需要断开连接
                self.check_disconnections()
                # 再检查是否可以建立新连接
                self.check_connections()
                
                # 拖拽结束后，自动扩展画布
                scene = self.scene()
                if scene and hasattr(scene, 'parent') and hasattr(scene.parent, 'auto_expand_scene'):
                    scene.parent.auto_expand_scene()
            else:
                logger.debug(f"积木 {self.block_name} 被点击")
            
        super().mouseReleaseEvent(event)
        
    def check_disconnections(self):
        """检查是否需要断开连接"""
        scene = self.scene()
        if not scene:
            return
        
        # 连接点偏移量（与绘制代码中的 notch_offset 一致）
        notch_offset = 15
        tab_width = 30
        connection_center = notch_offset + tab_width / 2  # 连接点中心位置
            
        # 检查垂直连接的断开条件（距离超过50像素）
        if hasattr(self, 'connected_to') and self.connected_to:
            # 使用左侧连接点位置计算距离
            self_top_pos = self.pos() + QPointF(connection_center, 0)
            other_bottom_pos = self.connected_to.pos() + QPointF(connection_center, self.connected_to.rect().height())
            
            distance = (self_top_pos - other_bottom_pos).manhattanLength()
            
            if distance > 50:  # 增大断开距离阈值
                other_name = self.connected_to.block_name
                self.disconnect_from(self.connected_to)
                logger.info(f"积木 {self.block_name} 与 {other_name} 断开连接 (距离: {distance:.1f}px)")
        
        if hasattr(self, 'connected_from') and self.connected_from:
            # 使用左侧连接点位置计算距离
            self_bottom_pos = self.pos() + QPointF(connection_center, self.rect().height())
            other_top_pos = self.connected_from.pos() + QPointF(connection_center, 0)
            
            distance = (self_bottom_pos - other_top_pos).manhattanLength()
            
            if distance > 50:  # 增大断开距离阈值
                other_name = self.connected_from.block_name
                self.disconnect_from(self.connected_from)
                logger.info(f"积木 {self.block_name} 与 {other_name} 断开连接 (距离: {distance:.1f}px)")
        
        # 检查包含区域内的子积木的断开条件
        if hasattr(self, 'connected_blocks') and self.connected_blocks:
            for child in self.connected_blocks.copy():
                if self.block_type in ["loop", "if", "function"] and hasattr(self, 'contain_area'):
                    contain_rect = self.contain_area.sceneBoundingRect()
                    child_rect = child.sceneBoundingRect()
                    
                    # 计算距离和重叠率两种断开条件
                    center1 = contain_rect.center()
                    center2 = child_rect.center()
                    distance = (center1 - center2).manhattanLength()
                    
                    overlap_ratio = self.calculate_overlap_ratio(contain_rect, child_rect)
                    
                    # 如果距离超过100像素或重叠率低于0.1，断开连接
                    if distance > 100 or overlap_ratio < 0.1:
                        child_name = child.block_name
                        self.disconnect_from(child)
                        logger.info(f"子积木 {child_name} 从 {self.block_name} 中移出，断开连接 (距离: {distance:.1f}px, 重叠率: {overlap_ratio:.2f})")
        
        # 检查当前积木是否还在父积木的包含区域内
        if self.connected_to and self.connected_to.block_type in ["loop", "if", "function"]:
            if hasattr(self.connected_to, 'contain_area'):
                contain_rect = self.connected_to.contain_area.sceneBoundingRect()
                self_rect = self.sceneBoundingRect()
                
                overlap_ratio = self.calculate_overlap_ratio(contain_rect, self_rect)
                
                if overlap_ratio < 0.1:
                    parent_name = self.connected_to.block_name
                    self.disconnect_from(self.connected_to)
                    logger.info(f"积木 {self.block_name} 从 {parent_name} 中移出，断开连接 (重叠率: {overlap_ratio:.2f})")
    
    def check_connections(self):
        scene = self.scene()
        if not scene:
            return
            
        logger.debug(f"             {self.block_name}                                   ?..")
        
        # 连接点位置常量（与绘制代码一致）
        notch_offset = 15
        tab_width = 30
        connection_center = notch_offset + tab_width / 2  # 连接点中心位置
        
        #                                                                                                                                                                                     
        all_blocks = [item for item in scene.items() if isinstance(item, BlockItem) and item != self]
        
        #                                                                                                       
        def distance_to_other(item):
            # 使用左侧连接点位置计算距离
            self_connection = self.pos() + QPointF(connection_center, self.rect().height() / 2)
            item_connection = item.pos() + QPointF(connection_center, item.rect().height() / 2)
            return (self_connection - item_connection).manhattanLength()
            
        all_blocks.sort(key=distance_to_other)
        
        for item in all_blocks:
            logger.debug(f"检查积木 {self.block_name} 与 {item.block_name} 的连接")
            
            # 如果两个积木类型匹配且距离合适，建立连接
            logger.debug(f"尝试连接积木 {self.block_name} 到 {item.block_name}")
            if self.can_connect_to(item):
                self.connect_to(item)
                # 找到合适的连接后停止检查其他积木
                break
        
    def can_connect_to(self, other_block):
        if other_block == self:
            logger.debug(f"积木 {self.block_name} 不能连接到自身")
            return False
        
        # 连接点位置常量（与绘制代码一致）
        notch_offset = 15
        tab_width = 30
        connection_center = notch_offset + tab_width / 2  # 连接点中心位置
            
        # 检查垂直连接条件 - 使用左侧连接点位置
        self_top_pos = self.pos() + QPointF(connection_center, 0)
        other_bottom_pos = other_block.pos() + QPointF(connection_center, other_block.rect().height())
        
        distance = (self_top_pos - other_bottom_pos).manhattanLength()
        
        # 检查左侧连接点的水平对齐
        self_connection_x = self.pos().x() + connection_center
        other_connection_x = other_block.pos().x() + connection_center
        horizontal_alignment = abs(self_connection_x - other_connection_x) < 40  # 增大容差
        
        vertical_direction = self_top_pos.y() > other_bottom_pos.y() - 10  # 检查当前积木是否在其他积木下方
        vertical_connection = distance < 50 and horizontal_alignment and vertical_direction  # 增大连接距离

        if vertical_connection:
            logger.debug(f"积木 {self.block_name} 可以连接到 {other_block.block_name} "
                        f"(距离: {distance:.1f}px, 水平对齐: {horizontal_alignment}, 垂直方向: {vertical_direction})")
            return True
            
        #                                                       other_block                                          self                                                
        if other_block.block_type in ["loop", "if", "function"] and hasattr(other_block, 'contain_area'):
            contain_rect = other_block.contain_area.sceneBoundingRect()
            self_rect = self.sceneBoundingRect()
            
            overlap_ratio = self.calculate_overlap_ratio(contain_rect, self_rect)
            if overlap_ratio > 0.7:  #                                                                                                                         
                logger.debug(f"             {self.block_name}     ?{other_block.block_name}                                      (                ? {overlap_ratio:.2f})")
                return True
        
        return False
        
    def calculate_overlap_ratio(self, rect1, rect2):
        """计算两个矩形的重叠率"""
        overlap_rect = rect1.intersected(rect2)
        
        if overlap_rect.isEmpty():
            return 0.0
            
        rect2_area = rect2.width() * rect2.height()
        overlap_area = overlap_rect.width() * overlap_rect.height()
        
        return overlap_area / rect2_area
        
    def connect_to(self, other_block):
        """Connect to another block"""
        logger.debug(f"Connecting block {self.block_name} to {other_block.block_name}")
        
        # 连接点位置常量（与绘制代码一致）
        notch_offset = 15
        tab_width = 30
        connection_center = notch_offset + tab_width / 2  # 连接点中心位置
        
        #                                                                                                                                                 
        self_top_pos = self.pos() + QPointF(connection_center, 0)
        other_bottom_pos = other_block.pos() + QPointF(connection_center, other_block.rect().height())
        
        distance = (self_top_pos - other_bottom_pos).manhattanLength()
        
        # 检查左侧连接点的水平对齐
        self_connection_x = self.pos().x() + connection_center
        other_connection_x = other_block.pos().x() + connection_center
        horizontal_alignment = abs(self_connection_x - other_connection_x) < 40
        
        vertical_direction = (self.pos().y() > other_block.pos().y())
        
        is_vertical_connection = distance < 50 and horizontal_alignment and vertical_direction
        
        if is_vertical_connection:
            #                         
            if self.connected_to == other_block:
                logger.debug("Block is already connected")
                return
                
            if self.connected_to:
                logger.debug(f"Disconnecting from {self.connected_to.block_name}")
                self.connected_to.disconnect_from(self)
                
            self.connected_to = other_block
            other_block.connected_from = self
        
            # 将当前积木的位置设置为与目标积木左对齐（连接点对齐）
            target_x = other_block.pos().x()  # 左对齐，让连接点对齐
            # 连接点紧密对齐，不留间隙
            target_y = other_block.pos().y() + other_block.rect().height()
            
            self.setPos(target_x, target_y)
        
            self.is_connected = True
            other_block.is_connected = True
        
            logger.info(f"积木 {self.block_name} 连接到 {other_block.block_name}")
        
            # 更新两个积木的显示
            self.update()
            other_block.update()
            return
                
        #                                                       other_block                                          self                                                
        if other_block.block_type in ["loop", "if", "function"] and hasattr(other_block, 'contain_area'):
            contain_rect = other_block.contain_area.sceneBoundingRect()
            self_rect = self.sceneBoundingRect()
            overlap_ratio = self.calculate_overlap_ratio(contain_rect, self_rect)
            
            if overlap_ratio > 0.3:
                #                         
                if self not in other_block.connected_blocks:
                    other_block.connected_blocks.append(self)
                    self.connected_to = other_block
                    
                    #                                                                                                                                     
                    target_x = contain_rect.left() + (contain_rect.width() - self.rect().width()) // 2
                    target_y = contain_rect.top() + 20
                    self.setPos(target_x, target_y)
                    
                    self.is_connected = True
                    other_block.is_connected = True
                    
                    # 更新两个积木的显示
                    self.update()
                    other_block.update()
                    
                    logger.info(f"积木 {self.block_name} 成功连接到 {other_block.block_name}")
            
    def highlight_connection(self):
        """高亮显示积木连接状态 - 通过改变边框颜色"""
        # 使用绿色边框表示连接状态
        self.setPen(QPen(Qt.green, 3))
        self.update()
        
    def reset_connection_colors(self):
        """重置积木连接颜色 - 恢复正常边框"""
        block_color = self.get_block_color(self.block_type)
        self.setPen(QPen(block_color.darker(130), 2))
        self.update()
        
    def disconnect_from(self, other_block):
        """断开与另一个积木的连接"""
        #                                                                               
        if other_block.block_type in ["loop", "if", "function"] and self in other_block.connected_blocks:
            #                                           
            other_block.connected_blocks.remove(self)
            self.connected_to = None
            logger.info(f"积木 {self.block_name} 从 {other_block.block_name} 中移除")
        elif self.connected_to == other_block:
            self.connected_to = None
            other_block.connected_from = None
        elif hasattr(self, 'connected_from') and self.connected_from == other_block:
            self.connected_from = None
            other_block.connected_to = None
            
        self.is_connected = self.connected_to is not None or (hasattr(self, 'connected_from') and self.connected_from is not None) or len(getattr(self, 'connected_blocks', [])) > 0
        other_block.is_connected = other_block.connected_to is not None or (hasattr(other_block, 'connected_from') and other_block.connected_from is not None) or len(other_block.connected_blocks) > 0
        
        # 强制更新两个积木的显示
        self.update()
        other_block.update()
        
        # 强制刷新场景以确保连接点颜色更新
        scene = self.scene()
        if scene:
            scene.update(self.sceneBoundingRect())
            scene.update(other_block.sceneBoundingRect())
        
    def reset_connection_colors(self):
        """重置积木连接颜色 - 适配新的Scratch风格"""
        # 恢复正常的积木边框
        normal_pen = QPen(QColor(0, 0, 0), 2)
        self.setPen(normal_pen)
        
        # 恢复正常的文字颜色
        if hasattr(self, 'text_item') and self.text_item:
            self.text_item.setDefaultTextColor(Qt.white)

class DraggableGraphicsView(QGraphicsView):
    """支持鼠标拖动画布的 GraphicsView"""
    
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.setDragMode(QGraphicsView.NoDrag)
        self._is_panning = False
        self._pan_start_x = 0
        self._pan_start_y = 0
        
    def mousePressEvent(self, event):
        # 鼠标中键或右键按下时开始拖动画布
        if event.button() == Qt.MiddleButton or (event.button() == Qt.RightButton and event.modifiers() == Qt.NoModifier):
            self._is_panning = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        if self._is_panning:
            # 计算移动距离
            delta_x = event.x() - self._pan_start_x
            delta_y = event.y() - self._pan_start_y
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            
            # 移动滚动条
            h_bar = self.horizontalScrollBar()
            v_bar = self.verticalScrollBar()
            h_bar.setValue(h_bar.value() - delta_x)
            v_bar.setValue(v_bar.value() - delta_y)
            event.accept()
        else:
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton or event.button() == Qt.RightButton:
            if self._is_panning:
                self._is_panning = False
                self.setCursor(Qt.ArrowCursor)
                event.accept()
                return
        super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event):
        # 鼠标滚轮滚动画布
        delta = event.angleDelta().y()
        if event.modifiers() == Qt.ShiftModifier:
            # Shift + 滚轮 = 水平滚动
            h_bar = self.horizontalScrollBar()
            h_bar.setValue(h_bar.value() - delta)
        else:
            # 普通滚轮 = 垂直滚动
            v_bar = self.verticalScrollBar()
            v_bar.setValue(v_bar.value() - delta)
        event.accept()

class CustomTreeWidget(QTreeWidget):
    """                  TreeWidget                                                            """
    
    def startDrag(self, supportedActions):
        selected_items = self.selectedItems()
        if selected_items and len(selected_items) == 1:
            item = selected_items[0]
            if item.parent():
                block_name = item.text(0)
                block_type = item.text(1)
                
                from PyQt5.QtGui import QDrag
                from PyQt5.QtCore import QMimeData
                
                drag = QDrag(self)
                mime_data = QMimeData()
                mime_data.setText(f"{block_name}|{block_type}")
                drag.setMimeData(mime_data)
                
                #                                     
                from PyQt5.QtGui import QPixmap, QPainter, QColor
                pixmap = QPixmap(100, 30)
                pixmap.fill(QColor(200, 200, 200))
                painter = QPainter(pixmap)
                painter.drawText(10, 20, block_name)
                painter.end()
                drag.setPixmap(pixmap)
                
                drag.exec_(supportedActions)
    
class BlockEditor(QWidget):
    
    script_updated = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.init_blocks()
        self.current_script = []
        self.parent = parent
        self.selected_block = None
        
        # 初始化脚本组管理器（用于并行执行）
        from src.core.script_group_manager import ScriptGroupManager
        self.script_group_manager = None  # 延迟初始化，等待executor可用
        
    def parse_code_to_blocks(self, code):
        """将代码转换为积木"""
        logger.info("解析代码到积木")
        # 清空现有积木
        self.script_scene.clear()
        self.current_script = []
        
        # 首先尝试解析blocks_data数组
        blocks = []
        has_parsed_blocks_data = False
        try:
            # 查找blocks_data定义，使用更可靠的正则表达式匹配完整的JSON数组
            # 先找到blocks_data = [ 的位置，然后找到对应的结束 ]
            blocks_data_start = code.find('blocks_data = [')
            if blocks_data_start != -1:
                # 找到blocks_data开始位置
                blocks_data_start += len('blocks_data = [')
                # 计算JSON数组的结束位置
                bracket_count = 1
                blocks_data_end = blocks_data_start
                
                while blocks_data_end < len(code) and bracket_count > 0:
                    char = code[blocks_data_end]
                    if char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                    blocks_data_end += 1
                
                if bracket_count == 0:
                    # 提取完整的JSON字符串
                    blocks_data_str = '[' + code[blocks_data_start:blocks_data_end-1] + ']'
                    logger.info(f"找到blocks_data: {blocks_data_str[:100]}...")
                    try:
                        blocks = json.loads(blocks_data_str)
                        logger.info(f"成功解析blocks_data，包含 {len(blocks)} 个积木")
                        has_parsed_blocks_data = True
                        
                        # 将解析到的积木添加到场景中
                        for block in blocks:
                            block_item = BlockItem(block['name'], block['type'], block['properties'])
                            block_item.setPos(block.get('position', (100, 50)))
                            self.script_scene.addItem(block_item)
                            self.current_script.append(block)
                        
                        # 更新当前脚本，并按照 y 坐标排序，确保执行顺序与上下位置匹配
                        self.current_script = sorted(self.current_script, key=lambda block: block.get('position', (0, 0))[1])
                        logger.info(f"成功从blocks_data加载 {len(blocks)} 个积木")
                        
                        # 执行 update_script 以确保积木连接关系正确
                        self.update_script()
                        return self.current_script
                    except Exception as e:
                        logger.error(f"解析blocks_data失败: {e}")
                        blocks = []
                else:
                    logger.warning("未找到blocks_data结束位置，将使用代码解析方式")
            else:
                logger.warning("未找到blocks_data，将使用代码解析方式")
        except Exception as e:
            logger.error(f"解析blocks_data失败: {e}")
            blocks = []
        
        # 如果没有解析到blocks_data，则使用代码解析方式
        if not has_parsed_blocks_data:
            lines = code.split('\n')
            i = 0
            
            while i < len(lines):
                line = lines[i].strip()
                i += 1
                
                if not line or line.startswith('#') or line.startswith('"""'):
                    continue
                    
                # 解析循环积木
                if line.startswith("for loop_i in range("):
                    try:
                        count = int(float(line.split('(')[1].split(')')[0].strip()))
                        delay = 0.5
                        # 查找下一行的time.sleep
                        if i < len(lines):
                            next_line = lines[i].strip()
                            if next_line.startswith("time.sleep("):
                                delay = float(next_line.split('(')[1].split(')')[0].strip())
                                i += 1
                        block = {
                            'name': '循环',
                            'type': 'loop',
                            'properties': {
                                'count': count, 'delay': delay
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析循环积木失败: {e}")
                        continue
                    
                # 解析条件判断积木
                elif line.startswith("if ") and line.endswith(":"):
                    try:
                        condition = line[3:-1].strip()
                        block = {
                            'name': '条件判断',
                            'type': 'if',
                            'properties': {
                                'condition': condition, 'threshold': 0.8
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析条件判断积木失败: {e}")
                        continue
                    
                # 解析函数积木
                elif line.startswith("def ") and line.endswith(":"):
                    try:
                        function_name = line.split(' ')[1].split('(')[0].strip()
                        params_part = line.split('(')[1].split(')')[0].strip()
                        parameters = [p.strip() for p in params_part.split(',')] if params_part else []
                        block = {
                            'name': '函数',
                            'type': 'function',
                            'properties': {
                                'name': function_name, 'parameters': parameters
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析函数积木失败: {e}")
                        continue
                    
                # 解析查找文字积木
                if line.startswith("position = image_recognizer.find_text"):
                    try:
                        params = line.split('(')[1].split(')')[0].split(',')
                        text = params[0].strip().strip('"').strip("'")
                        threshold = float(params[1].strip())
                        
                        action = 'click'
                        while i < len(lines) and lines[i].strip():
                            next_line = lines[i].strip()
                            if "mouse_controller.click" in next_line:
                                action = 'click'
                            elif "mouse_controller.move_to" in next_line:
                                action = 'move'
                            elif "print" in next_line:
                                action = 'ignore'
                            i += 1
                            
                        block = {
                            'name': '查找文字',
                            'type': 'find_text',
                            'properties': {
                                'text': text, 'threshold': threshold, 'action': action
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析查找文字积木失败: {e}")
                        continue
                
                # 解析查找图像积木
                elif line.startswith("position = image_recognizer.find_image"):
                    try:
                        params = line.split('(')[1].split(')')[0].split(',')
                        image_path = params[0].strip().strip('"').strip("'")
                        threshold = float(params[1].strip())
                        
                        action = 'click'
                        while i < len(lines) and lines[i].strip():
                            next_line = lines[i].strip()
                            if "mouse_controller.click" in next_line:
                                action = 'click'
                            elif "mouse_controller.move_to" in next_line:
                                action = 'move'
                            elif "print" in next_line:
                                action = 'ignore'
                            i += 1
                            
                        block = {
                            'name': '查找图像',
                            'type': 'find_image',
                            'properties': {
                                'image_path': image_path, 'threshold': threshold, 'action': action
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析查找图像积木失败: {e}")
                        continue
                
                # 解析鼠标点击积木
                elif line.startswith("mouse_controller.click"):
                    try:
                        params = line.split('(')[1].split(')')[0].split(',')
                        x = None
                        y = None
                        button = 'left'
                        click_count = 1
                        delay = 0.1
                        
                        if len(params) >= 2:
                            x_str = params[0].strip()
                            y_str = params[1].strip()
                            if x_str != 'None' and y_str != 'None':
                                x = int(float(x_str))
                                y = int(float(y_str))
                        if len(params) >= 3:
                            button = params[2].strip().strip('"').strip("'")
                        if len(params) >= 4:
                            click_count = int(float(params[3].strip()))
                        if len(params) >= 5:
                            delay = float(params[4].strip())
                            
                        block = {
                            'name': '鼠标点击',
                            'type': 'mouse_click',
                            'properties': {
                                'x': x, 'y': y, 'button': button, 'click_count': click_count, 'delay': delay
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析鼠标点击积木失败: {e}")
                        continue
                
                # 解析鼠标移动积木
                elif line.startswith("mouse_controller.move_to"):
                    try:
                        params = line.split('(')[1].split(')')[0].split(',')
                        x = int(float(params[0].strip()))
                        y = int(float(params[1].strip()))
                        duration = 0.5
                        if len(params) >= 3:
                            duration = float(params[2].strip())
                            
                        block = {
                            'name': '鼠标移动',
                            'type': 'mouse_move',
                            'properties': {
                                'x': x, 'y': y, 'duration': duration, 'random_offset': 5
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析鼠标移动积木失败: {e}")
                        continue
                
                # 解析鼠标拖拽积木
                elif line.startswith("mouse_controller.drag_to"):
                    try:
                        params = line.split('(')[1].split(')')[0].split(',')
                        start_x = int(float(params[0].strip()))
                        start_y = int(float(params[1].strip()))
                        end_x = int(float(params[2].strip()))
                        end_y = int(float(params[3].strip()))
                        duration = 1.0
                        random_offset = 0
                        if len(params) >= 5:
                            duration = float(params[4].strip())
                        block = {
                            'name': '鼠标拖拽',
                            'type': 'mouse_drag',
                            'properties': {
                                'start_x': start_x, 'start_y': start_y, 'end_x': end_x, 'end_y': end_y, 
                                'duration': duration, 'random_offset': random_offset
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析鼠标拖拽积木失败: {e}")
                        continue
                
                # 解析键盘输入积木
                elif line.startswith("keyboard_controller.type_text"):
                    try:
                        params = line.split('(')[1].split(')')[0].split(',')
                        text = params[0].strip().strip('"').strip("'")
                        delay = 0.1
                        if len(params) >= 2:
                            delay = float(params[1].strip())
                            
                        block = {
                            'name': '键盘输入',
                            'type': 'keyboard_input',
                            'properties': {
                                'text': text, 'delay': delay
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析键盘输入积木失败: {e}")
                        continue
                
                # 解析键盘按键积木
                elif line.startswith("keyboard_controller.press_key"):
                    try:
                        params = line.split('(')[1].split(')')[0].split(',')
                        key = params[0].strip().strip('"').strip("'")
                        presses = 1
                        interval = 0.0
                        if len(params) >= 2:
                            presses = int(float(params[1].strip()))
                        if len(params) >= 3:
                            interval = float(params[2].strip())
                            
                        block = {
                            'name': '键盘按键',
                            'type': 'keyboard_key',
                            'properties': {
                                'key': key, 'presses': presses, 'interval': interval
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析键盘按键积木失败: {e}")
                        continue
                
                # 解析等待积木，处理有缩进的情况
                elif "time.sleep" in line:
                    try:
                        # 提取time.sleep语句，忽略缩进
                        sleep_part = line.split("time.sleep")[1]
                        delay_time = float(sleep_part.split('(')[1].split(')')[0].strip())
                        block = {
                            'name': '等待',
                            'type': 'wait',
                            'properties': {
                                'time': delay_time
                            }
                        }
                        blocks.append(block)
                    except Exception as e:
                        logger.error(f"解析等待积木失败: {e}")
                        continue
        
        # 创建积木项并添加到场景
        for block in blocks:
            block_item = BlockItem(block['name'], block['type'], block['properties'])
            if 'position' in block:
                block_item.setPos(block['position'][0], block['position'][1])
            else:
                # 计算默认位置
                index = len(self.current_script)
                x = 50
                y = 50 + index * 60
                block_item.setPos(x, y)
                # 保存位置信息到积木数据中
                block['position'] = (x, y)
                
            self.script_scene.addItem(block_item)
            self.current_script.append(block)
        
        # 按照 y 坐标排序，确保执行顺序与上下位置匹配
        self.current_script = sorted(self.current_script, key=lambda block: block.get('position', (0, 0))[1])
        
        # 执行 update_script 以确保积木连接关系正确
        self.update_script()
        
        logger.info(f"代码解析完成，生成了 {len(blocks)} 个积木")
        
        return self.current_script
    
    def setup_ui(self):
        """                        """
        layout = QVBoxLayout(self)
        
        #                                                       
        main_layout = QHBoxLayout()
        
        self.block_library = CustomTreeWidget()
        self.block_library.setFixedWidth(250)
        self.block_library.setHeaderLabel("积木库")
        self.block_library.setDragEnabled(True)
        self.block_library.itemDoubleClicked.connect(self.add_block_to_script)
        self.block_library.setSelectionMode(QTreeWidget.SingleSelection)
        #                                                 
        self.block_library.setDragDropMode(QTreeWidget.DragOnly)
        main_layout.addWidget(self.block_library)
        
        self.script_edit_area = QWidget()
        self.script_edit_layout = QVBoxLayout(self.script_edit_area)
        
        self.script_scene = QGraphicsScene()
        # 设置更大的初始场景大小，支持放置更多积木
        self.script_scene.setSceneRect(0, 0, 2000, 2000)
        self.script_scene.setBackgroundBrush(QBrush(QColor(240, 240, 240)))
        
        # 创建自定义的 GraphicsView 支持鼠标拖动画布
        self.script_view = DraggableGraphicsView(self.script_scene)
        # 改为最小尺寸而非固定尺寸，允许窗口调整时自动扩展
        self.script_view.setMinimumWidth(450)
        self.script_view.setMinimumHeight(500)
        self.script_view.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.script_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # 启用滚动条，方便查看大画布
        self.script_view.setAutoFillBackground(False)
        # 启用拖放功能
        self.script_view.setAcceptDrops(True)
        self.script_view.dragEnterEvent = self.drag_enter_event
        self.script_view.dragMoveEvent = self.drag_move_event
        self.script_view.dropEvent = self.drop_event
        
        self.script_edit_layout.addWidget(self.script_view)
        
        script_control_layout = QHBoxLayout()
        self.add_block_btn = QPushButton("添加积木")
        self.add_block_btn.clicked.connect(self.add_selected_block)
        script_control_layout.addWidget(self.add_block_btn)
        
        self.remove_block_btn = QPushButton("删除积木")
        self.remove_block_btn.clicked.connect(self.remove_selected_block)
        script_control_layout.addWidget(self.remove_block_btn)
        
        self.clear_script_btn = QPushButton("清空脚本")
        self.clear_script_btn.clicked.connect(self.clear_script)
        script_control_layout.addWidget(self.clear_script_btn)
        
        self.script_edit_layout.addLayout(script_control_layout)
        
        main_layout.addWidget(self.script_edit_area)
        
        #                               
        self.property_editor = QWidget()
        self.property_editor.setFixedWidth(300)
        self.property_layout = QVBoxLayout(self.property_editor)
        
        property_group = QGroupBox("积木属性")
        property_layout = QVBoxLayout(property_group)
        
        self.block_type_label = QLabel("积木类型:")
        property_layout.addWidget(self.block_type_label)
        
        self.property_form_layout = QVBoxLayout()
        property_layout.addLayout(self.property_form_layout)
        
        #                                                                                                       
        self.quick_screenshot_btn = QPushButton("快速截图")
        self.quick_screenshot_btn.clicked.connect(self.quick_region_screenshot)
        self.quick_screenshot_btn.hide()
        property_layout.addWidget(self.quick_screenshot_btn)
        
        self.property_layout.addWidget(property_group)
        
        main_layout.addWidget(self.property_editor)
        
        layout.addLayout(main_layout)
    
    def init_blocks(self):
        """初始化积木库"""
        # 事件操作分组（新增）
        event_group = QTreeWidgetItem(self.block_library, ["事件操作"])
        QTreeWidgetItem(event_group, ["🚀 启动脚本", "start"])
        QTreeWidgetItem(event_group, ["📢 广播消息", "broadcast"])
        QTreeWidgetItem(event_group, ["📻 接收消息", "receive"])
        
        # 控制操作分组
        control_group = QTreeWidgetItem(self.block_library, ["控制操作"])
        QTreeWidgetItem(control_group, ["循环", "loop"])
        QTreeWidgetItem(control_group, ["如果", "if"])
        QTreeWidgetItem(control_group, ["函数", "function"])
        QTreeWidgetItem(control_group, ["等待", "wait"])
        QTreeWidgetItem(control_group, ["跳转", "jump"])
        
        # 逻辑操作分组
        logic_group = QTreeWidgetItem(self.block_library, ["逻辑操作"])
        QTreeWidgetItem(logic_group, ["与", "and"])
        QTreeWidgetItem(logic_group, ["或", "or"])
        QTreeWidgetItem(logic_group, ["非", "not"])
        
        # 动作操作分组
        action_group = QTreeWidgetItem(self.block_library, ["动作操作"])
        QTreeWidgetItem(action_group, ["鼠标移动", "mouse_move"])
        QTreeWidgetItem(action_group, ["鼠标点击", "mouse_click"])
        QTreeWidgetItem(action_group, ["鼠标拖拽", "mouse_drag"])
        QTreeWidgetItem(action_group, ["键盘输入", "keyboard_input"])
        QTreeWidgetItem(action_group, ["键盘按键", "keyboard_key"])
        
        # 图像操作分组
        image_group = QTreeWidgetItem(self.block_library, ["图像操作"])
        QTreeWidgetItem(image_group, ["查找图像", "find_image"])
        QTreeWidgetItem(image_group, ["查找文字", "find_text"])
        QTreeWidgetItem(image_group, ["查找颜色", "find_color"])
        QTreeWidgetItem(image_group, ["图像匹配", "image_match"])
        
        # 脚本操作分组
        script_group = QTreeWidgetItem(self.block_library, ["脚本操作"])
        QTreeWidgetItem(script_group, ["执行录制脚本", "run_script"])
        
        # 确保积木库可以正确拖拽
        self.block_library.itemPressed.connect(self.on_block_library_item_pressed)
        
        # 展开所有分组，让用户可以看到所有积木
        self.block_library.expandAll()
        
    def on_block_library_item_pressed(self, item, column):
        """积木库项被按下时的处理"""
        if item.parent():  # 只有子项可以被拖拽
            block_name = item.text(0)
            block_type = item.text(1)
            logger.debug(f"准备拖拽积木: {block_name} ({block_type})")
            
    def quick_region_screenshot(self):
        """快速区域截图方法"""
        logger.debug("快速区域截图功能被调用")
        # 实现快速截图功能
        try:
            # 暂时隐藏主窗口
            self.parent.hide()
            
            # 定义截图完成后的回调函数
            def on_screenshot_complete(pixmap):
                # 截图完成后显示主窗口
                self.parent.show()
                
                if pixmap:
                    # 保存截图到临时文件
                    import os
                    import time
                    temp_dir = "temp"
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    
                    timestamp = int(time.time())
                    filename = f"screenshot_{timestamp}.png"
                    file_path = os.path.join(temp_dir, filename)
                    
                    pixmap.save(file_path)
                    logger.info(f"快速截图成功，保存到: {file_path}")
                    
                    # 更新文本框
                    if hasattr(self, 'image_path_edit'):
                        self.image_path_edit.setText(file_path)
                        # 更新选中积木的属性
                        if self.selected_block:
                            self.selected_block.properties["image_path"] = file_path
                            self.update_script()
                else:
                    logger.info("快速截图已取消")
            
            # 启动快速区域截图工具
            self.current_screenshot_tool = self.parent.screenshot_manager.capture_region(callback=on_screenshot_complete)
            logger.info("快速区域截图工具已打开")
            
        except Exception as e:
            logger.error(f"快速截图功能出错: {e}")
            QMessageBox.critical(self, "错误", f"快速截图功能出错: {e}")
            # 确保主窗口可见
            self.parent.show()
    
    def quick_screenshot_for_operand(self, block_item, operand_name):
        """操作数快速截图方法"""
        logger.debug(f"操作数 {operand_name} 快速截图功能被调用")
        # 实现快速截图功能
        try:
            # 暂时隐藏主窗口
            self.parent.hide()
            
            # 定义截图完成后的回调函数
            def on_screenshot_complete(pixmap):
                # 截图完成后显示主窗口
                self.parent.show()
                
                if pixmap:
                    # 保存截图到临时文件
                    import os
                    import time
                    temp_dir = "temp"
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    
                    timestamp = int(time.time())
                    filename = f"screenshot_{timestamp}.png"
                    file_path = os.path.join(temp_dir, filename)
                    
                    pixmap.save(file_path)
                    logger.info(f"操作数 {operand_name} 快速截图成功，保存到: {file_path}")
                    
                    # 更新对应的文本框
                    if operand_name == "operand1" and hasattr(self, 'operand1_edit'):
                        self.operand1_edit.setText(file_path)
                        block_item.properties["operand1"] = file_path
                    elif operand_name == "operand2" and hasattr(self, 'operand2_edit'):
                        self.operand2_edit.setText(file_path)
                        block_item.properties["operand2"] = file_path
                    elif operand_name == "operand" and hasattr(self, 'operand_edit'):
                        self.operand_edit.setText(file_path)
                        block_item.properties["operand"] = file_path
                    elif operand_name == "image_path" and hasattr(self, 'image_path_edit'):
                        self.image_path_edit.setText(file_path)
                        block_item.properties["image_path"] = file_path
                    
                    # 更新脚本
                    self.update_script()
                else:
                    logger.info(f"操作数 {operand_name} 快速截图已取消")
            
            # 启动快速区域截图工具
            self.current_screenshot_tool = self.parent.screenshot_manager.capture_region(callback=on_screenshot_complete)
            logger.info("操作数快速区域截图工具已打开")
            
        except Exception as e:
            logger.error(f"操作数快速截图功能出错: {e}")
            QMessageBox.critical(self, "错误", f"操作数快速截图功能出错: {e}")
            # 确保主窗口可见
            self.parent.show()
        
    
    def add_block_to_script(self, item):
        if item.parent():  # 确保是子项而非分组
            block_name = item.text(0)
            block_type = item.text(1)
            
            # 获取默认属性
            properties = self.get_default_properties(block_type)
            
            # 获取现有积木的位置信息
            existing_blocks = [item for item in self.script_scene.items() if isinstance(item, BlockItem)]
            max_y = max([block.pos().y() + block.rect().height() for block in existing_blocks]) if existing_blocks else 0
            
            block_item = BlockItem(block_name, block_type, properties)
            
            if existing_blocks:
                y_position = max_y + 40  # 间隔40像素
            else:
                y_position = 50  # 第一个y坐标
            block_item.setPos(50, y_position)
            
            # 设置场景的块选择回调
            self.script_scene.on_block_selected = self.on_block_selected
            
            self.script_scene.addItem(block_item)
            
            # 自动扩展画布以容纳新积木
            self.auto_expand_scene()
            
            self.update_script()
    
    def auto_expand_scene(self):
        """自动扩展场景大小以容纳所有积木"""
        # 获取所有积木的边界
        items_rect = self.script_scene.itemsBoundingRect()
        
        if items_rect.isEmpty():
            return
        
        # 获取当前场景大小
        current_rect = self.script_scene.sceneRect()
        
        # 计算需要的最小尺寸（添加边距）
        margin = 200  # 边距
        min_width = max(2000, items_rect.right() + margin)
        min_height = max(2000, items_rect.bottom() + margin)
        
        # 如果需要扩展，则扩展场景
        new_width = max(current_rect.width(), min_width)
        new_height = max(current_rect.height(), min_height)
        
        if new_width > current_rect.width() or new_height > current_rect.height():
            self.script_scene.setSceneRect(0, 0, new_width, new_height)
            logger.debug(f"画布已自动扩展到: {new_width}x{new_height}")
    
    def add_selected_block(self):
        selected_items = self.block_library.selectedItems()
        if selected_items:
            self.add_block_to_script(selected_items[0])
    
    def remove_selected_block(self):
        if self.selected_block:
            block_name = self.selected_block.block_name
            self.script_scene.removeItem(self.selected_block)
            del self.selected_block
            self.selected_block = None
            self.update_script()
            self.clear_property_editor()
            logger.info(f"                        : {block_name}")
    
    def parse_code_to_blocks(self, code):
        """将Python代码转换为积木"""
        logger.info(f"开始解析代码: {code}")
        
        # 清空当前脚本
        self.clear_script()
        
        # 首先尝试解析blocks_data，这样可以完全恢复所有积木及其属性
        try:
            blocks_data_match = re.search(r'blocks_data\s*=\s*(\[.*?\])', code, re.DOTALL)
            if blocks_data_match:
                blocks_data_str = blocks_data_match.group(1)
                logger.info(f"找到blocks_data: {blocks_data_str}")
                blocks = json.loads(blocks_data_str)
                logger.info(f"成功解析blocks_data，包含 {len(blocks)} 个积木")
                
                # 将解析到的积木添加到场景中
                for block in blocks:
                    block_item = BlockItem(block['name'], block['type'], block['properties'])
                    block_item.setPos(block.get('position', (100, 50)))
                    self.script_scene.addItem(block_item)
                
                # 更新当前脚本，并按照 y 坐标排序，确保执行顺序与上下位置匹配
                self.current_script = sorted(blocks, key=lambda block: block.get('position', (0, 0))[1])
                logger.info(f"成功从blocks_data加载 {len(blocks)} 个积木")
                return self.current_script
        except Exception as e:
            logger.error(f"解析blocks_data出错: {e}")
        
        # 如果没有找到blocks_data，使用传统的解析方式
        logger.info("未找到blocks_data，使用传统解析方式")
        lines = code.split('\n')
        y_position = 50
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            # 简单的代码匹配逻辑
            block_name = ""
            block_type = "default"
            
            if "while" in line or "for" in line:
                block_name = "循环"
                block_type = "loop"
            elif "if" in line:
                block_name = "条件判断"
                block_type = "if"
            elif "def " in line:
                block_name = "函数"
                block_type = "function"
            elif "time.sleep" in line:
                block_name = "等待"
                block_type = "wait"
            elif "mouse_move" in line:
                block_name = "鼠标移动"
                block_type = "mouse_move"
            elif "mouse_click" in line:
                block_name = "鼠标点击"
                block_type = "mouse_click"
            elif "keyboard_input" in line:
                block_name = "键盘输入"
                block_type = "keyboard_input"
            elif "find_image" in line:
                block_name = "查找图像"
                block_type = "find_image"
            elif "find_text" in line:
                block_name = "查找文字"
                block_type = "find_text"
            elif "image_match" in line:
                block_name = "图像匹配"
                block_type = "image_match"
            else:
                block_name = "自定义"
                block_type = "default"
                
            # 创建积木
            block_item = BlockItem(block_name, block_type)
            block_item.setPos(50, y_position)
            self.script_scene.addItem(block_item)
            
            y_position += 80  # 增加垂直间距
            
        logger.info("代码转积木完成")
        self.update_script()
    
    def clear_script(self):
        """                        """
        self.script_scene.clear()
        self.current_script = []
        self.script_updated.emit("")
        self.clear_property_editor()
        logger.info("清空脚本")
        
    def drag_enter_event(self, event):
        """处理拖入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        logger.debug("拖拽进入脚本编辑区域")
        
    def drag_move_event(self, event):
        """处理拖入移动事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()
        logger.debug("拖拽在脚本编辑区域移动")
        
    def drop_event(self, event):
        """处理放置事件"""
        logger.debug("在脚本编辑区域放置积木")
        
        # 获取拖拽数据
        item_data = event.mimeData().text()
        logger.debug(f"拖拽数据: {item_data}")
        
        # 尝试解析拖拽的数据（假设格式为 'block_name|block_type'）
        if '|' in item_data:
            block_name, block_type = item_data.split('|')
        else:
            # 如果没有分隔符，可能是直接从积木库拖拽的默认格式
            block_name = item_data
            block_type = "default"
            
        logger.debug(f"解析到积木: {block_name} ({block_type})")
        
        # 创建新的积木并添加到脚本场景
        properties = {}
        block_item = BlockItem(block_name, block_type, properties)
        
        # 计算放置位置（相对于视图的坐标）
        view_pos = event.pos()
        scene_pos = self.script_view.mapToScene(view_pos)
        block_item.setPos(scene_pos.x() - block_item.rect().width()/2, 
                        scene_pos.y() - block_item.rect().height()/2)
        
        # 设置场景的块选择回调
        self.script_scene.on_block_selected = self.on_block_selected
        
        self.script_scene.addItem(block_item)
        
        # 更新脚本
        self.update_script()
        
        event.acceptProposedAction()
        logger.info(f"成功添加积木: {block_name}")
    
    def on_block_selected(self, block_item):
        """                                    """
        self.selected_block = block_item
        self.update_property_editor(block_item)
    
    def get_block_description(self, block_type):
        """获取积木的详细介绍和作用说明"""
        descriptions = {
            "start": {
                "title": "🚀 启动脚本",
                "desc": "脚本的入口点，定义脚本名称和启动方式。",
                "usage": "• 每个脚本必须有一个启动积木\n• 可设置快捷键快速启动\n• 支持自动启动选项"
            },
            "broadcast": {
                "title": "📢 广播消息",
                "desc": "向其他脚本发送消息，实现脚本间通信。",
                "usage": "• 发送指定名称的消息\n• 可设置延迟发送\n• 配合接收消息积木使用"
            },
            "receive": {
                "title": "📻 接收消息",
                "desc": "等待并接收其他脚本发送的消息。",
                "usage": "• 监听指定名称的消息\n• 可设置超时时间\n• 收到消息后继续执行"
            },
            "loop": {
                "title": "🔄 循环",
                "desc": "重复执行内部的积木，支持多种循环方式。",
                "usage": "• 计数循环：执行指定次数\n• 永远循环：持续执行直到停止\n• 条件循环：等待条件满足"
            },
            "if": {
                "title": "❓ 条件判断",
                "desc": "根据条件决定是否执行内部积木。",
                "usage": "• 支持图像/文字条件\n• 条件满足时执行内部积木\n• 可设置匹配阈值"
            },
            "function": {
                "title": "📦 函数定义",
                "desc": "定义可重复调用的代码块。",
                "usage": "• 封装常用操作\n• 支持参数传递\n• 提高代码复用性"
            },
            "wait": {
                "title": "⏰ 等待",
                "desc": "暂停脚本执行指定时间。",
                "usage": "• 设置等待秒数\n• 用于控制执行节奏\n• 等待页面加载等场景"
            },
            "delay": {
                "title": "⏱️ 延时",
                "desc": "短暂延迟脚本执行。",
                "usage": "• 设置延迟时间\n• 用于操作间隔\n• 避免操作过快"
            },
            "mouse_move": {
                "title": "🖱️ 鼠标移动",
                "desc": "将鼠标移动到指定位置。",
                "usage": "• 设置目标坐标(X,Y)\n• 可设置移动速度\n• 支持随机偏移"
            },
            "mouse_click": {
                "title": "🖱️ 鼠标点击",
                "desc": "在指定位置执行鼠标点击。",
                "usage": "• 支持左键/右键/中键\n• 可设置点击次数\n• 可设置点击间隔"
            },
            "mouse_drag": {
                "title": "🖱️ 鼠标拖拽",
                "desc": "从起点拖拽到终点。",
                "usage": "• 设置起点和终点坐标\n• 可设置拖拽速度\n• 支持随机偏移"
            },
            "keyboard_input": {
                "title": "⌨️ 键盘输入",
                "desc": "模拟键盘输入文字。",
                "usage": "• 输入指定文本\n• 可设置输入速度\n• 支持中英文输入"
            },
            "keyboard_key": {
                "title": "⌨️ 按键操作",
                "desc": "模拟按下指定按键。",
                "usage": "• 支持所有按键\n• 可设置按键次数\n• 支持组合键"
            },
            "find_image": {
                "title": "🔍 查找图像",
                "desc": "在屏幕上查找指定图像。",
                "usage": "• 选择目标图像文件\n• 设置匹配阈值\n• 找到后可点击/移动"
            },
            "find_text": {
                "title": "🔍 查找文字",
                "desc": "在屏幕上查找指定文字。",
                "usage": "• 输入要查找的文字\n• 使用OCR识别\n• 找到后可点击/移动"
            },
            "find_color": {
                "title": "🎨 查找颜色",
                "desc": "在屏幕上查找指定颜色。",
                "usage": "• 选择目标颜色\n• 设置容差范围\n• 找到后可点击/移动"
            },
            "image_match": {
                "title": "🖼️ 图像匹配",
                "desc": "匹配屏幕上的图像并执行操作。",
                "usage": "• 选择模板图像\n• 设置匹配精度\n• 支持多种匹配动作"
            },
            "jump": {
                "title": "↪️ 跳转",
                "desc": "跳转到指定的积木位置。",
                "usage": "• 绝对跳转：跳到指定积木\n• 相对跳转：向前/后跳转\n• 用于流程控制"
            },
            "and": {
                "title": "➕ 逻辑与",
                "desc": "两个条件都满足时为真。",
                "usage": "• 组合多个条件\n• 所有条件都满足才执行\n• 用于复杂判断"
            },
            "or": {
                "title": "➕ 逻辑或",
                "desc": "任一条件满足时为真。",
                "usage": "• 组合多个条件\n• 任一条件满足即执行\n• 用于多选一判断"
            },
            "not": {
                "title": "➖ 逻辑非",
                "desc": "条件取反。",
                "usage": "• 反转条件结果\n• 真变假，假变真\n• 用于否定判断"
            },
            "run_script": {
                "title": "▶️ 执行脚本",
                "desc": "执行录制的脚本文件。",
                "usage": "• 选择脚本文件\n• 设置播放速度\n• 可设置执行次数"
            }
        }
        
        return descriptions.get(block_type, {
            "title": "📦 积木",
            "desc": "执行指定操作。",
            "usage": "• 配置相关属性后使用"
        })
    
    def add_block_description(self, block_type):
        """在属性面板中添加积木介绍"""
        desc_info = self.get_block_description(block_type)
        
        # 创建介绍区域
        desc_frame = QFrame()
        desc_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 1px solid #b0c4de;
                border-radius: 5px;
                padding: 5px;
                margin-bottom: 10px;
            }
        """)
        desc_layout = QVBoxLayout(desc_frame)
        desc_layout.setSpacing(3)
        desc_layout.setContentsMargins(8, 8, 8, 8)
        
        # 标题
        title_label = QLabel(desc_info["title"])
        title_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #2c3e50;")
        desc_layout.addWidget(title_label)
        
        # 描述
        desc_label = QLabel(desc_info["desc"])
        desc_label.setStyleSheet("color: #34495e; font-size: 11px;")
        desc_label.setWordWrap(True)
        desc_layout.addWidget(desc_label)
        
        # 用法
        usage_label = QLabel(desc_info["usage"])
        usage_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        usage_label.setWordWrap(True)
        desc_layout.addWidget(usage_label)
        
        self.property_form_layout.addWidget(desc_frame)
        
        # 添加分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("color: #ddd;")
        self.property_form_layout.addWidget(separator)
    
    def update_property_editor(self, block_item):
        """                                          """
        if block_item:
            self.block_type_label.setText(f"积木类型: {block_item.block_name}")
            
            #                       
            for i in reversed(range(self.property_form_layout.count())):
                item = self.property_form_layout.itemAt(i)
                if item:
                    if item.widget():
                        item.widget().setParent(None)
                    elif item.layout():
                        #                                           
                        sub_layout = item.layout()
                        for j in reversed(range(sub_layout.count())):
                            sub_item = sub_layout.itemAt(j)
                            if sub_item.widget():
                                sub_item.widget().setParent(None)
                        self.property_form_layout.removeItem(sub_layout)
                    else:
                        self.property_form_layout.removeItem(item)
            
            
            block_type = block_item.block_type
            
            # 添加积木介绍
            self.add_block_description(block_type)
            
            if block_type == "start":
                # 启动积木属性编辑器
                # 脚本名称
                name_label = QLabel("脚本名称:")
                self.property_form_layout.addWidget(name_label)
                
                self.script_name_edit = QLineEdit(block_item.properties.get("name", "新脚本"))
                self.property_form_layout.addWidget(self.script_name_edit)
                
                # 自动启动
                auto_start_label = QLabel("自动启动:")
                self.property_form_layout.addWidget(auto_start_label)
                
                self.auto_start_check = QCheckBox()
                self.auto_start_check.setChecked(block_item.properties.get("auto_start", True))
                self.property_form_layout.addWidget(self.auto_start_check)
                
                # 快捷键（可选）
                hotkey_label = QLabel("快捷键（可选）:")
                self.property_form_layout.addWidget(hotkey_label)
                
                self.hotkey_edit = QLineEdit(block_item.properties.get("hotkey", ""))
                self.hotkey_edit.setPlaceholderText("例如: Ctrl+F1")
                self.property_form_layout.addWidget(self.hotkey_edit)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "broadcast":
                # 广播积木属性编辑器
                # 消息名称
                message_label = QLabel("消息名称:")
                self.property_form_layout.addWidget(message_label)
                
                self.broadcast_message_edit = QLineEdit(block_item.properties.get("message", "消息1"))
                self.broadcast_message_edit.setPlaceholderText("输入要广播的消息名称")
                self.property_form_layout.addWidget(self.broadcast_message_edit)
                
                # 延迟发送（可选）
                delay_label = QLabel("延迟发送(秒):")
                self.property_form_layout.addWidget(delay_label)
                
                self.broadcast_delay_spin = QDoubleSpinBox()
                self.broadcast_delay_spin.setRange(0.0, 60.0)
                self.broadcast_delay_spin.setSingleStep(0.1)
                self.broadcast_delay_spin.setValue(block_item.properties.get("delay", 0.0))
                self.property_form_layout.addWidget(self.broadcast_delay_spin)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "receive":
                # 接收积木属性编辑器
                # 消息名称
                message_label = QLabel("监听消息:")
                self.property_form_layout.addWidget(message_label)
                
                self.receive_message_edit = QLineEdit(block_item.properties.get("message", "消息1"))
                self.receive_message_edit.setPlaceholderText("输入要监听的消息名称")
                self.property_form_layout.addWidget(self.receive_message_edit)
                
                # 超时时间（可选）
                timeout_label = QLabel("超时时间(秒):")
                self.property_form_layout.addWidget(timeout_label)
                
                self.receive_timeout_spin = QDoubleSpinBox()
                self.receive_timeout_spin.setRange(0.0, 300.0)
                self.receive_timeout_spin.setSingleStep(1.0)
                self.receive_timeout_spin.setValue(block_item.properties.get("timeout", 30.0))
                self.receive_timeout_spin.setSpecialValueText("无限等待")
                self.property_form_layout.addWidget(self.receive_timeout_spin)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "find_image":
                
                #                                     
                image_label = QLabel("图像路径:")
                self.property_form_layout.addWidget(image_label)
                
                image_layout = QHBoxLayout()
                self.image_path_edit = QLineEdit(block_item.properties.get("image_path", ""))
                image_layout.addWidget(self.image_path_edit)
                
                browse_btn = QPushButton("浏览")
                browse_btn.clicked.connect(lambda: self.browse_image_file(block_item))
                image_layout.addWidget(browse_btn)
                
                screenshot_btn = QPushButton("快速截图")
                screenshot_btn.clicked.connect(lambda: self.quick_screenshot_for_operand(block_item, "image_path"))
                image_layout.addWidget(screenshot_btn)
                
                self.property_form_layout.addLayout(image_layout)
                
                threshold_label = QLabel("匹配阈值:")
                threshold_label = QLabel("匹配阈值:")
                threshold_label = QLabel("匹配阈值:")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                                                 
                action_label = QLabel("找到后的动作:")
                self.property_form_layout.addWidget(action_label)
                
                self.action_combo = QComboBox()
                self.action_combo.addItems(["点击", "移动", "忽略"])
                action_map = {"click": 0, "move": 1, "ignore": 2}
                self.action_combo.setCurrentIndex(action_map.get(block_item.properties.get("action", "click"), 0))
                self.property_form_layout.addWidget(self.action_combo)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "loop":
                # 循环类型选择
                loop_type_label = QLabel("循环类型:")
                self.property_form_layout.addWidget(loop_type_label)
                
                self.loop_type_combo = QComboBox()
                self.loop_type_combo.addItems(["计数循环", "永远重复", "重复直到条件满足"])
                
                # 根据当前属性设置选中项
                current_loop_type = block_item.properties.get("loop_type", "count")
                type_index = {"count": 0, "forever": 1, "until": 2}.get(current_loop_type, 0)
                self.loop_type_combo.setCurrentIndex(type_index)
                
                # 连接信号，当类型改变时更新界面
                self.loop_type_combo.currentIndexChanged.connect(lambda: self.update_loop_property_editor(block_item))
                self.property_form_layout.addWidget(self.loop_type_combo)
                
                # 循环次数（仅计数循环显示）
                self.count_label = QLabel("循环次数:")
                self.property_form_layout.addWidget(self.count_label)
                
                self.count_spin = QSpinBox()
                self.count_spin.setRange(1, 1000)
                self.count_spin.setValue(block_item.properties.get("count", 10))
                self.property_form_layout.addWidget(self.count_spin)
                
                # 条件设置（仅条件循环显示）
                self.condition_label = QLabel("结束条件:")
                self.property_form_layout.addWidget(self.condition_label)
                
                self.condition_combo = QComboBox()
                self.condition_combo.addItems(["找到图像", "找到文字", "位置匹配"])
                
                # 根据当前条件设置选中项
                current_condition = block_item.properties.get("condition", "image_found")
                condition_index = {"image_found": 0, "text_found": 1, "position_found": 2}.get(current_condition, 0)
                self.condition_combo.setCurrentIndex(condition_index)
                self.condition_combo.currentIndexChanged.connect(lambda: self.update_condition_value_editor(block_item))
                self.property_form_layout.addWidget(self.condition_combo)
                
                # 条件值设置（仅条件循环显示）
                self.condition_value_label = QLabel("条件值:")
                self.property_form_layout.addWidget(self.condition_value_label)
                
                # 条件值输入框（用于文字条件）
                self.condition_value_edit = QLineEdit(block_item.properties.get("condition_value", ""))
                self.condition_value_edit.setPlaceholderText("输入要查找的文字")
                self.property_form_layout.addWidget(self.condition_value_edit)
                
                # 条件图像选择（用于图像条件）
                condition_image_layout = QHBoxLayout()
                self.condition_image_edit = QLineEdit(block_item.properties.get("condition_value", ""))
                self.condition_image_edit.setPlaceholderText("选择条件图像文件")
                condition_image_layout.addWidget(self.condition_image_edit)
                
                browse_condition_btn = QPushButton("浏览")
                browse_condition_btn.clicked.connect(lambda: self.browse_condition_image(block_item))
                condition_image_layout.addWidget(browse_condition_btn)
                
                screenshot_condition_btn = QPushButton("截图")
                screenshot_condition_btn.clicked.connect(lambda: self.screenshot_condition_image(block_item))
                condition_image_layout.addWidget(screenshot_condition_btn)
                
                self.condition_image_widget = QWidget()
                self.condition_image_widget.setLayout(condition_image_layout)
                self.property_form_layout.addWidget(self.condition_image_widget)
                
                # 条件阈值
                self.condition_threshold_label = QLabel("匹配阈值:")
                self.property_form_layout.addWidget(self.condition_threshold_label)
                
                self.condition_threshold_spin = QDoubleSpinBox()
                self.condition_threshold_spin.setRange(0.1, 1.0)
                self.condition_threshold_spin.setSingleStep(0.1)
                self.condition_threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.condition_threshold_spin)
                
                # 延迟时间（所有类型都显示）
                delay_label = QLabel("延迟时间(秒):")
                self.property_form_layout.addWidget(delay_label)
                
                self.delay_spin = QDoubleSpinBox()
                self.delay_spin.setRange(0.1, 10.0)
                self.delay_spin.setSingleStep(0.1)
                self.delay_spin.setValue(block_item.properties.get("delay", 0.5))
                self.property_form_layout.addWidget(self.delay_spin)
                
                # 根据当前循环类型更新界面显示
                self.update_loop_property_editor(block_item)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "mouse_move":
                # X坐标
                x_label = QLabel("X坐标:")
                self.property_form_layout.addWidget(x_label)
                
                self.x_spin = QSpinBox()
                self.x_spin.setRange(0, 2000)
                self.x_spin.setValue(block_item.properties.get("x") or 100)
                self.property_form_layout.addWidget(self.x_spin)
                
                # Y坐标
                y_label = QLabel("Y坐标:")
                self.property_form_layout.addWidget(y_label)
                
                self.y_spin = QSpinBox()
                self.y_spin.setRange(0, 2000)
                self.y_spin.setValue(block_item.properties.get("y") or 100)
                self.property_form_layout.addWidget(self.y_spin)
                
                # 快速选择位置按钮
                quick_select_btn = QPushButton("快速选择位置")
                quick_select_btn.clicked.connect(lambda: self.quick_select_move_position(block_item))
                self.property_form_layout.addWidget(quick_select_btn)
                
                # 移动时间
                duration_label = QLabel("移动时间(秒):")
                self.property_form_layout.addWidget(duration_label)
                
                self.duration_spin = QDoubleSpinBox()
                self.duration_spin.setRange(0.1, 5.0)
                self.duration_spin.setSingleStep(0.1)
                self.duration_spin.setValue(block_item.properties.get("duration", 0.5))
                self.property_form_layout.addWidget(self.duration_spin)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "keyboard_input":
                #                         
                text_label = QLabel("输入文字:")
                self.property_form_layout.addWidget(text_label)
                
                self.text_edit = QLineEdit(block_item.properties.get("text", "Hello World"))
                self.property_form_layout.addWidget(self.text_edit)
                
                #                         
                delay_label = QLabel("延迟(秒):")
                self.property_form_layout.addWidget(delay_label)
                
                self.delay_spin = QDoubleSpinBox()
                self.delay_spin.setRange(0.01, 2.0)
                self.delay_spin.setSingleStep(0.05)
                self.delay_spin.setValue(block_item.properties.get("delay", 0.1))
                self.property_form_layout.addWidget(self.delay_spin)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "keyboard_key":
                # 键盘按键积木属性编辑器
                key_label = QLabel("按键类型:")
                self.property_form_layout.addWidget(key_label)
                
                self.key_combo = QComboBox()
                self.key_combo.addItems([
                    "回车键 (Enter)", "空格键 (Space)", "退格键 (Backspace)", 
                    "删除键 (Delete)", "制表键 (Tab)", "Esc键 (Escape)",
                    "上箭头 (Up)", "下箭头 (Down)", "左箭头 (Left)", "右箭头 (Right)",
                    "Home键", "End键", "Page Up", "Page Down",
                    "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"
                ])
                
                # 设置当前选中的按键
                key_map = {
                    "enter": 0, "space": 1, "backspace": 2, "delete": 3, "tab": 4, "escape": 5,
                    "up": 6, "down": 7, "left": 8, "right": 9,
                    "home": 10, "end": 11, "pageup": 12, "pagedown": 13,
                    "f1": 14, "f2": 15, "f3": 16, "f4": 17, "f5": 18, "f6": 19,
                    "f7": 20, "f8": 21, "f9": 22, "f10": 23, "f11": 24, "f12": 25
                }
                current_key = block_item.properties.get("key", "enter")
                self.key_combo.setCurrentIndex(key_map.get(current_key, 0))
                self.property_form_layout.addWidget(self.key_combo)
                
                # 按键次数
                presses_label = QLabel("按键次数:")
                self.property_form_layout.addWidget(presses_label)
                
                self.presses_spin = QSpinBox()
                self.presses_spin.setRange(1, 10)
                self.presses_spin.setValue(block_item.properties.get("presses", 1))
                self.property_form_layout.addWidget(self.presses_spin)
                
                # 按键间隔
                interval_label = QLabel("按键间隔(秒):")
                self.property_form_layout.addWidget(interval_label)
                
                self.interval_spin = QDoubleSpinBox()
                self.interval_spin.setRange(0.0, 2.0)
                self.interval_spin.setSingleStep(0.1)
                self.interval_spin.setValue(block_item.properties.get("interval", 0.0))
                self.property_form_layout.addWidget(self.interval_spin)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "mouse_click":
                #                         
                position_label = QLabel("点击位置:")
                self.property_form_layout.addWidget(position_label)
                
                position_layout = QHBoxLayout()
                self.click_x_spin = QSpinBox()
                self.click_x_spin.setRange(0, 2000)
                self.click_x_spin.setValue(block_item.properties.get("x") or 100)
                position_layout.addWidget(QLabel("X:"))
                position_layout.addWidget(self.click_x_spin)
                
                self.click_y_spin = QSpinBox()
                self.click_y_spin.setRange(0, 2000)
                self.click_y_spin.setValue(block_item.properties.get("y") or 100)
                position_layout.addWidget(QLabel("Y:"))
                position_layout.addWidget(self.click_y_spin)
                
                #                                     
                self.quick_select_btn = QPushButton("快速选择位置")
                self.quick_select_btn.clicked.connect(lambda: self.quick_select_click_position(block_item))
                position_layout.addWidget(self.quick_select_btn)
                
                self.property_form_layout.addLayout(position_layout)
                
                #                         
                button_label = QLabel("鼠标按键:")
                self.property_form_layout.addWidget(button_label)
                
                self.button_combo = QComboBox()
                self.button_combo.addItems(["左键点击", "右键点击", "中键点击"])
                button_map = {"left": 0, "right": 1, "middle": 2}
                self.button_combo.setCurrentIndex(button_map.get(block_item.properties.get("button", "left"), 0))
                self.property_form_layout.addWidget(self.button_combo)
                
                #                         
                count_label = QLabel("点击次数:")
                self.property_form_layout.addWidget(count_label)
                
                self.click_count_spin = QSpinBox()
                self.click_count_spin.setRange(1, 10)
                self.click_count_spin.setValue(block_item.properties.get("click_count", 1))
                self.property_form_layout.addWidget(self.click_count_spin)
                
                #                         
                delay_label = QLabel("延迟(秒):")
                self.property_form_layout.addWidget(delay_label)
                
                self.delay_spin = QDoubleSpinBox()
                self.delay_spin.setRange(0.1, 2.0)
                self.delay_spin.setSingleStep(0.1)
                self.delay_spin.setValue(block_item.properties.get("delay", 0.2))
                self.property_form_layout.addWidget(self.delay_spin)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "mouse_drag":
                #                         
                start_label = QLabel("起始位置:")
                self.property_form_layout.addWidget(start_label)
                
                start_layout = QHBoxLayout()
                self.start_x_spin = QSpinBox()
                self.start_x_spin.setRange(0, 2000)
                self.start_x_spin.setValue(block_item.properties.get("start_x", 100))
                start_layout.addWidget(QLabel("X:"))
                start_layout.addWidget(self.start_x_spin)
                
                self.start_y_spin = QSpinBox()
                self.start_y_spin.setRange(0, 2000)
                self.start_y_spin.setValue(block_item.properties.get("start_y", 100))
                start_layout.addWidget(QLabel("Y:"))
                start_layout.addWidget(self.start_y_spin)
                
                self.property_form_layout.addLayout(start_layout)
                
                #                         
                end_label = QLabel("结束位置:")
                self.property_form_layout.addWidget(end_label)
                
                end_layout = QHBoxLayout()
                self.end_x_spin = QSpinBox()
                self.end_x_spin.setRange(0, 2000)
                self.end_x_spin.setValue(block_item.properties.get("end_x", 200))
                end_layout.addWidget(QLabel("X:"))
                end_layout.addWidget(self.end_x_spin)
                
                self.end_y_spin = QSpinBox()
                self.end_y_spin.setRange(0, 2000)
                self.end_y_spin.setValue(block_item.properties.get("end_y", 200))
                end_layout.addWidget(QLabel("Y:"))
                end_layout.addWidget(self.end_y_spin)
                
                self.property_form_layout.addLayout(end_layout)
                
                #                         
                duration_label = QLabel("拖拽时间(秒):")
                self.property_form_layout.addWidget(duration_label)
                
                self.duration_spin = QDoubleSpinBox()
                self.duration_spin.setRange(0.1, 5.0)
                self.duration_spin.setSingleStep(0.1)
                self.duration_spin.setValue(block_item.properties.get("duration", 1.0))
                self.property_form_layout.addWidget(self.duration_spin)
                
                #                                     
                record_btn = QPushButton("快速录制拖拽")
                record_btn.clicked.connect(lambda: self.quick_select_drag_positions(block_item))
                self.property_form_layout.addWidget(record_btn)
                
                #                         
                offset_label = QLabel("偏移范围:")
                self.property_form_layout.addWidget(offset_label)
                
                self.offset_spin = QSpinBox()
                self.offset_spin.setRange(0, 50)
                self.offset_spin.setValue(block_item.properties.get("random_offset", 5))
                self.property_form_layout.addWidget(self.offset_spin)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "find_text":
                #                                                                                                       
                self.quick_screenshot_btn.show()
                
                #                         
                text_label = QLabel("查找文本:")
                self.property_form_layout.addWidget(text_label)
                
                self.text_edit = QLineEdit(block_item.properties.get("text", "                        "))
                self.property_form_layout.addWidget(self.text_edit)
                
                #             
                font_label = QLabel("字体:")
                self.property_form_layout.addWidget(font_label)
                
                self.font_combo = QComboBox()
                self.font_combo.addItems(["Arial", "Microsoft YaHei", "SimSun", "SimHei"])
                self.font_combo.setCurrentText(block_item.properties.get("font", "Arial"))
                self.property_form_layout.addWidget(self.font_combo)
                
                #                         
                size_label = QLabel("字体大小:")
                self.property_form_layout.addWidget(size_label)
                
                self.size_spin = QSpinBox()
                self.size_spin.setRange(8, 72)
                self.size_spin.setValue(block_item.properties.get("size", 14))
                self.property_form_layout.addWidget(self.size_spin)
                
                #                         
                color_label = QLabel("文字颜色:")
                self.property_form_layout.addWidget(color_label)
                
                self.color_edit = QLineEdit(block_item.properties.get("color", "#000000"))
                self.property_form_layout.addWidget(self.color_edit)
                
                threshold_label = QLabel("匹配阈值:")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                                                 
                action_label = QLabel("找到后的动作:")
                self.property_form_layout.addWidget(action_label)
                
                self.action_combo = QComboBox()
                self.action_combo.addItems(["点击", "移动", "忽略"])
                action_map = {"click": 0, "move": 1, "ignore": 2}
                self.action_combo.setCurrentIndex(action_map.get(block_item.properties.get("action", "click"), 0))
                self.property_form_layout.addWidget(self.action_combo)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "find_color":
                # 查找颜色积木属性编辑器
                
                # 颜色选择
                color_label = QLabel("目标颜色:")
                self.property_form_layout.addWidget(color_label)
                
                color_layout = QHBoxLayout()
                self.color_edit = QLineEdit(block_item.properties.get("color", "#FF0000"))
                self.color_edit.setPlaceholderText("#FF0000 或 255,0,0")
                color_layout.addWidget(self.color_edit)
                
                # 颜色选择按钮
                self.color_picker_btn = QPushButton("选择颜色")
                self.color_picker_btn.clicked.connect(lambda: self.pick_color_for_block(block_item))
                color_layout.addWidget(self.color_picker_btn)
                
                color_widget = QWidget()
                color_widget.setLayout(color_layout)
                self.property_form_layout.addWidget(color_widget)
                
                # 颜色预览
                self.color_preview = QLabel()
                self.color_preview.setFixedSize(60, 30)
                self.color_preview.setStyleSheet(f"background-color: {block_item.properties.get('color', '#FF0000')}; border: 1px solid black;")
                self.property_form_layout.addWidget(self.color_preview)
                
                # 更新颜色预览
                self.color_edit.textChanged.connect(lambda text: self.update_color_preview(text))
                
                # 从屏幕取色按钮
                self.screen_color_picker_btn = QPushButton("从屏幕取色")
                self.screen_color_picker_btn.clicked.connect(lambda: self.pick_color_from_screen(block_item))
                self.property_form_layout.addWidget(self.screen_color_picker_btn)
                
                # 颜色容差
                tolerance_label = QLabel("颜色容差 (0-255):")
                self.property_form_layout.addWidget(tolerance_label)
                
                self.tolerance_spin = QSpinBox()
                self.tolerance_spin.setRange(0, 255)
                self.tolerance_spin.setValue(block_item.properties.get("tolerance", 10))
                self.property_form_layout.addWidget(self.tolerance_spin)
                
                # 找到后的动作
                action_label = QLabel("找到后的动作:")
                self.property_form_layout.addWidget(action_label)
                
                self.action_combo = QComboBox()
                self.action_combo.addItems(["点击", "移动", "忽略"])
                action_map = {"click": 0, "move": 1, "ignore": 2}
                self.action_combo.setCurrentIndex(action_map.get(block_item.properties.get("action", "click"), 0))
                self.property_form_layout.addWidget(self.action_combo)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "if":
                # 条件积木类型选择
                if_type_label = QLabel("条件积木类型:")
                self.property_form_layout.addWidget(if_type_label)
                
                self.if_type_combo = QComboBox()
                self.if_type_combo.addItems(["简单条件", "复合条件(多分支判断)"])
                
                # 根据当前属性设置选中项
                current_if_type = block_item.properties.get("if_type", "simple")
                type_index = {"simple": 0, "compound": 1}.get(current_if_type, 0)
                self.if_type_combo.setCurrentIndex(type_index)
                
                # 连接信号，当类型改变时更新界面
                self.if_type_combo.currentIndexChanged.connect(lambda: self.update_if_property_editor(block_item))
                self.property_form_layout.addWidget(self.if_type_combo)
                
                # 简单条件设置
                self.simple_condition_label = QLabel("条件类型:")
                self.property_form_layout.addWidget(self.simple_condition_label)
                
                self.condition_combo = QComboBox()
                self.condition_combo.addItems(["图像存在", "文本存在", "位置存在"])
                condition_map = {"image_found": 0, "text_found": 1, "position_found": 2}
                self.condition_combo.setCurrentIndex(condition_map.get(block_item.properties.get("condition", "image_found"), 0))
                self.property_form_layout.addWidget(self.condition_combo)
                
                # 条件值设置
                self.condition_value_label = QLabel("条件值:")
                self.property_form_layout.addWidget(self.condition_value_label)
                
                self.condition_value_edit = QLineEdit(block_item.properties.get("condition_value", ""))
                self.condition_value_edit.setPlaceholderText("输入条件值（图像路径或文字）")
                self.property_form_layout.addWidget(self.condition_value_edit)
                
                # 匹配阈值
                self.threshold_label = QLabel("匹配阈值:")
                self.property_form_layout.addWidget(self.threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                # 复合条件设置
                self.compound_conditions_label = QLabel("条件分支设置:")
                self.property_form_layout.addWidget(self.compound_conditions_label)
                
                # 条件分支数量
                self.branch_count_label = QLabel("分支数量:")
                self.property_form_layout.addWidget(self.branch_count_label)
                
                self.branch_count_spin = QSpinBox()
                self.branch_count_spin.setRange(2, 5)  # 最多5个分支
                self.branch_count_spin.setValue(block_item.properties.get("branch_count", 2))
                self.branch_count_spin.valueChanged.connect(lambda: self.update_compound_branches(block_item))
                self.property_form_layout.addWidget(self.branch_count_spin)
                
                # 动态创建条件分支编辑器
                self.create_compound_branch_editors(block_item)
                
                # 根据当前if类型更新界面显示
                self.update_if_property_editor(block_item)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "function":
                #                         
                name_label = QLabel("函数名称:")
                self.property_form_layout.addWidget(name_label)
                
                self.name_edit = QLineEdit(block_item.properties.get("name", "my_function"))
                self.property_form_layout.addWidget(self.name_edit)
                
                #                         
                params_label = QLabel("参数列表:")
                self.property_form_layout.addWidget(params_label)
                
                params = block_item.properties.get("params", [])
                params_str = ", ".join(params) if isinstance(params, list) else str(params)
                self.params_edit = QLineEdit(params_str)
                self.property_form_layout.addWidget(self.params_edit)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "wait":
                #                         
                time_label = QLabel("延迟(秒):")
                self.property_form_layout.addWidget(time_label)
                
                self.time_spin = QDoubleSpinBox()
                self.time_spin.setRange(0.1, 60.0)
                self.time_spin.setSingleStep(0.5)
                self.time_spin.setValue(block_item.properties.get("time", 1.0))
                self.property_form_layout.addWidget(self.time_spin)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "delay":
                #                         
                time_label = QLabel("延迟(秒):")
                self.property_form_layout.addWidget(time_label)
                
                self.time_spin = QDoubleSpinBox()
                self.time_spin.setRange(0.1, 60.0)
                self.time_spin.setSingleStep(0.5)
                self.time_spin.setValue(block_item.properties.get("time", 0.5))
                self.property_form_layout.addWidget(self.time_spin)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)

            elif block_type == "jump":
                #                         
                target_label = QLabel("目标积木:")
                self.property_form_layout.addWidget(target_label)
                
                #                                                                                                 
                all_blocks = [item.block_name for item in self.script_scene.items() if isinstance(item, BlockItem) and item != block_item]
                self.target_combo = QComboBox()
                self.target_combo.addItems(all_blocks)
                target_block = block_item.properties.get("target_block", "")
                if target_block and target_block in all_blocks:
                    self.target_combo.setCurrentText(target_block)
                self.property_form_layout.addWidget(self.target_combo)
                
                #                         
                type_label = QLabel("跳转类型:")
                self.property_form_layout.addWidget(type_label)
                
                self.jump_type_combo = QComboBox()
                self.jump_type_combo.addItems(["绝对跳转", "相对跳转"])
                type_map = {"absolute": 0, "relative": 1}
                self.jump_type_combo.setCurrentIndex(type_map.get(block_item.properties.get("jump_type", "absolute"), 0))
                self.property_form_layout.addWidget(self.jump_type_combo)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type in ["and", "or"]:
                # 操作数1标签
                operand1_label = QLabel("操作数1:")
                self.property_form_layout.addWidget(operand1_label)
                
                operand1_layout = QHBoxLayout()
                self.operand1_edit = QLineEdit(block_item.properties.get("operand1", ""))
                operand1_layout.addWidget(self.operand1_edit)
                
                screenshot1_btn = QPushButton("快速截图")
                screenshot1_btn.clicked.connect(lambda: self.quick_screenshot_for_operand(block_item, "operand1"))
                operand1_layout.addWidget(screenshot1_btn)
                
                self.property_form_layout.addLayout(operand1_layout)
                
                # 操作数2标签
                operand2_label = QLabel("操作数2:")
                self.property_form_layout.addWidget(operand2_label)
                
                operand2_layout = QHBoxLayout()
                self.operand2_edit = QLineEdit(block_item.properties.get("operand2", ""))
                operand2_layout.addWidget(self.operand2_edit)
                
                screenshot2_btn = QPushButton("快速截图")
                screenshot2_btn.clicked.connect(lambda: self.quick_screenshot_for_operand(block_item, "operand2"))
                operand2_layout.addWidget(screenshot2_btn)
                
                self.property_form_layout.addLayout(operand2_layout)
                
                # 条件类型标签
                condition_type_label = QLabel("条件类型:")
                self.property_form_layout.addWidget(condition_type_label)
                
                self.condition_type_combo = QComboBox()
                self.condition_type_combo.addItems(["图像条件", "文本条件"])
                type_map = {"image": 0, "text": 1}
                self.condition_type_combo.setCurrentIndex(type_map.get(block_item.properties.get("condition_type", "image"), 0))
                self.property_form_layout.addWidget(self.condition_type_combo)
                
                # 阈值标签
                threshold_label = QLabel("匹配阈值:")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "not":
                # 操作数标签
                operand_label = QLabel("操作数:")
                self.property_form_layout.addWidget(operand_label)
                
                operand_layout = QHBoxLayout()
                self.operand_edit = QLineEdit(block_item.properties.get("operand", ""))
                operand_layout.addWidget(self.operand_edit)
                
                screenshot_btn = QPushButton("快速截图")
                screenshot_btn.clicked.connect(lambda: self.quick_screenshot_for_operand(block_item, "operand"))
                operand_layout.addWidget(screenshot_btn)
                
                self.property_form_layout.addLayout(operand_layout)
                
                # 条件类型标签
                condition_type_label = QLabel("条件类型:")
                self.property_form_layout.addWidget(condition_type_label)
                
                self.condition_type_combo = QComboBox()
                self.condition_type_combo.addItems(["图像条件", "文本条件"])
                type_map = {"image": 0, "text": 1}
                self.condition_type_combo.setCurrentIndex(type_map.get(block_item.properties.get("condition_type", "image"), 0))
                self.property_form_layout.addWidget(self.condition_type_combo)
                
                # 阈值标签
                threshold_label = QLabel("匹配阈值:")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                         
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "run_script":
                # 执行录制脚本积木属性编辑器
                
                # 脚本文件路径
                script_label = QLabel("脚本文件:")
                self.property_form_layout.addWidget(script_label)
                
                script_layout = QHBoxLayout()
                self.script_path_edit = QLineEdit(block_item.properties.get("script_path", ""))
                self.script_path_edit.setPlaceholderText("选择或录制脚本文件")
                script_layout.addWidget(self.script_path_edit)
                
                browse_script_btn = QPushButton("选择")
                browse_script_btn.clicked.connect(lambda: self.browse_script_file(block_item))
                script_layout.addWidget(browse_script_btn)
                
                script_widget = QWidget()
                script_widget.setLayout(script_layout)
                self.property_form_layout.addWidget(script_widget)
                
                # 录制新脚本按钮
                record_script_btn = QPushButton("录制新脚本")
                record_script_btn.setStyleSheet("background-color: #FF6B6B; color: white; font-weight: bold;")
                record_script_btn.clicked.connect(lambda: self.start_script_recording_for_block(block_item))
                self.property_form_layout.addWidget(record_script_btn)
                
                # 播放速度
                speed_label = QLabel("播放速度倍率:")
                self.property_form_layout.addWidget(speed_label)
                
                self.speed_spin = QDoubleSpinBox()
                self.speed_spin.setRange(0.1, 5.0)
                self.speed_spin.setSingleStep(0.1)
                self.speed_spin.setValue(block_item.properties.get("speed", 1.0))
                self.property_form_layout.addWidget(self.speed_spin)
                
                # 循环次数
                repeat_label = QLabel("执行次数:")
                self.property_form_layout.addWidget(repeat_label)
                
                self.repeat_spin = QSpinBox()
                self.repeat_spin.setRange(1, 100)
                self.repeat_spin.setValue(block_item.properties.get("repeat", 1))
                self.property_form_layout.addWidget(self.repeat_spin)
                
                # 提示信息
                tip_label = QLabel("提示: 录制时按ESC停止录制\n播放时Ctrl+Shift+X暂停，Ctrl+Shift+C停止")
                tip_label.setStyleSheet("color: #666; font-size: 10px;")
                self.property_form_layout.addWidget(tip_label)
                
                # 保存按钮
                save_btn = QPushButton("保存属性")
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            else:
                #                                                 
                self.quick_screenshot_btn.hide()
                
                info_label = QLabel("该类型积木暂无可编辑属性")
                info_label.setAlignment(Qt.AlignCenter)
                self.property_form_layout.addWidget(info_label)
        else:
            self.clear_property_editor()
    
    def update_loop_property_editor(self, block_item):
        """根据循环类型更新属性编辑器的显示"""
        if not hasattr(self, 'loop_type_combo'):
            return
            
        loop_type_index = self.loop_type_combo.currentIndex()
        
        # 显示/隐藏循环次数控件
        if hasattr(self, 'count_label') and hasattr(self, 'count_spin'):
            show_count = (loop_type_index == 0)  # 仅计数循环显示
            self.count_label.setVisible(show_count)
            self.count_spin.setVisible(show_count)
        
        # 显示/隐藏条件控件
        show_condition = (loop_type_index == 2)  # 仅条件循环显示
        if hasattr(self, 'condition_label') and hasattr(self, 'condition_combo'):
            self.condition_label.setVisible(show_condition)
            self.condition_combo.setVisible(show_condition)
            
        # 显示/隐藏条件值控件
        if hasattr(self, 'condition_value_label'):
            self.condition_value_label.setVisible(show_condition)
        if hasattr(self, 'condition_value_edit'):
            self.condition_value_edit.setVisible(show_condition)
        if hasattr(self, 'condition_image_widget'):
            self.condition_image_widget.setVisible(show_condition)
        if hasattr(self, 'condition_threshold_label'):
            self.condition_threshold_label.setVisible(show_condition)
        if hasattr(self, 'condition_threshold_spin'):
            self.condition_threshold_spin.setVisible(show_condition)
            
        # 根据条件类型更新条件值编辑器
        if show_condition:
            self.update_condition_value_editor(block_item)
    
    def update_if_property_editor(self, block_item):
        """根据if类型更新属性编辑器的显示"""
        if not hasattr(self, 'if_type_combo'):
            return
            
        if_type_index = self.if_type_combo.currentIndex()
        
        # 显示/隐藏简单条件控件
        show_simple = (if_type_index == 0)  # 简单条件
        if hasattr(self, 'simple_condition_label'):
            self.simple_condition_label.setVisible(show_simple)
        if hasattr(self, 'condition_combo'):
            self.condition_combo.setVisible(show_simple)
        if hasattr(self, 'condition_value_label'):
            self.condition_value_label.setVisible(show_simple)
        if hasattr(self, 'condition_value_edit'):
            self.condition_value_edit.setVisible(show_simple)
        if hasattr(self, 'threshold_label'):
            self.threshold_label.setVisible(show_simple)
        if hasattr(self, 'threshold_spin'):
            self.threshold_spin.setVisible(show_simple)
        
        # 显示/隐藏复合条件控件
        show_compound = (if_type_index == 1)  # 复合条件
        if hasattr(self, 'compound_conditions_label'):
            self.compound_conditions_label.setVisible(show_compound)
        if hasattr(self, 'branch_count_label'):
            self.branch_count_label.setVisible(show_compound)
        if hasattr(self, 'branch_count_spin'):
            self.branch_count_spin.setVisible(show_compound)
        
        # 显示/隐藏分支编辑器
        if hasattr(self, 'branch_editors'):
            for editor in self.branch_editors:
                editor.setVisible(show_compound)
    
    def create_compound_branch_editors(self, block_item):
        """创建复合条件的分支编辑器"""
        if not hasattr(self, 'branch_editors'):
            self.branch_editors = []
        
        # 清除现有的分支编辑器
        for editor in self.branch_editors:
            editor.setParent(None)
        self.branch_editors.clear()
        
        branch_count = getattr(self, 'branch_count_spin', None)
        if branch_count:
            count = branch_count.value()
        else:
            count = block_item.properties.get("branch_count", 2)
        
        branches = block_item.properties.get("branches", [])
        
        for i in range(count):
            # 创建分支容器
            branch_widget = QWidget()
            branch_layout = QVBoxLayout(branch_widget)
            
            # 分支标题
            if i == 0:
                branch_title = QLabel(f"如果 (分支 {i+1}):")
            else:
                branch_title = QLabel(f"条件 {i+1}:")
            
            branch_title.setStyleSheet("font-weight: bold; color: #2196F3;")
            branch_layout.addWidget(branch_title)
            
            # 所有分支都需要条件设置
            # 条件类型
            condition_type_combo = QComboBox()
            condition_type_combo.addItems(["图像存在", "文本存在", "位置存在"])
            branch_layout.addWidget(QLabel("条件类型:"))
            branch_layout.addWidget(condition_type_combo)
            
            # 条件值
            condition_value_edit = QLineEdit()
            condition_value_edit.setPlaceholderText("输入条件值")
            branch_layout.addWidget(QLabel("条件值:"))
            branch_layout.addWidget(condition_value_edit)
            
            # 匹配阈值
            threshold_spin = QDoubleSpinBox()
            threshold_spin.setRange(0.1, 1.0)
            threshold_spin.setSingleStep(0.1)
            threshold_spin.setValue(0.8)
            branch_layout.addWidget(QLabel("匹配阈值:"))
            branch_layout.addWidget(threshold_spin)
            
            # 设置当前值
            if i < len(branches):
                branch_data = branches[i]
                condition_map = {"image_found": 0, "text_found": 1, "position_found": 2}
                condition_type_combo.setCurrentIndex(condition_map.get(branch_data.get("condition", "image_found"), 0))
                condition_value_edit.setText(branch_data.get("condition_value", ""))
                threshold_spin.setValue(branch_data.get("threshold", 0.8))
            
            # 保存控件引用
            setattr(branch_widget, 'condition_type_combo', condition_type_combo)
            setattr(branch_widget, 'condition_value_edit', condition_value_edit)
            setattr(branch_widget, 'threshold_spin', threshold_spin)
            
            # 添加分隔线
            if i < count - 1:
                separator = QLabel("─" * 30)
                separator.setAlignment(Qt.AlignCenter)
                separator.setStyleSheet("color: #CCCCCC;")
                branch_layout.addWidget(separator)
            
            self.branch_editors.append(branch_widget)
            self.property_form_layout.addWidget(branch_widget)
    
    def update_compound_branches(self, block_item):
        """更新复合条件的分支数量"""
        self.create_compound_branch_editors(block_item)
        """根据条件类型更新条件值编辑器的显示"""
        if not hasattr(self, 'condition_combo'):
            return
            
        condition_index = self.condition_combo.currentIndex()
        
        # 显示/隐藏文字输入框
        if hasattr(self, 'condition_value_edit'):
            show_text = (condition_index == 1)  # 找到文字
            self.condition_value_edit.setVisible(show_text)
            if show_text:
                self.condition_value_edit.setPlaceholderText("输入要查找的文字")
        
        # 显示/隐藏图像选择控件
        if hasattr(self, 'condition_image_widget'):
            show_image = (condition_index == 0)  # 找到图像
            self.condition_image_widget.setVisible(show_image)
    
    def clear_property_editor(self):
        """                                          """
        self.block_type_label.setText("积木类型:")
        self.quick_screenshot_btn.hide()
        
        for i in reversed(range(self.property_form_layout.count())): 
            item = self.property_form_layout.itemAt(i)
            if item:
                if item.widget():
                    item.widget().setParent(None)
                elif item.layout():
                    #                                           
                    sub_layout = item.layout()
                    for j in reversed(range(sub_layout.count())):
                        sub_item = sub_layout.itemAt(j)
                        if sub_item.widget():
                            sub_item.widget().setParent(None)
                    self.property_form_layout.removeItem(sub_layout)
                else:
                    self.property_form_layout.removeItem(item)
    
    def browse_image_file(self, block_item):
        """                                    """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "                                    ",
            "",
            "                         (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            block_item.properties["image_path"] = file_path
            self.image_path_edit.setText(file_path)
            self.update_script()
            logger.info(f"                                          : {file_path}")
    
    def quick_select_click_position(self, block_item):
        """快速选择点击位置"""
        from PyQt5.QtCore import Qt, QTimer
        from PyQt5.QtGui import QCursor
        
        try:
            # 暂时隐藏主窗口，露出目标窗口
            if self.parent:
                self.parent.hide()
                logger.info("主窗口已隐藏，等待用户选择位置")
            
            # 延迟一小段时间，确保窗口完全隐藏
            QTimer.singleShot(100, lambda: self._show_position_picker(block_item))
            
        except Exception as e:
            logger.error(f"快速选择位置功能出错: {e}")
            # 确保主窗口可见
            if self.parent:
                self.parent.show()
    
    def _show_position_picker(self, block_item):
        """显示位置选择器"""
        from PyQt5.QtCore import Qt
        
        class PositionPicker(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.setGeometry(self.screen().geometry())
                self.setWindowOpacity(0.1)
                self.setStyleSheet("background-color: black;")
                self.setCursor(Qt.CrossCursor)  # 设置十字光标
                self.selected_position = None
                
            def mousePressEvent(self, event):
                """鼠标点击事件 - 记录点击位置"""
                if event.button() == Qt.LeftButton:
                    self.selected_position = event.globalPos()
                    self.accept()
            
            def keyPressEvent(self, event):
                """键盘事件 - ESC键取消"""
                if event.key() == Qt.Key_Escape:
                    self.reject()
        
        picker = PositionPicker(self)
        picker.setModal(True)
        result = picker.exec_()
        
        # 关闭选择器后，显示主窗口
        if self.parent:
            self.parent.show()
            logger.info("主窗口已恢复显示")
        
        if result == QDialog.Accepted and picker.selected_position:
            # 更新积木属性
            x, y = picker.selected_position.x(), picker.selected_position.y()
            block_item.properties["x"] = x
            block_item.properties["y"] = y
            
            # 更新属性编辑器中的显示
            if hasattr(self, 'click_x_spin'):
                self.click_x_spin.setValue(x)
            if hasattr(self, 'click_y_spin'):
                self.click_y_spin.setValue(y)
            
            self.update_script()
            logger.info(f"已选择点击位置: ({x}, {y})")
        else:
            logger.info("用户取消了位置选择")
    
    def quick_select_move_position(self, block_item):
        """快速选择鼠标移动位置"""
        from PyQt5.QtCore import Qt, QTimer
        
        try:
            # 暂时隐藏主窗口，露出目标窗口
            if self.parent:
                self.parent.hide()
                logger.info("主窗口已隐藏，等待用户选择移动位置")
            
            # 延迟一小段时间，确保窗口完全隐藏
            QTimer.singleShot(100, lambda: self._show_move_position_picker(block_item))
            
        except Exception as e:
            logger.error(f"快速选择移动位置功能出错: {e}")
            # 确保主窗口可见
            if self.parent:
                self.parent.show()
    
    def _show_move_position_picker(self, block_item):
        """显示移动位置选择器"""
        from PyQt5.QtCore import Qt
        
        class PositionPicker(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.setGeometry(self.screen().geometry())
                self.setWindowOpacity(0.1)
                self.setStyleSheet("background-color: black;")
                self.setCursor(Qt.CrossCursor)  # 设置十字光标
                self.selected_position = None
                
            def mousePressEvent(self, event):
                """鼠标点击事件 - 记录点击位置"""
                if event.button() == Qt.LeftButton:
                    self.selected_position = event.globalPos()
                    self.accept()
            
            def keyPressEvent(self, event):
                """键盘事件 - ESC键取消"""
                if event.key() == Qt.Key_Escape:
                    self.reject()
        
        picker = PositionPicker(self)
        picker.setModal(True)
        result = picker.exec_()
        
        # 关闭选择器后，显示主窗口
        if self.parent:
            self.parent.show()
            logger.info("主窗口已恢复显示")
        
        if result == QDialog.Accepted and picker.selected_position:
            # 更新积木属性
            x, y = picker.selected_position.x(), picker.selected_position.y()
            block_item.properties["x"] = x
            block_item.properties["y"] = y
            
            # 更新属性编辑器中的显示
            if hasattr(self, 'x_spin'):
                self.x_spin.setValue(x)
            if hasattr(self, 'y_spin'):
                self.y_spin.setValue(y)
            
            self.update_script()
            logger.info(f"已选择移动位置: ({x}, {y})")
        else:
            logger.info("用户取消了移动位置选择")
    
    def quick_select_drag_positions(self, block_item):
        """快速录制拖拽位置和时长"""
        from PyQt5.QtCore import Qt, QDateTime, QTimer
        from PyQt5.QtGui import QCursor
        
        try:
            # 暂时隐藏主窗口，露出目标窗口
            if self.parent:
                self.parent.hide()
                logger.info("主窗口已隐藏，等待用户录制拖拽操作")
            
            # 延迟一小段时间，确保窗口完全隐藏
            QTimer.singleShot(100, lambda: self._show_drag_recorder(block_item))
            
        except Exception as e:
            logger.error(f"快速录制拖拽功能出错: {e}")
            # 确保主窗口可见
            if self.parent:
                self.parent.show()
    
    def _show_drag_recorder(self, block_item):
        """显示拖拽录制器"""
        from PyQt5.QtCore import Qt, QDateTime
        
        class DragRecorder(QDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.setGeometry(self.screen().geometry())
                self.setWindowOpacity(0.1)
                self.setStyleSheet("background-color: black;")
                self.setCursor(Qt.CrossCursor)  # 设置十字光标
                self.start_position = None
                self.end_position = None
                self.is_recording = False
                self.press_time = None
                self.release_time = None
                
            def mousePressEvent(self, event):
                if event.button() == Qt.LeftButton and not self.is_recording:
                    self.start_position = event.globalPos()
                    self.press_time = QDateTime.currentDateTime()
                    self.is_recording = True
                    logger.debug(f"开始录制拖拽，起始位置: ({self.start_position.x()}, {self.start_position.y()})")
                    
            def mouseReleaseEvent(self, event):
                if event.button() == Qt.LeftButton and self.is_recording:
                    self.end_position = event.globalPos()
                    self.release_time = QDateTime.currentDateTime()
                    logger.debug(f"结束录制拖拽，结束位置: ({self.end_position.x()}, {self.end_position.y()})")
                    self.accept()
            
            def keyPressEvent(self, event):
                """键盘事件 - ESC键取消"""
                if event.key() == Qt.Key_Escape:
                    self.reject()
        
        recorder = DragRecorder(self)
        recorder.setModal(True)
        result = recorder.exec_()
        
        # 关闭录制器后，显示主窗口
        if self.parent:
            self.parent.show()
            logger.info("主窗口已恢复显示")
        
        if result == QDialog.Accepted and recorder.start_position and recorder.end_position:
            # 更新积木属性
            start_x, start_y = recorder.start_position.x(), recorder.start_position.y()
            end_x, end_y = recorder.end_position.x(), recorder.end_position.y()
            
            block_item.properties["start_x"] = start_x
            block_item.properties["start_y"] = start_y
            block_item.properties["end_x"] = end_x
            block_item.properties["end_y"] = end_y
            
            # 计算拖拽持续时间
            duration = 1.0  # 默认值
            if recorder.press_time and recorder.release_time:
                duration = recorder.press_time.msecsTo(recorder.release_time) / 1000.0  # 转换为秒
                block_item.properties["duration"] = duration
                if hasattr(self, 'duration_spin'):
                    self.duration_spin.setValue(duration)
            
            # 更新属性编辑器中的显示
            if hasattr(self, 'start_x_spin'):
                self.start_x_spin.setValue(start_x)
            if hasattr(self, 'start_y_spin'):
                self.start_y_spin.setValue(start_y)
            if hasattr(self, 'end_x_spin'):
                self.end_x_spin.setValue(end_x)
            if hasattr(self, 'end_y_spin'):
                self.end_y_spin.setValue(end_y)
            
            self.update_script()
            logger.info(f"已录制拖拽操作: ({start_x}, {start_y}) -> ({end_x}, {end_y})，持续时间: {duration:.2f}秒")
        else:
            logger.info("用户取消了拖拽录制")
    
    def open_screenshot_tool(self):
        """                                    """
        if self.parent and hasattr(self.parent, 'screenshot_manager'):
            tool = self.parent.screenshot_manager.capture_region(callback=self.on_screenshot_completed)
            logger.info("                                          ")
        else:
            QMessageBox.warning(self, "            ", "                                                ")
    
    def on_screenshot_completed(self, pixmap):
        """                                    """
        temp_dir = tempfile.gettempdir()
        temp_path = os.path.join(temp_dir, f"screenshot_{int(time.time())}.png")
        
        try:
            pixmap.save(temp_path)
            
            #                                                                                     
            if self.selected_block and self.selected_block.block_type == "find_image":
                self.selected_block.properties["image_path"] = temp_path
                
                if hasattr(self, 'image_path_edit'):
                    self.image_path_edit.setText(temp_path)
                
                self.update_script()
                logger.info(f"                                                                ? {temp_path}")
                QMessageBox.information(self, "            ", "                                                                ?")
        except Exception as e:
            logger.error(f"                                    : {e}")
            QMessageBox.critical(self, "            ", f"                                    : {str(e)}")
    
    def save_block_properties(self, block_item):
        block_type = block_item.block_type
        
        if block_type == "start":
            block_item.properties["name"] = self.script_name_edit.text()
            block_item.properties["auto_start"] = self.auto_start_check.isChecked()
            block_item.properties["hotkey"] = self.hotkey_edit.text()
        elif block_type == "broadcast":
            block_item.properties["message"] = self.broadcast_message_edit.text()
            block_item.properties["delay"] = self.broadcast_delay_spin.value()
        elif block_type == "receive":
            block_item.properties["message"] = self.receive_message_edit.text()
            block_item.properties["timeout"] = self.receive_timeout_spin.value()
        elif block_type == "find_image":
            block_item.properties["image_path"] = self.image_path_edit.text()
            block_item.properties["threshold"] = self.threshold_spin.value()
            
            action_map = {0: "click", 1: "move", 2: "ignore"}
            block_item.properties["action"] = action_map[self.action_combo.currentIndex()]
        elif block_type == "loop":
            # 保存循环类型
            loop_type_map = {0: "count", 1: "forever", 2: "until"}
            block_item.properties["loop_type"] = loop_type_map[self.loop_type_combo.currentIndex()]
            
            # 保存循环次数（仅计数循环需要）
            if hasattr(self, 'count_spin'):
                block_item.properties["count"] = self.count_spin.value()
            
            # 保存延迟时间
            if hasattr(self, 'delay_spin'):
                block_item.properties["delay"] = self.delay_spin.value()
            
            # 保存条件设置（仅条件循环需要）
            if hasattr(self, 'condition_combo'):
                condition_map = {0: "image_found", 1: "text_found", 2: "position_found"}
                block_item.properties["condition"] = condition_map[self.condition_combo.currentIndex()]
            
            # 保存条件值
            if hasattr(self, 'condition_value_edit') and self.condition_value_edit.isVisible():
                block_item.properties["condition_value"] = self.condition_value_edit.text()
            elif hasattr(self, 'condition_image_edit') and self.condition_image_edit.isVisible():
                block_item.properties["condition_value"] = self.condition_image_edit.text()
            
            # 保存条件阈值
            if hasattr(self, 'condition_threshold_spin'):
                block_item.properties["threshold"] = self.condition_threshold_spin.value()
        elif block_type == "mouse_move":
            block_item.properties["x"] = self.x_spin.value()
            block_item.properties["y"] = self.y_spin.value()
            block_item.properties["duration"] = self.duration_spin.value()
        elif block_type == "keyboard_input":
            block_item.properties["text"] = self.text_edit.text()
            block_item.properties["delay"] = self.delay_spin.value()
        elif block_type == "keyboard_key":
            # 键盘按键积木属性保存
            key_map = {
                0: "enter", 1: "space", 2: "backspace", 3: "delete", 4: "tab", 5: "escape",
                6: "up", 7: "down", 8: "left", 9: "right",
                10: "home", 11: "end", 12: "pageup", 13: "pagedown",
                14: "f1", 15: "f2", 16: "f3", 17: "f4", 18: "f5", 19: "f6",
                20: "f7", 21: "f8", 22: "f9", 23: "f10", 24: "f11", 25: "f12"
            }
            block_item.properties["key"] = key_map[self.key_combo.currentIndex()]
            block_item.properties["presses"] = self.presses_spin.value()
            block_item.properties["interval"] = self.interval_spin.value()
        elif block_type == "mouse_click":
            button_map = {0: "left", 1: "right", 2: "middle"}
            block_item.properties["button"] = button_map[self.button_combo.currentIndex()]
            block_item.properties["click_count"] = self.click_count_spin.value()
            block_item.properties["delay"] = self.delay_spin.value()
            block_item.properties["x"] = self.click_x_spin.value()
            block_item.properties["y"] = self.click_y_spin.value()
        elif block_type == "mouse_drag":
            block_item.properties["start_x"] = self.start_x_spin.value()
            block_item.properties["start_y"] = self.start_y_spin.value()
            block_item.properties["end_x"] = self.end_x_spin.value()
            block_item.properties["end_y"] = self.end_y_spin.value()
            block_item.properties["duration"] = self.duration_spin.value()
            block_item.properties["random_offset"] = self.offset_spin.value()
        elif block_type == "find_text":
            block_item.properties["text"] = self.text_edit.text()
            block_item.properties["font"] = self.font_combo.currentText()
            block_item.properties["size"] = self.size_spin.value()
            block_item.properties["color"] = self.color_edit.text()
            block_item.properties["threshold"] = self.threshold_spin.value()
            
            action_map = {0: "click", 1: "move", 2: "ignore"}
            block_item.properties["action"] = action_map[self.action_combo.currentIndex()]
        elif block_type == "find_color":
            block_item.properties["color"] = self.color_edit.text()
            block_item.properties["tolerance"] = self.tolerance_spin.value()
            action_map = {0: "click", 1: "move", 2: "ignore"}
            block_item.properties["action"] = action_map[self.action_combo.currentIndex()]
        elif block_type == "if":
            # 保存if类型
            if_type_map = {0: "simple", 1: "compound"}
            block_item.properties["if_type"] = if_type_map[self.if_type_combo.currentIndex()]
            
            if block_item.properties["if_type"] == "simple":
                # 简单条件保存
                condition_map = {0: "image_found", 1: "text_found", 2: "position_found"}
                block_item.properties["condition"] = condition_map[self.condition_combo.currentIndex()]
                block_item.properties["condition_value"] = self.condition_value_edit.text()
                block_item.properties["threshold"] = self.threshold_spin.value()
            else:
                # 复合条件保存
                block_item.properties["branch_count"] = self.branch_count_spin.value()
                branches = []
                
                for i, editor in enumerate(self.branch_editors):
                    if i < self.branch_count_spin.value() - 1:  # 非最后一个分支
                        condition_type_combo = getattr(editor, 'condition_type_combo', None)
                        condition_value_edit = getattr(editor, 'condition_value_edit', None)
                        threshold_spin = getattr(editor, 'threshold_spin', None)
                        
                        if condition_type_combo and condition_value_edit and threshold_spin:
                            condition_map = {0: "image_found", 1: "text_found", 2: "position_found"}
                            branch_data = {
                                "condition": condition_map[condition_type_combo.currentIndex()],
                                "condition_value": condition_value_edit.text(),
                                "threshold": threshold_spin.value()
                            }
                            branches.append(branch_data)
                    else:
                        # 最后一个分支是else，不需要条件
                        branches.append({"condition": "else"})
                
                block_item.properties["branches"] = branches
        elif block_type == "function":
            block_item.properties["name"] = self.name_edit.text()
            params_text = self.params_edit.text()
            block_item.properties["parameters"] = [p.strip() for p in params_text.split(',') if p.strip()]
        elif block_type == "wait":
            block_item.properties["time"] = self.time_spin.value()
        elif block_type == "delay":
            block_item.properties["time"] = self.time_spin.value()

        elif block_type == "jump":
            block_item.properties["target_block"] = self.target_edit.text()
            type_map = {0: "absolute", 1: "relative"}
            block_item.properties["jump_type"] = type_map[self.jump_type_combo.currentIndex()]
        elif block_type == "and":
            block_item.properties["operand1"] = self.operand1_edit.text()
            block_item.properties["operand2"] = self.operand2_edit.text()
        elif block_type == "or":
            block_item.properties["operand1"] = self.operand1_edit.text()
            block_item.properties["operand2"] = self.operand2_edit.text()
        elif block_type == "not":
            block_item.properties["operand"] = self.operand_edit.text()
        elif block_type == "run_script":
            block_item.properties["script_path"] = self.script_path_edit.text()
            block_item.properties["speed"] = self.speed_spin.value()
            block_item.properties["repeat"] = self.repeat_spin.value()
        
        self.update_script()
        logger.info("                                          ")
        QMessageBox.information(self, "            ", "                                          ")
    
    def browse_script_file(self, block_item):
        """浏览并选择脚本文件"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择脚本文件",
            "",
            "脚本文件 (*.json *.py);;JSON文件 (*.json);;Python文件 (*.py);;所有文件 (*.*)"
        )
        
        if file_path:
            self.script_path_edit.setText(file_path)
            # 提取文件名作为脚本名称
            import os
            script_name = os.path.basename(file_path)
            block_item.properties["script_path"] = file_path
            block_item.properties["script_name"] = script_name
            block_item.update()
            self.update_script()
            logger.info(f"已选择脚本文件: {file_path}")
    
    def start_script_recording_for_block(self, block_item):
        """为积木启动脚本录制"""
        from PyQt5.QtWidgets import QMessageBox, QInputDialog
        import os
        
        # 获取脚本名称
        script_name, ok = QInputDialog.getText(
            self,
            "录制新脚本",
            "请输入脚本名称:",
            text="录制脚本_" + str(int(time.time()))
        )
        
        if not ok or not script_name:
            return
        
        # 确保temp目录存在
        temp_dir = "temp"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        
        # 生成脚本文件路径
        script_path = os.path.join(temp_dir, f"{script_name}.json")
        
        # 获取主窗口的脚本录制器
        main_window = self.window()
        if hasattr(main_window, 'script_recorder'):
            recorder = main_window.script_recorder
            
            # 设置录制完成后的回调
            def on_recording_finished():
                # 保存录制的脚本
                if recorder.recorded_actions:
                    import json
                    with open(script_path, 'w', encoding='utf-8') as f:
                        json.dump({
                            "name": script_name,
                            "actions": recorder.recorded_actions
                        }, f, ensure_ascii=False, indent=2)
                    
                    # 更新积木属性
                    self.script_path_edit.setText(script_path)
                    block_item.properties["script_path"] = script_path
                    block_item.properties["script_name"] = script_name
                    block_item.update()
                    self.update_script()
                    
                    QMessageBox.information(self, "录制完成", f"脚本已保存到: {script_path}")
                    logger.info(f"脚本录制完成: {script_path}")
                else:
                    QMessageBox.warning(self, "录制取消", "没有录制到任何操作")
            
            # 连接录制完成信号
            if hasattr(recorder, 'recording_finished'):
                recorder.recording_finished.connect(on_recording_finished)
            
            # 开始录制
            QMessageBox.information(self, "开始录制", "点击确定后开始录制\n按ESC键停止录制")
            recorder.start_recording()
            logger.info("开始录制脚本...")
        else:
            QMessageBox.warning(self, "错误", "脚本录制器未初始化")
            logger.error("脚本录制器未初始化")

    def get_default_properties(self, block_type):
        properties = {}
        
        if block_type == "start":
            properties["name"] = "新脚本"
            properties["auto_start"] = True
            properties["hotkey"] = ""
        elif block_type == "broadcast":
            properties["message"] = "消息1"
            properties["delay"] = 0.0
        elif block_type == "receive":
            properties["message"] = "消息1"
            properties["timeout"] = 30.0
        elif block_type == "loop":
            properties["loop_type"] = "count"  # count, forever, until
            properties["count"] = 10
            properties["delay"] = 0.5
            properties["condition"] = "image_found"  # for until loops
        elif block_type == "if":
            properties["condition"] = "image_found"
            properties["threshold"] = 0.8
        elif block_type == "function":
            properties["name"] = "my_function"
            properties["parameters"] = []
        elif block_type == "wait":
            properties["time"] = 1.0
        elif block_type == "delay":
            properties["time"] = 0.5

        elif block_type == "mouse_move":
            properties["x"] = 100
            properties["y"] = 100
            properties["duration"] = 0.5
            properties["random_offset"] = 5
        elif block_type == "mouse_click":
            properties["button"] = "left"
            properties["click_count"] = 1
            properties["delay"] = 0.2
            properties["x"] = 100
            properties["y"] = 100
        elif block_type == "mouse_drag":
            properties["start_x"] = 100
            properties["start_y"] = 100
            properties["end_x"] = 200
            properties["end_y"] = 200
            properties["duration"] = 1.0
            properties["random_offset"] = 5
        elif block_type == "keyboard_input":
            properties["text"] = "Hello World"
            properties["delay"] = 0.1
        elif block_type == "keyboard_key":
            properties["key"] = "enter"
            properties["presses"] = 1
            properties["interval"] = 0.0
        elif block_type == "find_image":
            properties["image_path"] = ""
            properties["threshold"] = 0.8
            properties["action"] = "click"
        elif block_type == "find_text":
            properties["text"] = "                        "
            properties["font"] = "Arial"
        elif block_type == "find_color":
            properties["color"] = "#FF0000"
            properties["tolerance"] = 10
            properties["action"] = "click"
            properties["size"] = 14
            properties["color"] = "#000000"
            properties["threshold"] = 0.8
            properties["action"] = "click"
        elif block_type == "jump":
            properties["target_block"] = ""
            properties["jump_type"] = "absolute"
        elif block_type == "and":
            properties["operand1"] = "condition1"
            properties["operand2"] = "condition2"
        elif block_type == "or":
            properties["operand1"] = "condition1"
            properties["operand2"] = "condition2"
        elif block_type == "not":
            properties["operand"] = "condition"
        elif block_type == "run_script":
            properties["script_path"] = ""
            properties["script_name"] = "未选择"
            properties["speed"] = 1.0
            properties["repeat"] = 1
        
        return properties
    
    def update_script(self):
        """更新脚本数据，识别积木连接关系和子积木"""
        self.current_script = []
        
        # 首先收集所有积木
        all_blocks = []
        for item in self.script_scene.items():
            if isinstance(item, BlockItem):
                all_blocks.append(item)
        
        # 按照y坐标排序
        all_blocks.sort(key=lambda b: b.pos().y())
        
        # 标记已处理的积木（作为子积木被处理的）
        processed_as_child = set()
        
        for item in all_blocks:
            if item in processed_as_child:
                continue
                
            # 获取子积木列表（对于循环、条件等容器积木）
            child_blocks = []
            
            if item.block_type in ["loop", "if", "function"]:
                logger.info(f"检测容器积木 {item.block_name} 的子积木...")
                
                # 方法1：检查connected_blocks（放入容器内部的积木）
                if hasattr(item, 'connected_blocks') and item.connected_blocks:
                    logger.info(f"  方法1: connected_blocks = {[b.block_name for b in item.connected_blocks]}")
                    for child_item in item.connected_blocks:
                        child_block_data = {
                            "name": child_item.block_name,
                            "type": child_item.block_type,
                            "properties": child_item.properties
                        }
                        child_blocks.append(child_block_data)
                        processed_as_child.add(child_item)
                
                # 方法2：检查connected_from（垂直连接在下方的积木）
                if hasattr(item, 'connected_from') and item.connected_from:
                    child_item = item.connected_from
                    logger.info(f"  方法2: connected_from = {child_item.block_name}")
                    # 只有当子积木不是容器类型时才作为子积木
                    if child_item.block_type not in ["loop", "if", "function", "start"]:
                        if child_item not in processed_as_child:
                            child_block_data = {
                                "name": child_item.block_name,
                                "type": child_item.block_type,
                                "properties": child_item.properties
                            }
                            child_blocks.append(child_block_data)
                            processed_as_child.add(child_item)
                        
                            # 继续收集连接链上的积木
                            current = child_item
                            while hasattr(current, 'connected_from') and current.connected_from:
                                next_item = current.connected_from
                                if next_item.block_type not in ["loop", "if", "function", "start"]:
                                    if next_item not in processed_as_child:
                                        child_block_data = {
                                            "name": next_item.block_name,
                                            "type": next_item.block_type,
                                            "properties": next_item.properties
                                        }
                                        child_blocks.append(child_block_data)
                                        processed_as_child.add(next_item)
                                        current = next_item
                                    else:
                                        break
                                else:
                                    break
                
                # 方法3：基于位置关系识别子积木（始终执行，作为补充检测）
                # 即使方法1和方法2找到了子积木，也检查位置关系以确保不遗漏
                item_rect = item.rect()
                item_bottom = item.pos().y() + item_rect.height()
                item_x = item.pos().x()
                item_width = item_rect.width()
                logger.info(f"  方法3: 位置检测 - 容器底部y={item_bottom}, x={item_x}, width={item_width}")
                
                for other_item in all_blocks:
                    if other_item == item or other_item in processed_as_child:
                        continue
                    
                    other_y = other_item.pos().y()
                    other_x = other_item.pos().x()
                    
                    # 检查是否在循环积木下方且水平位置接近
                    y_distance = other_y - item_bottom
                    x_distance = abs(other_x - item_x)
                    
                    logger.info(f"    检查积木 {other_item.block_name}: y={other_y}, x={other_x}, y_distance={y_distance}, x_distance={x_distance}")
                    
                    # 扩大检测范围：下方100像素内且水平偏移不超过150像素
                    if -10 <= y_distance <= 100 and x_distance <= 150:
                        if other_item.block_type not in ["loop", "if", "function", "start"]:
                            logger.info(f"    ✓ 检测到子积木: {other_item.block_name}")
                            child_block_data = {
                                "name": other_item.block_name,
                                "type": other_item.block_type,
                                "properties": other_item.properties
                            }
                            child_blocks.append(child_block_data)
                            processed_as_child.add(other_item)
                            
                            # 继续收集该子积木下方的积木链
                            current_bottom = other_y + other_item.rect().height()
                            for chain_item in all_blocks:
                                if chain_item == item or chain_item == other_item or chain_item in processed_as_child:
                                    continue
                                chain_y = chain_item.pos().y()
                                chain_x = chain_item.pos().x()
                                chain_y_distance = chain_y - current_bottom
                                chain_x_distance = abs(chain_x - other_x)
                                
                                if -10 <= chain_y_distance <= 50 and chain_x_distance <= 50:
                                    if chain_item.block_type not in ["loop", "if", "function", "start"]:
                                        logger.info(f"    ✓ 检测到链式子积木: {chain_item.block_name}")
                                        chain_block_data = {
                                            "name": chain_item.block_name,
                                            "type": chain_item.block_type,
                                            "properties": chain_item.properties
                                        }
                                        child_blocks.append(chain_block_data)
                                        processed_as_child.add(chain_item)
                                        current_bottom = chain_y + chain_item.rect().height()
                
                logger.info(f"  最终子积木列表: {[cb['name'] for cb in child_blocks]}")
            
            block_data = {
                "name": item.block_name,
                "type": item.block_type,
                "properties": item.properties,
                "position": (item.pos().x(), item.pos().y()),
                "connected_blocks": [block.block_name for block in getattr(item, 'connected_blocks', [])],
                "child_blocks": child_blocks  # 添加子积木数据
            }
            self.current_script.append(block_data)
        
        # 按照积木的垂直位置（y坐标）排序，确保执行顺序与上下位置匹配
        self.current_script.sort(key=lambda block: block["position"][1])
        
        self.script_updated.emit(json.dumps(self.current_script, ensure_ascii=False, indent=2))
    
    def save_script(self, file_path):
        """                        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_script, f, ensure_ascii=False, indent=2)
            logger.info(f"                                    : {file_path}")
            return True
        except Exception as e:
            logger.error(f"                                    : {e}")
            return False
    
    def load_script(self, file_path):
        """                        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.current_script = json.load(f)
            
            self.script_scene.clear()
            
            for block in self.current_script:
                block_item = BlockItem(block["name"], block["type"], block["properties"])
                block_item.setPos(block.get("position", (50, 50)))
                self.script_scene.addItem(block_item)
            
            logger.info(f"                                    : {file_path}")
            return True
        except Exception as e:
            logger.error(f"                                    : {e}")
            return False
    
    def get_script_code(self):
        """                                    """
        return json.dumps(self.current_script, ensure_ascii=False, indent=2)
    
    def parse_code_to_blocks(self, code):
        """将Python代码转换为积木"""
        logger.info(f"正在解析代码到积木: {code[:100]}...")
        
        # 清空当前脚本场景
        if hasattr(self, 'script_scene') and self.script_scene:
            self.script_scene.clear()
        self.current_script = []
        
        # 首先尝试解析blocks_data，这样可以完全恢复所有积木及其属性
        try:
            # 使用更精确的正则表达式匹配blocks_data，支持多行
            blocks_data_pattern = r'blocks_data\s*=\s*(\[[\s\S]*?\n\])'
            blocks_data_match = re.search(blocks_data_pattern, code)
            
            if blocks_data_match:
                blocks_data_str = blocks_data_match.group(1)
                logger.info(f"找到blocks_data，长度: {len(blocks_data_str)}")
                
                # 尝试解析JSON
                try:
                    blocks = json.loads(blocks_data_str)
                    logger.info(f"成功解析blocks_data，包含 {len(blocks)} 个积木")
                    
                    # 验证解析出的数据格式
                    valid_blocks = []
                    for block in blocks:
                        if isinstance(block, dict) and 'name' in block and 'type' in block:
                            # 确保必要的字段存在
                            if 'properties' not in block:
                                block['properties'] = {}
                            if 'position' not in block:
                                block['position'] = (100, 50 + len(valid_blocks) * 60)
                            valid_blocks.append(block)
                        else:
                            logger.warning(f"跳过无效的积木数据: {block}")
                    
                    # 将解析到的积木添加到场景中
                    created_blocks = {}  # 用于存储创建的积木，以便后续建立连接
                    
                    for idx, block in enumerate(valid_blocks):
                        try:
                            block_item = BlockItem(block['name'], block['type'], block['properties'])
                            position = block.get('position', (100, 50))
                            if isinstance(position, (list, tuple)) and len(position) >= 2:
                                block_item.setPos(float(position[0]), float(position[1]))
                            else:
                                block_item.setPos(100, 50 + idx * 60)
                            
                            if hasattr(self, 'script_scene') and self.script_scene:
                                self.script_scene.addItem(block_item)
                            
                            created_blocks[idx] = block_item
                            
                            # 处理子积木（对于循环、条件等容器积木）
                            child_blocks_data = block.get('child_blocks', [])
                            if child_blocks_data and block['type'] in ['loop', 'if', 'function']:
                                logger.info(f"处理容器积木 {block['name']} 的 {len(child_blocks_data)} 个子积木")
                                
                                # 初始化 connected_blocks 列表
                                if not hasattr(block_item, 'connected_blocks'):
                                    block_item.connected_blocks = []
                                
                                # 计算子积木的起始位置（在容器内部）
                                container_x = float(position[0]) if isinstance(position, (list, tuple)) else 100
                                container_y = float(position[1]) if isinstance(position, (list, tuple)) else 50
                                child_start_y = container_y + 50  # 子积木在容器内部偏移
                                
                                for child_idx, child_data in enumerate(child_blocks_data):
                                    try:
                                        child_item = BlockItem(
                                            child_data['name'], 
                                            child_data['type'], 
                                            child_data.get('properties', {})
                                        )
                                        # 子积木位置在容器内部
                                        child_x = container_x + 20
                                        child_y = child_start_y + child_idx * 55
                                        child_item.setPos(child_x, child_y)
                                        
                                        if hasattr(self, 'script_scene') and self.script_scene:
                                            self.script_scene.addItem(child_item)
                                        
                                        # 建立父子关系
                                        block_item.connected_blocks.append(child_item)
                                        child_item.parent_block = block_item
                                        
                                        logger.info(f"  添加子积木: {child_data['name']} 到 {block['name']}")
                                    except Exception as e:
                                        logger.error(f"创建子积木失败: {e}")
                                
                        except Exception as e:
                            logger.error(f"创建积木失败: {e}")
                    
                    # 更新当前脚本
                    self.current_script = valid_blocks
                    logger.info(f"成功从blocks_data加载 {len(valid_blocks)} 个积木")
                    return self.current_script
                    
                except json.JSONDecodeError as e:
                    logger.error(f"JSON解析失败: {e}")
                    logger.error(f"问题数据: {blocks_data_str[:200]}...")
                except Exception as e:
                    logger.error(f"处理blocks_data时发生错误: {e}")
            else:
                logger.warning("未找到blocks_data，将使用代码解析方式")
        except Exception as e:
            logger.error(f"解析blocks_data失败: {e}")
        
        # 如果没有找到blocks_data或解析失败，使用传统的解析方式
        return self._parse_code_traditional(code)
    
    def _parse_code_traditional(self, code):
        """传统的代码解析方式"""
        logger.info("使用传统方式解析代码")
        
        # 按行分割代码
        lines = code.strip().split('\n')
        
        # 存储解析出的积木
        blocks = []
        
        # 解析代码
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # 跳过导入语句和初始化代码
            if (line.startswith("import") or line.startswith("from") or 
                line.startswith("#") or not line or line.startswith("blocks_data")):
                i += 1
                continue
                
            # 解析延时积木
            if line.startswith("time.sleep"):
                try:
                    # 提取延时时间
                    delay_time = float(line.split('(')[1].split(')')[0])
                    block = {
                        'name': '延时',
                        'type': 'delay',
                        'properties': {'time': delay_time},
                        'position': (100, 50 + len(blocks) * 60)
                    }
                    blocks.append(block)
                    
                    # 创建并添加到场景
                    if hasattr(self, 'script_scene') and self.script_scene:
                        block_item = BlockItem(block['name'], block['type'], block['properties'])
                        block_item.setPos(block['position'][0], block['position'][1])
                        self.script_scene.addItem(block_item)
                    
                except Exception as e:
                    logger.error(f"解析延时积木失败: {e}")
                    
            # 解析鼠标移动积木
            elif line.startswith("mouse_controller.move_to"):
                try:
                    # 提取参数
                    params = line.split('(')[1].split(')')[0].split(',')
                    x = int(float(params[0].strip()))
                    y = int(float(params[1].strip()))
                    duration = float(params[2].strip())
                    
                    block = {
                        'name': '鼠标移动',
                        'type': 'mouse_move',
                        'properties': {'x': x, 'y': y, 'duration': duration},
                        'position': (100, 50 + len(blocks) * 60)
                    }
                    blocks.append(block)
                    
                    if hasattr(self, 'script_scene') and self.script_scene:
                        block_item = BlockItem(block['name'], block['type'], block['properties'])
                        block_item.setPos(block['position'][0], block['position'][1])
                        self.script_scene.addItem(block_item)
                    
                except Exception as e:
                    logger.error(f"解析鼠标移动积木失败: {e}")
                    
            # 解析鼠标点击积木
            elif line.startswith("mouse_controller.click"):
                try:
                    # 提取参数
                    params = line.split('(')[1].split(')')[0].split(',')
                    x = int(float(params[0].strip())) if params[0].strip() != 'None' else None
                    y = int(float(params[1].strip())) if params[1].strip() != 'None' else None
                    button = params[2].strip().strip('"').strip("'")
                    click_count = int(float(params[3].strip()))
                    delay = float(params[4].strip())
                    
                    block = {
                        'name': '鼠标点击',
                        'type': 'mouse_click',
                        'properties': {
                            'x': x, 'y': y, 'button': button, 
                            'click_count': click_count, 'delay': delay
                        },
                        'position': (100, 50 + len(blocks) * 60)
                    }
                    blocks.append(block)
                    
                    if hasattr(self, 'script_scene') and self.script_scene:
                        block_item = BlockItem(block['name'], block['type'], block['properties'])
                        block_item.setPos(block['position'][0], block['position'][1])
                        self.script_scene.addItem(block_item)
                    
                except Exception as e:
                    logger.error(f"解析鼠标点击积木失败: {e}")
                    
            # 解析键盘输入积木
            elif line.startswith("keyboard_controller.type_text"):
                try:
                    # 提取参数
                    params = line.split('(')[1].split(')')[0].split(',')
                    text = params[0].strip().strip('"').strip("'")
                    delay = float(params[1].strip())
                    
                    block = {
                        'name': '键盘输入',
                        'type': 'keyboard_input',
                        'properties': {'text': text, 'delay': delay},
                        'position': (100, 50 + len(blocks) * 60)
                    }
                    blocks.append(block)
                    
                    if hasattr(self, 'script_scene') and self.script_scene:
                        block_item = BlockItem(block['name'], block['type'], block['properties'])
                        block_item.setPos(block['position'][0], block['position'][1])
                        self.script_scene.addItem(block_item)
                    
                except Exception as e:
                    logger.error(f"解析键盘输入积木失败: {e}")
                    
            # 解析键盘按键积木
            elif line.startswith("keyboard_controller.press_key"):
                try:
                    # 提取参数
                    params = line.split('(')[1].split(')')[0].split(',')
                    key = params[0].strip().strip('"').strip("'")
                    presses = int(float(params[1].strip())) if len(params) >= 2 else 1
                    interval = float(params[2].strip()) if len(params) >= 3 else 0.0
                    
                    block = {
                        'name': '键盘按键',
                        'type': 'keyboard_key',
                        'properties': {'key': key, 'presses': presses, 'interval': interval},
                        'position': (100, 50 + len(blocks) * 60)
                    }
                    blocks.append(block)
                    
                    if hasattr(self, 'script_scene') and self.script_scene:
                        block_item = BlockItem(block['name'], block['type'], block['properties'])
                        block_item.setPos(block['position'][0], block['position'][1])
                        self.script_scene.addItem(block_item)
                    
                except Exception as e:
                    logger.error(f"解析键盘按键积木失败: {e}")
                    
            # 解析循环积木
            elif line.startswith("for loop_i in range"):
                try:
                    # 提取循环次数
                    count = int(line.split('(')[1].split(')')[0])
                    
                    block = {
                        'name': '循环',
                        'type': 'loop',
                        'properties': {'count': count, 'delay': 0.5},
                        'position': (100, 50 + len(blocks) * 60)
                    }
                    blocks.append(block)
                    
                    if hasattr(self, 'script_scene') and self.script_scene:
                        block_item = BlockItem(block['name'], block['type'], block['properties'])
                        block_item.setPos(block['position'][0], block['position'][1])
                        self.script_scene.addItem(block_item)
                    
                    # 跳过循环体内容
                    i += 1
                    while i < len(lines) and lines[i].strip().startswith("    "):
                        i += 1
                    continue  # 跳过正常的i递增
                    
                except Exception as e:
                    logger.error(f"解析循环积木失败: {e}")
                    
            # 解析逻辑运算积木（与、或、非）
            elif "result_and = condition1 and condition2" in line:
                # 向前查找操作数
                operand1, operand2 = self._extract_logic_operands(lines, i, "and")
                block = {
                    'name': '逻辑与',
                    'type': 'and',
                    'properties': {
                        'operand1': operand1, 'operand2': operand2,
                        'condition_type': 'image', 'threshold': 0.8
                    },
                    'position': (100, 50 + len(blocks) * 60)
                }
                blocks.append(block)
                
                if hasattr(self, 'script_scene') and self.script_scene:
                    block_item = BlockItem(block['name'], block['type'], block['properties'])
                    block_item.setPos(block['position'][0], block['position'][1])
                    self.script_scene.addItem(block_item)
                    
            elif "result_or = condition1 or condition2" in line:
                operand1, operand2 = self._extract_logic_operands(lines, i, "or")
                block = {
                    'name': '逻辑或',
                    'type': 'or',
                    'properties': {
                        'operand1': operand1, 'operand2': operand2,
                        'condition_type': 'image', 'threshold': 0.8
                    },
                    'position': (100, 50 + len(blocks) * 60)
                }
                blocks.append(block)
                
                if hasattr(self, 'script_scene') and self.script_scene:
                    block_item = BlockItem(block['name'], block['type'], block['properties'])
                    block_item.setPos(block['position'][0], block['position'][1])
                    self.script_scene.addItem(block_item)
                    
            elif "result_not = not condition" in line:
                operand = self._extract_not_operand(lines, i)
                block = {
                    'name': '逻辑非',
                    'type': 'not',
                    'properties': {
                        'operand': operand,
                        'condition_type': 'image', 'threshold': 0.8
                    },
                    'position': (100, 50 + len(blocks) * 60)
                }
                blocks.append(block)
                
                if hasattr(self, 'script_scene') and self.script_scene:
                    block_item = BlockItem(block['name'], block['type'], block['properties'])
                    block_item.setPos(block['position'][0], block['position'][1])
                    self.script_scene.addItem(block_item)
            
            i += 1
            
        # 更新当前脚本
        self.current_script = blocks
        logger.info(f"传统方式成功解析 {len(blocks)} 个积木")
        return blocks
    
    def _extract_logic_operands(self, lines, current_line, operation_type):
        """从代码中提取逻辑运算的操作数"""
        operand1, operand2 = "", ""
        
        # 向前查找condition1和condition2的定义
        for i in range(max(0, current_line - 10), current_line):
            line = lines[i].strip()
            if "condition1 = " in line and "find_image" in line:
                match = re.search(r'find_image\("([^"]+)"', line)
                if match:
                    operand1 = match.group(1)
            elif "condition1 = " in line and "find_text" in line:
                match = re.search(r'find_text\("([^"]+)"', line)
                if match:
                    operand1 = match.group(1)
            elif "condition2 = " in line and "find_image" in line:
                match = re.search(r'find_image\("([^"]+)"', line)
                if match:
                    operand2 = match.group(1)
            elif "condition2 = " in line and "find_text" in line:
                match = re.search(r'find_text\("([^"]+)"', line)
                if match:
                    operand2 = match.group(1)
        
        return operand1, operand2
    
    def _extract_not_operand(self, lines, current_line):
        """从代码中提取逻辑非运算的操作数"""
        operand = ""
        
        # 向前查找condition的定义
        for i in range(max(0, current_line - 5), current_line):
            line = lines[i].strip()
            if "condition = " in line and "find_image" in line:
                match = re.search(r'find_image\("([^"]+)"', line)
                if match:
                    operand = match.group(1)
            elif "condition = " in line and "find_text" in line:
                match = re.search(r'find_text\("([^"]+)"', line)
                if match:
                    operand = match.group(1)
        
        return operand
        
    def get_executable_code(self):
        """生成可执行的Python代码"""
        import json
        code = []
        
        # 添加必要的导入语句
        code.append("import time")
        code.append("import random")
        code.append("import json")
        code.append("from modules.image_recognition import ImageRecognition")
        code.append("from modules.mouse_control import MouseControl")
        code.append("from modules.keyboard_control import KeyboardControl")
        code.append("")
        code.append("image_recognizer = ImageRecognition()")
        code.append("mouse_controller = MouseControl()")
        code.append("keyboard_controller = KeyboardControl()")
        code.append("")
        code.append("# 积木数据保存区域")
        code.append("")
        
        # 保存完整的积木数据到代码中，包括位置和连接信息
        blocks_data = []
        for i, block in enumerate(self.current_script):
            # 获取积木在场景中的实际位置
            block_position = (100, 50 + i * 60)  # 默认位置
            
            # 如果积木在场景中，获取其实际位置
            if hasattr(self, 'script_scene') and self.script_scene:
                for item in self.script_scene.items():
                    if (isinstance(item, BlockItem) and 
                        item.block_name == block['name'] and 
                        item.block_type == block['type']):
                        block_position = (item.pos().x(), item.pos().y())
                        break
            
            block_data = {
                'name': block['name'],
                'type': block['type'],
                'properties': block.get('properties', {}),
                'position': block_position
                # 移除连接信息，避免JSON序列化问题
            }
            blocks_data.append(block_data)
        
        # 使用更安全的JSON序列化
        try:
            blocks_json = json.dumps(blocks_data, ensure_ascii=False, indent=4)
            code.append(f"blocks_data = {blocks_json}")
        except Exception as e:
            logger.error(f"JSON序列化失败: {e}")
            # 如果JSON序列化失败，使用简化版本
            code.append("blocks_data = []")
        
        code.append("")
        
        for block in self.current_script:
            if block['type'] == "loop":
                loop_type = block['properties'].get('loop_type', 'count')
                delay = block['properties'].get('delay', 0.5)
                code.append(f"# {block['name']}")
                
                # 获取循环内部的子积木
                child_blocks = block.get('child_blocks', [])
                
                if loop_type == 'count':
                    # 计数循环
                    count = block['properties'].get('count', 10)
                    code.append(f"for loop_i in range({count}):")
                    code.append(f"    print(f'循环第{{loop_i+1}}次执行')")
                    code.append(f"    check_execution_control()  # 检查暂停/停止状态")
                    
                    # 执行子积木
                    if child_blocks:
                        for child_block in child_blocks:
                            child_code = self.generate_single_block_code(child_block, indent="    ")
                            code.extend(child_code)
                    else:
                        code.append(f"    # 循环体为空，添加延迟")
                        code.append(f"    time.sleep({delay})")
                    
                elif loop_type == 'forever':
                    # 永远循环
                    code.append(f"loop_i = 0")
                    code.append(f"while True:")
                    code.append(f"    loop_i += 1")
                    code.append(f"    print(f'永远循环第{{loop_i}}次执行')")
                    code.append(f"    check_execution_control()  # 检查暂停/停止状态")
                    
                    # 执行子积木
                    if child_blocks:
                        for child_block in child_blocks:
                            child_code = self.generate_single_block_code(child_block, indent="    ")
                            code.extend(child_code)
                    else:
                        code.append(f"    # 循环体为空，添加延迟")
                        code.append(f"    time.sleep({delay})")
                    
                elif loop_type == 'until':
                    # 循环到条件满足
                    condition = block['properties'].get('condition', 'image_found')
                    threshold = block['properties'].get('threshold', 0.8)
                    condition_value = block['properties'].get('condition_value', '')
                    
                    code.append(f"loop_i = 0")
                    code.append(f"condition_met = False")
                    code.append(f"while not condition_met:")
                    code.append(f"    loop_i += 1")
                    code.append(f"    print(f'条件循环第{{loop_i}}次执行')")
                    code.append(f"    check_execution_control()  # 检查暂停/停止状态")
                    
                    # 执行子积木
                    if child_blocks:
                        for child_block in child_blocks:
                            child_code = self.generate_single_block_code(child_block, indent="    ")
                            code.extend(child_code)
                    else:
                        code.append(f"    # 循环体为空，添加延迟")
                        code.append(f"    time.sleep({delay})")
                    
                    # 检查条件
                    code.append(f"    ")
                    if condition == 'image_found':
                        code.append(f"    # 检查图像是否出现")
                        if condition_value:
                            code.append(f"    position = image_recognizer.find_image({json.dumps(condition_value)}, {threshold})")
                            code.append(f"    if position:")
                            code.append(f"        print('找到目标图像，循环结束')")
                            code.append(f"        condition_met = True")
                        else:
                            code.append(f"    # 未设置条件图像，循环将永远执行")
                            
                    elif condition == 'text_found':
                        code.append(f"    # 检查文字是否出现")
                        if condition_value:
                            code.append(f"    position = image_recognizer.find_text({json.dumps(condition_value)}, {threshold})")
                            code.append(f"    if position:")
                            code.append(f"        print('找到目标文字，循环结束')")
                            code.append(f"        condition_met = True")
                        else:
                            code.append(f"    # 未设置条件文字，循环将永远执行")
                            
                    elif condition == 'position_found':
                        code.append(f"    # 检查位置是否匹配")
                        code.append(f"    # 这里可以添加位置检查逻辑")
                        code.append(f"    # condition_met = check_position_condition()")
                        
                    code.append(f"    ")
                    code.append(f"    # 防止无限循环的安全机制")
                    code.append(f"    if loop_i > 1000:")
                    code.append(f"        print('循环次数超过1000次，自动停止')")
                    code.append(f"        break")
                        
                code.append("")
                
            elif block['type'] == "delay":
                delay_time = block['properties'].get('time', 0.5)
                code.append(f"# {block['name']}")
                code.append(f"time.sleep({delay_time})")
                code.append("")
                
            elif block['type'] == "mouse_move":
                x = block['properties'].get('x', 100)
                y = block['properties'].get('y', 100)
                duration = block['properties'].get('duration', 0.5)
                random_offset = block['properties'].get('random_offset', 5)
                code.append(f"# {block['name']}")
                code.append(f"mouse_controller.move_to({x}, {y}, {duration})")
                code.append("")
                
            elif block['type'] == "mouse_click":
                button = block['properties'].get('button', 'left')
                click_count = block['properties'].get('click_count', 1)
                delay = block['properties'].get('delay', 0.2)
                x = block['properties'].get('x', None)
                y = block['properties'].get('y', None)
                code.append(f"# {block['name']}")
                if x is not None and y is not None:
                    code.append(f"mouse_controller.click({x}, {y}, {json.dumps(button)}, {click_count}, {delay})")
                else:
                    code.append(f"mouse_controller.click(None, None, {json.dumps(button)}, {click_count}, {delay})")
                code.append("")
                
            elif block['type'] == "keyboard_input":
                text = block['properties'].get('text', 'Hello World')
                delay = block['properties'].get('delay', 0.1)
                code.append(f"# {block['name']}")
                code.append(f"keyboard_controller.type_text({json.dumps(text)}, {delay})")
                code.append("")
                
            elif block['type'] == "keyboard_key":
                key = block['properties'].get('key', 'enter')
                presses = block['properties'].get('presses', 1)
                interval = block['properties'].get('interval', 0.0)
                code.append(f"# {block['name']}")
                code.append(f"keyboard_controller.press_key('{key}', {presses}, {interval})")
                code.append("")
                
            elif block['type'] == "find_image":
                image_path = block['properties'].get('image_path', '')
                threshold = block['properties'].get('threshold', 0.8)
                action = block['properties'].get('action', 'click')
                code.append(f"# {block['name']}")
                if image_path:
                    code.append(f"position = image_recognizer.find_image({json.dumps(image_path)}, {threshold})")
                    code.append(f"if position:")
                    if action == 'click':
                        code.append(f"    mouse_controller.move_to(position[0], position[1], 0.5)")
                        code.append(f"    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
                    code.append(f"else:")
                    code.append(f"    print('                            ?')")
                code.append("")
                
            elif block['type'] == "find_text":
                text = block['properties'].get('text', '查找的文字')
                threshold = block['properties'].get('threshold', 0.8)
                action = block['properties'].get('action', 'click')
                code.append(f"# {block['name']}")
                code.append(f"position = image_recognizer.find_text({json.dumps(text)}, {threshold})")
                code.append(f"if position:")
                if action == 'click':
                    code.append(f"    mouse_controller.move_to(position[0], position[1], 0.5)")
                    code.append(f"    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
                code.append(f"else:")
                code.append(f"    print('未找到指定文字')")
                code.append("")
                
            elif block['type'] == "find_color":
                color = block['properties'].get('color', '#FF0000')
                tolerance = block['properties'].get('tolerance', 10)
                action = block['properties'].get('action', 'click')
                code.append(f"# {block['name']}")
                code.append(f"position = image_recognizer.find_color({json.dumps(color)}, {tolerance})")
                code.append(f"if position:")
                if action == 'click':
                    code.append(f"    mouse_controller.move_to(position[0], position[1], 0.5)")
                    code.append(f"    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
                elif action == 'move':
                    code.append(f"    mouse_controller.move_to(position[0], position[1], 0.5)")
                else:  # action == 'ignore'
                    code.append(f"    print(f'找到颜色 {color}，位置: {{position}}')")
                code.append(f"else:")
                code.append(f"    print('未找到指定颜色')")
                code.append("")
                
            elif block['type'] == "image_match":
                image_path = block['properties'].get('image_path', '')
                threshold = block['properties'].get('threshold', 0.8)
                action = block['properties'].get('action', 'click')
                code.append(f"# {block['name']}")
                if image_path:
                    code.append(f"position = image_recognizer.find_image({json.dumps(image_path)}, {threshold})")
                    code.append(f"if position:")
                    if action == 'click':
                        code.append(f"    mouse_controller.move_to(position[0], position[1], 0.5)")
                        code.append(f"    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
                    elif action == 'move':
                        code.append(f"    mouse_controller.move_to(position[0], position[1], 0.5)")
                    else:  # action == 'ignore' 或其他情况
                        code.append(f"    print('图像匹配成功')")
                    code.append(f"else:")
                    code.append(f"    print('图像匹配失败')")
                else:
                    code.append(f"print('未指定匹配图像')")
                code.append("")
                
            elif block['type'] == "mouse_drag":
                start_x = block['properties'].get('start_x', 100)
                start_y = block['properties'].get('start_y', 100)
                end_x = block['properties'].get('end_x', 200)
                end_y = block['properties'].get('end_y', 200)
                duration = block['properties'].get('duration', 1.0)
                random_offset = block['properties'].get('random_offset', 0)
                code.append(f"# {block['name']}")
                if random_offset > 0:
                    #                                     
                    code.append(f"#                                     ")
                    code.append(f"offset_x1 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"offset_y1 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"offset_x2 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"offset_y2 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"mouse_controller.drag_to({start_x} + offset_x1, {start_y} + offset_y1, {end_x} + offset_x2, {end_y} + offset_y2, {duration})")
                else:
                    code.append(f"mouse_controller.drag_to({start_x}, {start_y}, {end_x}, {end_y}, {duration})")
                code.append("")
                
            elif block['type'] == "if":
                condition = block['properties'].get('condition', 'image_found')
                threshold = block['properties'].get('threshold', 0.8)
                code.append(f"# {block['name']}")
                code.append(f"#                         : {condition}")
                code.append(f"if {condition}:")
                code.append(f"    print('                        ')")
                code.append("")
                
            elif block['type'] == "function":
                function_name = block['properties'].get('name', 'my_function')
                parameters = block['properties'].get('parameters', [])
                params_str = ', '.join(parameters)
                code.append(f"# {block['name']}")
                code.append(f"def {function_name}({params_str}):")
                code.append(f"    print('执行函数 {function_name}')")
                code.append("")
                
            elif block['type'] == "wait":
                wait_time = block['properties'].get('time', 1.0)
                code.append(f"# {block['name']}")
                code.append(f"time.sleep({wait_time})")
                code.append("")
                
            elif block['type'] == "jump":
                target_block = block['properties'].get('target_block', '')
                jump_type = block['properties'].get('jump_type', 'absolute')
                code.append(f"# {block['name']}")
                code.append(f"#                             ? {target_block} (            : {jump_type})")
                import json
                code.append(f"jump_target = {json.dumps(target_block)}")
                code.append(f"jump_type = {json.dumps(jump_type)}")
                code.append("")
                
            elif block['type'] == "and":
                operand1 = block['properties'].get('operand1', '')
                operand2 = block['properties'].get('operand2', '')
                condition_type = block['properties'].get('condition_type', 'image')
                threshold = block['properties'].get('threshold', 0.8)
                code.append(f"# {block['name']}")
                code.append(f"#                             ?             1                ?")
                code.append(f"#                         : {condition_type}")
                import json
                if condition_type == "image":
                    code.append(f"#                       ? -                         ")
                    if operand1:
                        code.append(f"condition1 = image_recognizer.find_image({json.dumps(operand1)}, {threshold}) is not None")
                    else:
                        code.append(f"condition1 = False")
                else:
                    code.append(f"#                       ? -                         ")
                    if operand1:
                        code.append(f"condition1 = image_recognizer.find_text({json.dumps(operand1)}, {threshold}) is not None")
                    else:
                        code.append(f"condition1 = False")
                
                if condition_type == "image":
                    code.append(f"#                       ? -                         ")
                    if operand2:
                        code.append(f"condition2 = image_recognizer.find_image({json.dumps(operand2)}, {threshold}) is not None")
                    else:
                        code.append(f"condition2 = False")
                else:
                    code.append(f"#                       ? -                         ")
                    if operand2:
                        code.append(f"condition2 = image_recognizer.find_text({json.dumps(operand2)}, {threshold}) is not None")
                    else:
                        code.append(f"condition2 = False")
                
                code.append(f"result_and = condition1 and condition2")
                code.append(f"print(f'                            ? {{result_and}}')")
                code.append("")
                
            elif block['type'] == "or":
                operand1 = block['properties'].get('operand1', '')
                operand2 = block['properties'].get('operand2', '')
                condition_type = block['properties'].get('condition_type', 'image')
                threshold = block['properties'].get('threshold', 0.8)
                code.append(f"# {block['name']}")
                code.append(f"#                             ?             1                ?")
                code.append(f"#                         : {condition_type}")
                import json
                if condition_type == "image":
                    code.append(f"#                       ? -                         ")
                    if operand1:
                        code.append(f"condition1 = image_recognizer.find_image({json.dumps(operand1)}, {threshold}) is not None")
                    else:
                        code.append(f"condition1 = False")
                else:
                    code.append(f"#                       ? -                         ")
                    if operand1:
                        code.append(f"condition1 = image_recognizer.find_text({json.dumps(operand1)}, {threshold}) is not None")
                    else:
                        code.append(f"condition1 = False")
                
                if condition_type == "image":
                    code.append(f"#                       ? -                         ")
                    if operand2:
                        code.append(f"condition2 = image_recognizer.find_image({json.dumps(operand2)}, {threshold}) is not None")
                    else:
                        code.append(f"condition2 = False")
                else:
                    code.append(f"#                       ? -                         ")
                    if operand2:
                        code.append(f"condition2 = image_recognizer.find_text({json.dumps(operand2)}, {threshold}) is not None")
                    else:
                        code.append(f"condition2 = False")
                
                code.append(f"result_or = condition1 or condition2")
                code.append(f"print(f'                            ? {{result_or}}')")
                code.append("")
                
            elif block['type'] == "not":
                operand = block['properties'].get('operand', '')
                condition_type = block['properties'].get('condition_type', 'image')
                threshold = block['properties'].get('threshold', 0.8)
                code.append(f"# {block['name']}")
                code.append(f"#                             ?")
                code.append(f"#                         : {condition_type}")
                import json
                if condition_type == "image":
                    code.append(f"#                       ?-                         ")
                    if operand:
                        code.append(f"condition = image_recognizer.find_image({json.dumps(operand)}, {threshold}) is not None")
                    else:
                        code.append(f"condition = False")
                else:
                    code.append(f"#                       ?-                         ")
                    if operand:
                        code.append(f"condition = image_recognizer.find_text({json.dumps(operand)}, {threshold}) is not None")
                    else:
                        code.append(f"condition = False")
                
                code.append(f"result_not = not condition")
                code.append(f"print(f'逻辑非运算结果: {{result_not}}')")
                code.append("")
        
        # 在返回之前，检查并移除重复的blocks_data定义
        code_lines = []
        blocks_data_found = False
        
        for line in code:
            # 跳过重复的blocks_data定义
            if line.strip().startswith('blocks_data = '):
                if not blocks_data_found:
                    # 保留第一个blocks_data定义
                    code_lines.append(line)
                    blocks_data_found = True
                else:
                    # 跳过重复的blocks_data定义
                    continue
            else:
                code_lines.append(line)
        
        return '\n'.join(code_lines)
    
    def generate_single_block_code(self, block, indent=""):
        """生成单个积木的代码"""
        import json
        code = []
        
        if block['type'] == "mouse_move":
            x = block['properties'].get('x', 100)
            y = block['properties'].get('y', 100)
            duration = block['properties'].get('duration', 0.5)
            code.append(f"{indent}# {block['name']}")
            code.append(f"{indent}mouse_controller.move_to({x}, {y}, {duration})")
            
        elif block['type'] == "mouse_click":
            button = block['properties'].get('button', 'left')
            click_count = block['properties'].get('click_count', 1)
            delay = block['properties'].get('delay', 0.2)
            x = block['properties'].get('x', None)
            y = block['properties'].get('y', None)
            code.append(f"{indent}# {block['name']}")
            if x is not None and y is not None:
                code.append(f"{indent}mouse_controller.click({x}, {y}, {json.dumps(button)}, {click_count}, {delay})")
            else:
                code.append(f"{indent}mouse_controller.click(None, None, {json.dumps(button)}, {click_count}, {delay})")
                
        elif block['type'] == "keyboard_input":
            text = block['properties'].get('text', 'Hello World')
            delay = block['properties'].get('delay', 0.1)
            code.append(f"{indent}# {block['name']}")
            code.append(f"{indent}keyboard_controller.type_text({json.dumps(text)}, {delay})")
            
        elif block['type'] == "keyboard_key":
            key = block['properties'].get('key', 'enter')
            presses = block['properties'].get('presses', 1)
            interval = block['properties'].get('interval', 0.0)
            code.append(f"{indent}# {block['name']}")
            code.append(f"{indent}keyboard_controller.press_key('{key}', {presses}, {interval})")
            
        elif block['type'] == "find_image":
            image_path = block['properties'].get('image_path', '')
            threshold = block['properties'].get('threshold', 0.8)
            action = block['properties'].get('action', 'click')
            code.append(f"{indent}# {block['name']}")
            if image_path:
                code.append(f"{indent}position = image_recognizer.find_image({json.dumps(image_path)}, {threshold})")
                code.append(f"{indent}if position:")
                if action == 'click':
                    code.append(f"{indent}    mouse_controller.move_to(position[0], position[1], 0.5)")
                    code.append(f"{indent}    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
                code.append(f"{indent}else:")
                code.append(f"{indent}    print('未找到指定图像')")
                
        elif block['type'] == "find_text":
            text = block['properties'].get('text', '查找的文字')
            threshold = block['properties'].get('threshold', 0.8)
            action = block['properties'].get('action', 'click')
            code.append(f"{indent}# {block['name']}")
            code.append(f"{indent}position = image_recognizer.find_text({json.dumps(text)}, {threshold})")
            code.append(f"{indent}if position:")
            if action == 'click':
                code.append(f"{indent}    mouse_controller.move_to(position[0], position[1], 0.5)")
                code.append(f"{indent}    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
            code.append(f"{indent}else:")
            code.append(f"{indent}    print('未找到指定文字')")
            
        elif block['type'] == "find_color":
            color = block['properties'].get('color', '#FF0000')
            tolerance = block['properties'].get('tolerance', 10)
            action = block['properties'].get('action', 'click')
            code.append(f"{indent}# {block['name']}")
            code.append(f"{indent}position = image_recognizer.find_color({json.dumps(color)}, {tolerance})")
            code.append(f"{indent}if position:")
            if action == 'click':
                code.append(f"{indent}    mouse_controller.move_to(position[0], position[1], 0.5)")
                code.append(f"{indent}    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
            elif action == 'move':
                code.append(f"{indent}    mouse_controller.move_to(position[0], position[1], 0.5)")
            else:
                code.append(f"{indent}    print(f'找到颜色，位置: {{position}}')")
            code.append(f"{indent}else:")
            code.append(f"{indent}    print('未找到指定颜色')")
            
        elif block['type'] == "run_script":
            script_path = block['properties'].get('script_path', '')
            speed = block['properties'].get('speed', 1.0)
            repeat = block['properties'].get('repeat', 1)
            code.append(f"{indent}# {block['name']}")
            if script_path:
                code.append(f"{indent}# 执行录制的脚本")
                code.append(f"{indent}try:")
                code.append(f"{indent}    from src.modules.script_recorder import ScriptPlayer")
                code.append(f"{indent}    import json")
                code.append(f"{indent}    with open({json.dumps(script_path)}, 'r', encoding='utf-8') as f:")
                code.append(f"{indent}        script_data = json.load(f)")
                code.append(f"{indent}    script_actions = script_data.get('actions', script_data)")
                code.append(f"{indent}    player = ScriptPlayer(script_actions)")
                code.append(f"{indent}    player.set_speed({speed})")
                if repeat > 1:
                    code.append(f"{indent}    for _run_i in range({repeat}):")
                    code.append(f"{indent}        print(f'执行脚本第{{_run_i+1}}/{repeat}次')")
                    code.append(f"{indent}        player.start()")
                    code.append(f"{indent}        player.wait()  # 等待脚本执行完成")
                else:
                    code.append(f"{indent}    player.start()")
                    code.append(f"{indent}    player.wait()  # 等待脚本执行完成")
                code.append(f"{indent}except Exception as e:")
                code.append(f"{indent}    print(f'执行脚本失败: {{e}}')")
            else:
                code.append(f"{indent}print('未选择脚本文件')")
            
        elif block['type'] == "wait":
            wait_time = block['properties'].get('time', 1.0)
            code.append(f"{indent}# {block['name']}")
            code.append(f"{indent}time.sleep({wait_time})")
            
        elif block['type'] == "broadcast":
            message = block['properties'].get('message', '消息1')
            delay = block['properties'].get('delay', 0.0)
            code.append(f"{indent}# {block['name']}")
            if delay > 0:
                code.append(f"{indent}time.sleep({delay})")
            code.append(f"{indent}print(f'广播消息: {message}')")
            
        else:
            # 默认处理
            code.append(f"{indent}# {block['name']}")
            code.append(f"{indent}print('执行积木: {block['name']}')")
        
        return code
    
    def update_color_preview(self, color_text):
        """更新颜色预览"""
        try:
            if hasattr(self, 'color_preview'):
                # 验证颜色格式
                color = color_text.strip()
                if color.startswith('#') and len(color) == 7:
                    self.color_preview.setStyleSheet(f"background-color: {color}; border: 1px solid black;")
                elif ',' in color:
                    # RGB格式
                    parts = color.split(',')
                    if len(parts) == 3:
                        r, g, b = int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip())
                        hex_color = f"#{r:02x}{g:02x}{b:02x}"
                        self.color_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid black;")
        except Exception as e:
            logger.debug(f"颜色预览更新失败: {e}")
    
    def pick_color_for_block(self, block_item):
        """打开颜色选择对话框"""
        from PyQt5.QtWidgets import QColorDialog
        
        # 获取当前颜色
        current_color = block_item.properties.get('color', '#FF0000')
        initial_color = QColor(current_color)
        
        color = QColorDialog.getColor(initial_color, self, "选择颜色")
        if color.isValid():
            hex_color = color.name()
            if hasattr(self, 'color_edit'):
                self.color_edit.setText(hex_color)
            if hasattr(self, 'color_preview'):
                self.color_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid black;")
            logger.info(f"选择颜色: {hex_color}")
    
    def pick_color_from_screen(self, block_item):
        """从屏幕取色"""
        try:
            import pyautogui
            from PyQt5.QtWidgets import QInputDialog
            
            # 提示用户
            QMessageBox.information(self, "屏幕取色", 
                "点击确定后，将鼠标移动到目标颜色位置，\n然后按下空格键或等待3秒自动取色。")
            
            # 等待用户移动鼠标
            import time
            time.sleep(0.5)
            
            # 获取鼠标位置的颜色
            x, y = pyautogui.position()
            screenshot = pyautogui.screenshot(region=(x, y, 1, 1))
            pixel = screenshot.getpixel((0, 0))
            
            # 转换为十六进制
            hex_color = f"#{pixel[0]:02x}{pixel[1]:02x}{pixel[2]:02x}"
            
            if hasattr(self, 'color_edit'):
                self.color_edit.setText(hex_color)
            if hasattr(self, 'color_preview'):
                self.color_preview.setStyleSheet(f"background-color: {hex_color}; border: 1px solid black;")
            
            QMessageBox.information(self, "取色成功", 
                f"获取到颜色: {hex_color}\nRGB: ({pixel[0]}, {pixel[1]}, {pixel[2]})")
            
            logger.info(f"从屏幕取色: {hex_color}")
            
        except Exception as e:
            logger.error(f"屏幕取色失败: {e}")
            QMessageBox.warning(self, "取色失败", f"屏幕取色失败: {str(e)}")
    
    def browse_condition_image(self, block_item):
        """浏览选择条件图像文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择条件图像文件",
            "",
            "图像文件 (*.png *.jpg *.jpeg *.bmp)"
        )
        if file_path and hasattr(self, 'condition_image_edit'):
            self.condition_image_edit.setText(file_path)
            logger.info(f"选择条件图像文件: {file_path}")
    
    def screenshot_condition_image(self, block_item):
        """截图选择条件图像"""
        try:
            from modules.screenshot_tool import ScreenshotManager
            screenshot_manager = ScreenshotManager()
            
            def on_screenshot_taken(pixmap):
                # 保存截图到临时文件
                import tempfile
                import os
                temp_dir = tempfile.gettempdir()
                temp_file = os.path.join(temp_dir, f"condition_screenshot_{int(time.time())}.png")
                pixmap.save(temp_file)
                
                if hasattr(self, 'condition_image_edit'):
                    self.condition_image_edit.setText(temp_file)
                    logger.info(f"条件截图保存到: {temp_file}")
            
            screenshot_manager.take_region_screenshot(callback=on_screenshot_taken)
            
        except Exception as e:
            logger.error(f"条件截图失败: {e}")
            QMessageBox.warning(self, "截图失败", f"条件截图失败: {str(e)}")