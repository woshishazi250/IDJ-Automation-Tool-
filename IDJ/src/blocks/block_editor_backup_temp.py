#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
import os
import json
import logging
import time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton,
    QListWidget, QTreeWidget, QTreeWidgetItem, QLabel, QLineEdit,
    QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QFileDialog,
    QMessageBox, QScrollArea, QTabWidget, QGraphicsView, QGraphicsScene,
    QGraphicsRectItem, QGraphicsTextItem, QGraphicsItem
)
from PyQt5.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt5.QtGui import QFont, QColor, QPen, QBrush, QCursor

logger = logging.getLogger(__name__)

class BlockItem(QGraphicsRectItem):
    
    
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
        self.connected_blocks = []
        self.connected_to = None  #                                         ?        self.connected_from = None  #                                         ?    
    def paint(self, painter, option, widget):
                                                                                                                                                                                                                                                                                                                                                                                                                           -                                                                                                                          -                                                                                                                                     Connect to another block                                              ?""
        #                                                                             ?        if hasattr(self, 'top_connection'):
            self.top_connection.setBrush(QBrush(Qt.green))
            self.top_connection.setPen(QPen(Qt.darkGreen, 2))
            
        if hasattr(self, 'bottom_connection'):
            self.bottom_connection.setBrush(QBrush(Qt.green))
            self.bottom_connection.setPen(QPen(Qt.darkGreen, 2))
            
        if hasattr(self, 'input_connection'):
            self.input_connection.setBrush(QBrush(Qt.green))
            self.input_connection.setPen(QPen(Qt.darkGreen, 1))
        
    def disconnect_from(self, other_block):
        
        #                                                                               
        if other_block.block_type in ["loop", "if", "function"] and self in other_block.connected_blocks:
            #                                           
            other_block.connected_blocks.remove(self)
            self.connected_to = None
            logger.info(f"             {self.block_name}     ?{other_block.block_name}                 ?)
        elif self.connected_to == other_block:
            #                                                                                               ?            self.connected_to.connected_from = None
            self.connected_to = None
        elif self.connected_from == other_block:
            #                                                                                               ?            self.connected_from.connected_to = None
            self.connected_from = None
            
        self.is_connected = self.connected_to is not None or self.connected_from is not None or len(getattr(self, 'connected_blocks', [])) > 0
        other_block.is_connected = other_block.connected_to is not None or other_block.connected_from is not None or len(other_block.connected_blocks) > 0
        
        #                                         ?        self.reset_connection_colors()
        other_block.reset_connection_colors()
        
    def reset_connection_colors(self):
                          TreeWidget                                                                                                          ?""
        selected_items = self.selectedItems()
        if selected_items and len(selected_items) == 1:
            item = selected_items[0]
            if item.parent():  #                                                                 ?                block_name = item.text(0)
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
                                                                                                        ?""
        if item.parent():  #                                     
            block_name = item.text(0)
            block_type = item.text(1)
            
            #                                         ?            properties = self.get_default_properties(block_type)
            block_item = BlockItem(block_name, block_type, properties)
            
            #                                                                                         ?            existing_blocks = [obj for obj in self.script_scene.items() if isinstance(obj, BlockItem)]
            
            if existing_blocks:
                #                                                                                                                       ?                max_y = max(block.pos().y() + block.rect().height() for block in existing_blocks)
                y_position = max_y + 40  #             40            
            else:
                #                                                                                   ?                y_position = 50
                
            block_item.setPos(50, y_position)
            
            #                                                                   
            self.script_scene.on_block_selected = self.on_block_selected
            
            self.script_scene.addItem(block_item)
            
            #                                                                                                                                     
            #                                                                                                                 ?            logger.info(f"                        : {block_name} (            : ({block_item.pos().x():.1f}, {block_item.pos().y():.1f}))")
            
            self.update_script()
    
    def add_selected_block(self):
                                                ?""
        if self.selected_block:
            block_name = self.selected_block.block_name
            self.script_scene.removeItem(self.selected_block)
            del self.selected_block
            self.selected_block = None
            self.update_script()
            self.clear_property_editor()
            logger.info(f"                        : {block_name}")
    
    def clear_script(self):
        
        self.script_scene.clear()
        self.current_script = []
        self.script_updated.emit("")
        self.clear_property_editor()
        logger.info("                            ?)
    
    def on_block_selected(self, block_item):
        
        self.selected_block = block_item
        self.update_property_editor(block_item)
    
    def update_property_editor(self, block_item):
        
        if block_item:
            self.block_type_label.setText(f"                        : {block_item.block_name}")
            
            #                                   ?-                                                                                   ?            for i in reversed(range(self.property_form_layout.count())): 
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
            
            #                                                           ?            block_type = block_item.block_type
            
            if block_type == "find_image":
                #                                               ?                self.quick_screenshot_btn.show()
                
                #                                     
                image_label = QLabel("                        :")
                self.property_form_layout.addWidget(image_label)
                
                image_layout = QHBoxLayout()
                self.image_path_edit = QLineEdit(block_item.properties.get("image_path", ""))
                image_layout.addWidget(self.image_path_edit)
                
                browse_btn = QPushButton("            ")
                browse_btn.clicked.connect(lambda: self.browse_image_file(block_item))
                image_layout.addWidget(browse_btn)
                
                self.property_form_layout.addLayout(image_layout)
                
                #                             ?                threshold_label = QLabel("                            ?")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                                                 
                action_label = QLabel("                            ?")
                self.property_form_layout.addWidget(action_label)
                
                self.action_combo = QComboBox()
                self.action_combo.addItems(["            ", "            ", "            "])
                action_map = {"click": 0, "move": 1, "ignore": 2}
                self.action_combo.setCurrentIndex(action_map.get(block_item.properties.get("action", "click"), 0))
                self.property_form_layout.addWidget(self.action_combo)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "loop":
                #                         
                count_label = QLabel("                        :")
                self.property_form_layout.addWidget(count_label)
                
                self.count_spin = QSpinBox()
                self.count_spin.setRange(1, 1000)
                self.count_spin.setValue(block_item.properties.get("count", 10))
                self.property_form_layout.addWidget(self.count_spin)
                
                #                         
                delay_label = QLabel("                         (    ?:")
                self.property_form_layout.addWidget(delay_label)
                
                self.delay_spin = QDoubleSpinBox()
                self.delay_spin.setRange(0.1, 10.0)
                self.delay_spin.setSingleStep(0.1)
                self.delay_spin.setValue(block_item.properties.get("delay", 0.5))
                self.property_form_layout.addWidget(self.delay_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "mouse_move":
                # X            
                x_label = QLabel("X            :")
                self.property_form_layout.addWidget(x_label)
                
                self.x_spin = QSpinBox()
                self.x_spin.setRange(0, 2000)
                self.x_spin.setValue(block_item.properties.get("x", 100))
                self.property_form_layout.addWidget(self.x_spin)
                
                # Y            
                y_label = QLabel("Y            :")
                self.property_form_layout.addWidget(y_label)
                
                self.y_spin = QSpinBox()
                self.y_spin.setRange(0, 2000)
                self.y_spin.setValue(block_item.properties.get("y", 100))
                self.property_form_layout.addWidget(self.y_spin)
                
                #                         
                duration_label = QLabel("                         (    ?:")
                self.property_form_layout.addWidget(duration_label)
                
                self.duration_spin = QDoubleSpinBox()
                self.duration_spin.setRange(0.1, 5.0)
                self.duration_spin.setSingleStep(0.1)
                self.duration_spin.setValue(block_item.properties.get("duration", 0.5))
                self.property_form_layout.addWidget(self.duration_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "keyboard_input":
                #                         
                text_label = QLabel("                        :")
                self.property_form_layout.addWidget(text_label)
                
                self.text_edit = QLineEdit(block_item.properties.get("text", "Hello World"))
                self.property_form_layout.addWidget(self.text_edit)
                
                #                         
                delay_label = QLabel("                         (    ?:")
                self.property_form_layout.addWidget(delay_label)
                
                self.delay_spin = QDoubleSpinBox()
                self.delay_spin.setRange(0.01, 2.0)
                self.delay_spin.setSingleStep(0.05)
                self.delay_spin.setValue(block_item.properties.get("delay", 0.1))
                self.property_form_layout.addWidget(self.delay_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "mouse_click":
                #                         
                position_label = QLabel("                        :")
                self.property_form_layout.addWidget(position_label)
                
                position_layout = QHBoxLayout()
                self.click_x_spin = QSpinBox()
                self.click_x_spin.setRange(0, 2000)
                self.click_x_spin.setValue(block_item.properties.get("x", 100))
                position_layout.addWidget(QLabel("X:"))
                position_layout.addWidget(self.click_x_spin)
                
                self.click_y_spin = QSpinBox()
                self.click_y_spin.setRange(0, 2000)
                self.click_y_spin.setValue(block_item.properties.get("y", 100))
                position_layout.addWidget(QLabel("Y:"))
                position_layout.addWidget(self.click_y_spin)
                
                #                                     
                self.quick_select_btn = QPushButton("                        ")
                self.quick_select_btn.clicked.connect(lambda: self.quick_select_click_position(block_item))
                position_layout.addWidget(self.quick_select_btn)
                
                self.property_form_layout.addLayout(position_layout)
                
                #                         
                button_label = QLabel("                        :")
                self.property_form_layout.addWidget(button_label)
                
                self.button_combo = QComboBox()
                self.button_combo.addItems(["            ", "            ", "            "])
                button_map = {"left": 0, "right": 1, "middle": 2}
                self.button_combo.setCurrentIndex(button_map.get(block_item.properties.get("button", "left"), 0))
                self.property_form_layout.addWidget(self.button_combo)
                
                #                         
                count_label = QLabel("                        :")
                self.property_form_layout.addWidget(count_label)
                
                self.click_count_spin = QSpinBox()
                self.click_count_spin.setRange(1, 10)
                self.click_count_spin.setValue(block_item.properties.get("click_count", 1))
                self.property_form_layout.addWidget(self.click_count_spin)
                
                #                         
                delay_label = QLabel("                         (    ?:")
                self.property_form_layout.addWidget(delay_label)
                
                self.delay_spin = QDoubleSpinBox()
                self.delay_spin.setRange(0.1, 2.0)
                self.delay_spin.setSingleStep(0.1)
                self.delay_spin.setValue(block_item.properties.get("delay", 0.2))
                self.property_form_layout.addWidget(self.delay_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "mouse_drag":
                #                         
                start_label = QLabel("                        :")
                self.property_form_layout.addWidget(start_label)
                
                start_layout = QHBoxLayout()
                self.start_x_spin = QSpinBox()
                self.start_x_spin.setRange(0, 2000)
                self.start_x_spin.setValue(block_item.properties.get("start_x", 100))
                start_layout.addWidget(self.start_x_spin)
                
                self.start_y_spin = QSpinBox()
                self.start_y_spin.setRange(0, 2000)
                self.start_y_spin.setValue(block_item.properties.get("start_y", 100))
                start_layout.addWidget(self.start_y_spin)
                
                self.property_form_layout.addLayout(start_layout)
                
                #                         
                end_label = QLabel("                        :")
                self.property_form_layout.addWidget(end_label)
                
                end_layout = QHBoxLayout()
                self.end_x_spin = QSpinBox()
                self.end_x_spin.setRange(0, 2000)
                self.end_x_spin.setValue(block_item.properties.get("end_x", 200))
                end_layout.addWidget(self.end_x_spin)
                
                self.end_y_spin = QSpinBox()
                self.end_y_spin.setRange(0, 2000)
                self.end_y_spin.setValue(block_item.properties.get("end_y", 200))
                end_layout.addWidget(self.end_y_spin)
                
                self.property_form_layout.addLayout(end_layout)
                
                #                         
                duration_label = QLabel("                         (    ?:")
                self.property_form_layout.addWidget(duration_label)
                
                self.duration_spin = QDoubleSpinBox()
                self.duration_spin.setRange(0.1, 5.0)
                self.duration_spin.setSingleStep(0.1)
                self.duration_spin.setValue(block_item.properties.get("duration", 1.0))
                self.property_form_layout.addWidget(self.duration_spin)
                
                #                                     
                record_btn = QPushButton("                        ")
                record_btn.clicked.connect(lambda: self.quick_select_drag_positions(block_item))
                self.property_form_layout.addWidget(record_btn)
                
                #                         
                offset_label = QLabel("                         (            ):")
                self.property_form_layout.addWidget(offset_label)
                
                self.offset_spin = QSpinBox()
                self.offset_spin.setRange(0, 50)
                self.offset_spin.setValue(block_item.properties.get("random_offset", 5))
                self.property_form_layout.addWidget(self.offset_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "find_text":
                #                                                                                                       
                self.quick_screenshot_btn.show()
                
                #                         
                text_label = QLabel("                        :")
                self.property_form_layout.addWidget(text_label)
                
                self.text_edit = QLineEdit(block_item.properties.get("text", "                        "))
                self.property_form_layout.addWidget(self.text_edit)
                
                #             
                font_label = QLabel("            :")
                self.property_form_layout.addWidget(font_label)
                
                self.font_combo = QComboBox()
                self.font_combo.addItems(["Arial", "Microsoft YaHei", "SimSun", "SimHei"])
                self.font_combo.setCurrentText(block_item.properties.get("font", "Arial"))
                self.property_form_layout.addWidget(self.font_combo)
                
                #                         
                size_label = QLabel("                        :")
                self.property_form_layout.addWidget(size_label)
                
                self.size_spin = QSpinBox()
                self.size_spin.setRange(8, 72)
                self.size_spin.setValue(block_item.properties.get("size", 14))
                self.property_form_layout.addWidget(self.size_spin)
                
                #                         
                color_label = QLabel("                        :")
                self.property_form_layout.addWidget(color_label)
                
                self.color_edit = QLineEdit(block_item.properties.get("color", "#000000"))
                self.property_form_layout.addWidget(self.color_edit)
                
                #                             ?                threshold_label = QLabel("                            ?")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                                                 
                action_label = QLabel("                            ?")
                self.property_form_layout.addWidget(action_label)
                
                self.action_combo = QComboBox()
                self.action_combo.addItems(["            ", "            ", "            "])
                action_map = {"click": 0, "move": 1, "ignore": 2}
                self.action_combo.setCurrentIndex(action_map.get(block_item.properties.get("action", "click"), 0))
                self.property_form_layout.addWidget(self.action_combo)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "if":
                #                         
                condition_label = QLabel("                        :")
                self.property_form_layout.addWidget(condition_label)
                
                self.condition_combo = QComboBox()
                self.condition_combo.addItems(["                        ", "                        ", "                        "])
                condition_map = {"image_found": 0, "text_found": 1, "position_found": 2}
                self.condition_combo.setCurrentIndex(condition_map.get(block_item.properties.get("condition", "image_found"), 0))
                self.property_form_layout.addWidget(self.condition_combo)
                
                #                             ?                threshold_label = QLabel("                            ?")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "function":
                #                         
                name_label = QLabel("                        :")
                self.property_form_layout.addWidget(name_label)
                
                self.name_edit = QLineEdit(block_item.properties.get("name", "my_function"))
                self.property_form_layout.addWidget(self.name_edit)
                
                #                         
                params_label = QLabel("                         (                        ):")
                self.property_form_layout.addWidget(params_label)
                
                #                                                                                                                       ?                params = block_item.properties.get("parameters", [])
                params_str = ", ".join(params) if isinstance(params, list) else str(params)
                self.params_edit = QLineEdit(params_str)
                self.property_form_layout.addWidget(self.params_edit)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "wait":
                #                         
                time_label = QLabel("                         (    ?:")
                self.property_form_layout.addWidget(time_label)
                
                self.time_spin = QDoubleSpinBox()
                self.time_spin.setRange(0.1, 60.0)
                self.time_spin.setSingleStep(0.5)
                self.time_spin.setValue(block_item.properties.get("time", 1.0))
                self.property_form_layout.addWidget(self.time_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "delay":
                #                         
                time_label = QLabel("                         (    ?:")
                self.property_form_layout.addWidget(time_label)
                
                self.time_spin = QDoubleSpinBox()
                self.time_spin.setRange(0.1, 60.0)
                self.time_spin.setSingleStep(0.5)
                self.time_spin.setValue(block_item.properties.get("time", 0.5))
                self.property_form_layout.addWidget(self.time_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)

            elif block_type == "jump":
                #                         
                target_label = QLabel("                        :")
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
                type_label = QLabel("                        :")
                self.property_form_layout.addWidget(type_label)
                
                self.jump_type_combo = QComboBox()
                self.jump_type_combo.addItems(["                        ", "                        "])
                type_map = {"absolute": 0, "relative": 1}
                self.jump_type_combo.setCurrentIndex(type_map.get(block_item.properties.get("jump_type", "absolute"), 0))
                self.property_form_layout.addWidget(self.jump_type_combo)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type in ["and", "or"]:
                #                                               ?                self.quick_screenshot_btn.show()
                
                #                 ? -                                                     ?                operand1_label = QLabel("            1:")
                self.property_form_layout.addWidget(operand1_label)
                
                operand1_layout = QHBoxLayout()
                self.operand1_edit = QLineEdit(block_item.properties.get("operand1", ""))
                operand1_layout.addWidget(self.operand1_edit)
                
                #                                               ?                screenshot1_btn = QPushButton("                      ?)
                screenshot1_btn.clicked.connect(lambda: self.quick_screenshot_for_operand(block_item, "operand1"))
                operand1_layout.addWidget(screenshot1_btn)
                
                self.property_form_layout.addLayout(operand1_layout)
                
                #                 ? -                                                     ?                operand2_label = QLabel("            2:")
                self.property_form_layout.addWidget(operand2_label)
                
                operand2_layout = QHBoxLayout()
                self.operand2_edit = QLineEdit(block_item.properties.get("operand2", ""))
                operand2_layout.addWidget(self.operand2_edit)
                
                screenshot2_btn = QPushButton("                      ?)
                screenshot2_btn.clicked.connect(lambda: self.quick_screenshot_for_operand(block_item, "operand2"))
                operand2_layout.addWidget(screenshot2_btn)
                
                self.property_form_layout.addLayout(operand2_layout)
                
                #                          -                             ?                condition_type_label = QLabel("                        :")
                self.property_form_layout.addWidget(condition_type_label)
                
                self.condition_type_combo = QComboBox()
                self.condition_type_combo.addItems(["                        ", "                        "])
                type_map = {"image": 0, "text": 1}
                self.condition_type_combo.setCurrentIndex(type_map.get(block_item.properties.get("condition_type", "image"), 0))
                self.property_form_layout.addWidget(self.condition_type_combo)
                
                #                             ?                threshold_label = QLabel("                            ?")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            elif block_type == "not":
                #                                               ?                self.quick_screenshot_btn.show()
                
                #                 ?-                                                     ?                operand_label = QLabel("            :")
                self.property_form_layout.addWidget(operand_label)
                
                operand_layout = QHBoxLayout()
                self.operand_edit = QLineEdit(block_item.properties.get("operand", ""))
                operand_layout.addWidget(self.operand_edit)
                
                screenshot_btn = QPushButton("                      ?)
                screenshot_btn.clicked.connect(lambda: self.quick_screenshot_for_operand(block_item, "operand"))
                operand_layout.addWidget(screenshot_btn)
                
                self.property_form_layout.addLayout(operand_layout)
                
                #                          -                             ?                condition_type_label = QLabel("                        :")
                self.property_form_layout.addWidget(condition_type_label)
                
                self.condition_type_combo = QComboBox()
                self.condition_type_combo.addItems(["                        ", "                        "])
                type_map = {"image": 0, "text": 1}
                self.condition_type_combo.setCurrentIndex(type_map.get(block_item.properties.get("condition_type", "image"), 0))
                self.property_form_layout.addWidget(self.condition_type_combo)
                
                #                             ?                threshold_label = QLabel("                            ?")
                self.property_form_layout.addWidget(threshold_label)
                
                self.threshold_spin = QDoubleSpinBox()
                self.threshold_spin.setRange(0.1, 1.0)
                self.threshold_spin.setSingleStep(0.1)
                self.threshold_spin.setValue(block_item.properties.get("threshold", 0.8))
                self.property_form_layout.addWidget(self.threshold_spin)
                
                #                         
                save_btn = QPushButton("                      ?)
                save_btn.clicked.connect(lambda: self.save_block_properties(block_item))
                self.property_form_layout.addWidget(save_btn)
            else:
                #                                                 
                self.quick_screenshot_btn.hide()
                
                #                                   ?                info_label = QLabel("                                                                      ?)
                info_label.setAlignment(Qt.AlignCenter)
                self.property_form_layout.addWidget(info_label)
        else:
            self.clear_property_editor()
    
    def clear_property_editor(self):
        
        self.block_type_label.setText("                        :")
        self.quick_screenshot_btn.hide()
        
        #                                               ?-                         
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
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "                                    ",
            "",
            "                         (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            #                                                     ?            file_path = os.path.abspath(file_path)
            block_item.properties["image_path"] = file_path
            
            #              image_path_edit                                         ?            if hasattr(self, 'image_path_edit'):
                self.image_path_edit.setText(file_path)
            
            self.update_script()
            logger.info(f"                                          : {file_path}")
    
    def quick_select_click_position(self, block_item):
        
        #                                                                                         ?        from PyQt5.QtWidgets import QDialog
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QCursor
        
        class PositionPicker(QDialog):
                                                 -                                                                                                                                                                 ?""
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
                self.setGeometry(self.screen().geometry())
                self.setWindowOpacity(0.1)
                self.setStyleSheet("background-color: black;")
                self.start_position = None
                self.end_position = None
                self.is_recording = False
                self.press_time = None
                self.release_time = None
                
            def mousePressEvent(self, event):
                                                     -                                                     ?""
                if event.button() == Qt.LeftButton and self.is_recording:
                    self.end_position = event.globalPos()
                    self.release_time = QDateTime.currentDateTime()
                    self.accept()
        
        #                                         ?        recorder = DragRecorder(self)
        recorder.setModal(True)
        result = recorder.exec_()
        
        if result == QDialog.Accepted and recorder.start_position and recorder.end_position:
            #                         
            start_x, start_y = recorder.start_position.x(), recorder.start_position.y()
            end_x, end_y = recorder.end_position.x(), recorder.end_position.y()
            
            block_item.properties["start_x"] = start_x
            block_item.properties["start_y"] = start_y
            block_item.properties["end_x"] = end_x
            block_item.properties["end_y"] = end_y
            
            #                                                                         
            if recorder.press_time and recorder.release_time:
                duration = recorder.press_time.msecsTo(recorder.release_time) / 1000.0  #                         
                block_item.properties["duration"] = duration
                if hasattr(self, 'duration_spin'):
                    self.duration_spin.setValue(duration)
            
            #                                           
            if hasattr(self, 'start_x_spin'):
                self.start_x_spin.setValue(start_x)
            if hasattr(self, 'start_y_spin'):
                self.start_y_spin.setValue(start_y)
            if hasattr(self, 'end_x_spin'):
                self.end_x_spin.setValue(end_x)
            if hasattr(self, 'end_y_spin'):
                self.end_y_spin.setValue(end_y)
            
            self.update_script()
            logger.info(f"                                                : ({start_x}, {start_y}) -> ({end_x}, {end_y})                            ? {duration:.2f}    ?)
    
    def open_screenshot_tool(self):
        
        if self.parent and hasattr(self.parent, 'screenshot_manager'):
            tool = self.parent.screenshot_manager.capture_region(callback=self.on_screenshot_completed)
            logger.info("                                          ")
        else:
            QMessageBox.warning(self, "            ", "                                                ")
    
    def on_screenshot_completed(self, pixmap):
        
        #                                                     ?        import tempfile
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
                QMessageBox.information(self, "            ", "                                                                ?)
        except Exception as e:
            logger.error(f"                                    : {e}")
            QMessageBox.critical(self, "            ", f"                                    : {str(e)}")
    
    def save_block_properties(self, block_item):
                                                      ?""
        properties = {}
        
        if block_type == "loop":
            properties["count"] = 10
            properties["delay"] = 0.5
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
        elif block_type == "find_image":
            properties["image_path"] = ""
            properties["threshold"] = 0.8
            properties["action"] = "click"
        elif block_type == "find_text":
            properties["text"] = "                        "
            properties["font"] = "Arial"
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
        
        return properties
    
    def update_script(self):
        
        self.current_script = []
        
        for item in self.script_scene.items():
            if isinstance(item, BlockItem):
                block_data = {
                    "name": item.block_name,
                    "type": item.block_type,
                    "properties": item.properties,
                    "position": (item.pos().x(), item.pos().y()),
                    "connected_blocks": [block.block_name for block in item.connected_blocks]
                }
                self.current_script.append(block_data)
        
        self.script_updated.emit(json.dumps(self.current_script, ensure_ascii=False, indent=2))
    
    def save_script(self, file_path):
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_script, f, ensure_ascii=False, indent=2)
            logger.info(f"                                    : {file_path}")
            return True
        except Exception as e:
            logger.error(f"                                    : {e}")
            return False
    
    def load_script(self, file_path):
        
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
        
        return json.dumps(self.current_script, ensure_ascii=False, indent=2)
    
    def get_executable_code(self):
        
        code = []
        
        #                                                       
        code.append("import time")
        code.append("import random")
        code.append("from modules.image_recognition import ImageRecognition")
        code.append("from modules.mouse_control import MouseControl")
        code.append("from modules.keyboard_control import KeyboardControl")
        code.append("")
        code.append("image_recognizer = ImageRecognition()")
        code.append("mouse_controller = MouseControl()")
        code.append("keyboard_controller = KeyboardControl()")
        code.append("")
        code.append("#                                   ?)
        code.append("")
        
        #                                                                                                     ?        for i, block in enumerate(self.current_script):
            if block['type'] == "loop":
                count = block['properties'].get('count', 10)
                delay = block['properties'].get('delay', 0.5)
                code.append(f"# {block['name']}")
                code.append(f"for loop_i in range({count}):")
                code.append(f"    print(f'    ?{{loop_i+1}}                 ?)")
                code.append(f"    time.sleep({delay})")
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
                import json
                if x is not None and y is not None:
                    code.append(f"mouse_controller.click({x}, {y}, {json.dumps(button)}, {click_count}, {delay})")
                else:
                    code.append(f"mouse_controller.click(None, None, {json.dumps(button)}, {click_count}, {delay})")
                code.append("")
                
            elif block['type'] == "keyboard_input":
                text = block['properties'].get('text', 'Hello World')
                delay = block['properties'].get('delay', 0.1)
                code.append(f"# {block['name']}")
                import json
                code.append(f"keyboard_controller.type({json.dumps(text)}, {delay})")
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
                    code.append(f"    print('                            ?)")
                code.append("")
                
            elif block['type'] == "find_text":
                text = block['properties'].get('text', '                        ')
                threshold = block['properties'].get('threshold', 0.8)
                action = block['properties'].get('action', 'click')
                code.append(f"# {block['name']}")
                import json
                code.append(f"position = image_recognizer.find_text({json.dumps(text)}, {threshold})")
                code.append(f"if position:")
                if action == 'click':
                    code.append(f"    mouse_controller.move_to(position[0], position[1], 0.5)")
                    code.append(f"    mouse_controller.click(position[0], position[1], 'left', 1, 0.1)")
                code.append(f"else:")
                code.append(f"    print('                            ?)")
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
                code.append(f"    print('             {function_name}                 ?)")
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
                #                       ?
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
                
                #                       ?
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
                #                       ?
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
                
                #                       ?
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
                code.append(f"#                             ?)
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
                code.append(f"print(f'                            ? {{result_not}}')")
                code.append("")
        
        #                                                                                                                 ?        import json
        code.append("#                                                                                         ?)
        code.append("blocks_data = [")
        for block in self.current_script:
            code.append(f"    {json.dumps(block)},")
        code.append("]")
        
        return '\n'.join(code)
                
                if random_offset > 0:
                    #                                     
                    code.append(f"        #                                     ")
                    code.append(f"        offset_x1 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"        offset_y1 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"        offset_x2 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"        offset_y2 = random.randint(-{random_offset}, {random_offset})")
                    code.append(f"        mouse_controller.drag_to({start_x} + offset_x1, {start_y} + offset_y1, {end_x} + offset_x2, {end_y} + offset_y2, {duration})")
                else:
                    code.append(f"        mouse_controller.drag_to({start_x}, {start_y}, {end_x}, {end_y}, {duration})")
            
            elif block['type'] == "if":
                condition = block['properties'].get('condition', 'image_found')
                threshold = block['properties'].get('threshold', 0.8)
                
                code.append(f"        #                         : {condition}")
                code.append(f"        if {condition}:")
                code.append(f"            print('                        ')")
            
            elif block['type'] == "function":
                function_name = block['properties'].get('name', 'my_function')
                parameters = block['properties'].get('parameters', [])
                params_str = ', '.join(parameters)
                code.append(f"        def {function_name}({params_str}):")
                code.append(f"            print('             {function_name}                 ?)")
            
            elif block['type'] == "wait":
                wait_time = block['properties'].get('time', 1.0)
                code.append(f"        time.sleep({wait_time})")
            
            elif block['type'] == "jump":
                target_block = block['properties'].get('target_block', '')
                jump_type = block['properties'].get('jump_type', 'absolute')
                code.append(f"        #                             ? {target_block} (            : {jump_type})")
                code.append(f"        jump_target = {json.dumps(target_block)}")
                code.append(f"        jump_type = {json.dumps(jump_type)}")
                code.append(f"        if jump_target in block_name_to_index:")
                code.append(f"            print(f'                                        ? {{target_block}}')")
                code.append(f"            #                                     ")
                code.append(f"            target_index = block_name_to_index[jump_target]")
                code.append(f"            #                                                                         ")
                code.append(f"            if jump_type == 'absolute':")
                code.append(f"                block_index = target_index")
                code.append(f"            else:")  #                         
                code.append(f"                #                                                                                                           ?)
                code.append(f"                try:")
                code.append(f"                    #                                                                                   ?)
                code.append(f"                    offset = int(jump_target)")
                code.append(f"                    block_index += offset")
                code.append(f"                except:")
                code.append(f"                    print('                                                                ?)")
                code.append(f"                    block_index += 1")
                code.append(f"            #                                                             ")
                code.append(f"            if block_index < 0:")
                code.append(f"                block_index = 0")
                code.append(f"            if block_index >= len(blocks_data):")
                code.append(f"                block_index = len(blocks_data)")  #                         
                code.append(f"            #                                     ")
                code.append(f"            jump_flag = True")
                code.append(f"            #                                                             ")
                code.append(f"            continue")
            elif block['type'] == "and":
                operand1 = block['properties'].get('operand1', '')
                operand2 = block['properties'].get('operand2', '')
                condition_type = block['properties'].get('condition_type', 'image')
                threshold = block['properties'].get('threshold', 0.8)
                code.append(f"        #                             ?             1                ?")
                code.append(f"        #                         : {condition_type}")
                
                #                       ?
                if condition_type == "image":
                    code.append(f"        #                       ? -                         ")
                    if operand1:
                        code.append(f"        condition1 = image_recognizer.find_image({json.dumps(operand1)}, {threshold}) is not None")
                    else:
                        code.append(f"        condition1 = False")
                else:
                    code.append(f"        #                       ? -                         ")
                    if operand1:
                        code.append(f"        condition1 = image_recognizer.find_text({json.dumps(operand1)}, {threshold}) is not None")
                    else:
                        code.append(f"        condition1 = False")
                
                #                       ?
                if condition_type == "image":
                    code.append(f"        #                       ? -                         ")
                    if operand2:
                        code.append(f"        condition2 = image_recognizer.find_image({json.dumps(operand2)}, {threshold}) is not None")
                    else:
