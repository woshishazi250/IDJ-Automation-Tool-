#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本录制模块
录制鼠标点击、拖拽、键盘输入等操作
"""

import time
import json
import logging
from pynput import mouse, keyboard
from PyQt5.QtCore import QObject, pyqtSignal, QThread

logger = logging.getLogger(__name__)

class ScriptRecorder(QObject):
    """脚本录制器"""
    
    # 信号
    recording_started = pyqtSignal()
    recording_stopped = pyqtSignal()
    action_recorded = pyqtSignal(dict)  # 录制到新动作
    
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.recorded_actions = []
        self.start_time = None
        self.mouse_listener = None
        self.keyboard_listener = None
        self.last_mouse_pos = None
        self.drag_start_pos = None
        self.is_dragging = False
        
    def start_recording(self):
        """开始录制"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.recorded_actions = []
        self.start_time = time.time()
        self.last_mouse_pos = None
        self.drag_start_pos = None
        self.is_dragging = False
        
        # 启动鼠标监听
        self.mouse_listener = mouse.Listener(
            on_click=self._on_mouse_click,
            on_move=self._on_mouse_move
        )
        self.mouse_listener.start()
        
        # 启动键盘监听
        self.keyboard_listener = keyboard.Listener(
            on_press=self._on_key_press,
            on_release=self._on_key_release
        )
        self.keyboard_listener.start()
        
        self.recording_started.emit()
        logger.info("脚本录制已开始")
        
    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return self.recorded_actions
            
        self.is_recording = False
        
        # 停止监听器
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            
        self.recording_stopped.emit()
        logger.info(f"脚本录制已停止，共录制 {len(self.recorded_actions)} 个动作")
        
        return self.recorded_actions
        
    def _get_elapsed_time(self):
        """获取从开始录制到现在的时间"""
        if self.start_time:
            return time.time() - self.start_time
        return 0
        
    def _on_mouse_click(self, x, y, button, pressed):
        """鼠标点击事件"""
        if not self.is_recording:
            return
            
        if pressed:
            # 记录按下位置，可能是拖拽开始
            self.drag_start_pos = (x, y)
            self.is_dragging = False
        else:
            # 鼠标释放
            if self.is_dragging and self.drag_start_pos:
                # 这是一个拖拽操作
                action = {
                    'type': 'drag',
                    'start_x': self.drag_start_pos[0],
                    'start_y': self.drag_start_pos[1],
                    'end_x': x,
                    'end_y': y,
                    'button': button.name,
                    'time': self._get_elapsed_time()
                }
                self.recorded_actions.append(action)
                self.action_recorded.emit(action)
                logger.debug(f"录制拖拽: {self.drag_start_pos} -> ({x}, {y})")
            else:
                # 这是一个点击操作
                action = {
                    'type': 'click',
                    'x': x,
                    'y': y,
                    'button': button.name,
                    'time': self._get_elapsed_time()
                }
                self.recorded_actions.append(action)
                self.action_recorded.emit(action)
                logger.debug(f"录制点击: ({x}, {y}), 按钮: {button.name}")
                
            self.drag_start_pos = None
            self.is_dragging = False
            
    def _on_mouse_move(self, x, y):
        """鼠标移动事件"""
        if not self.is_recording:
            return
            
        # 检测是否在拖拽
        if self.drag_start_pos:
            dx = abs(x - self.drag_start_pos[0])
            dy = abs(y - self.drag_start_pos[1])
            if dx > 5 or dy > 5:
                self.is_dragging = True
                
    def _on_key_press(self, key):
        """键盘按下事件"""
        if not self.is_recording:
            return
            
        # 检查是否按下ESC取消录制
        try:
            if key == keyboard.Key.esc:
                self.stop_recording()
                return
        except:
            pass
            
        # 记录按键
        try:
            if hasattr(key, 'char') and key.char:
                key_name = key.char
            else:
                key_name = key.name
        except:
            key_name = str(key)
            
        action = {
            'type': 'key_press',
            'key': key_name,
            'time': self._get_elapsed_time()
        }
        self.recorded_actions.append(action)
        self.action_recorded.emit(action)
        logger.debug(f"录制按键: {key_name}")
        
    def _on_key_release(self, key):
        """键盘释放事件"""
        pass  # 暂时不记录释放事件
        
    def save_script(self, file_path):
        """保存录制的脚本到文件"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.recorded_actions, f, ensure_ascii=False, indent=2)
            logger.info(f"脚本已保存到: {file_path}")
            return True
        except Exception as e:
            logger.error(f"保存脚本失败: {e}")
            return False
            
    def load_script(self, file_path):
        """从文件加载脚本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.recorded_actions = json.load(f)
            logger.info(f"脚本已加载: {file_path}, 共 {len(self.recorded_actions)} 个动作")
            return self.recorded_actions
        except Exception as e:
            logger.error(f"加载脚本失败: {e}")
            return []


class ScriptPlayer(QThread):
    """脚本播放器"""
    
    # 信号
    playback_started = pyqtSignal()
    playback_finished = pyqtSignal()
    playback_paused = pyqtSignal()
    playback_resumed = pyqtSignal()
    playback_stopped = pyqtSignal()
    action_executed = pyqtSignal(int, dict)  # 执行的动作索引和内容
    error_occurred = pyqtSignal(str)
    
    def __init__(self, actions=None):
        super().__init__()
        self.actions = actions or []
        self.is_paused = False
        self.is_stopped = False
        self.speed_multiplier = 1.0
        
    def set_actions(self, actions):
        """设置要播放的动作列表"""
        self.actions = actions
        
    def set_speed(self, multiplier):
        """设置播放速度倍率"""
        self.speed_multiplier = multiplier
        
    def pause(self):
        """暂停播放"""
        self.is_paused = True
        self.playback_paused.emit()
        logger.info("脚本播放已暂停")
        
    def resume(self):
        """恢复播放"""
        self.is_paused = False
        self.playback_resumed.emit()
        logger.info("脚本播放已恢复")
        
    def stop(self):
        """停止播放"""
        self.is_stopped = True
        self.playback_stopped.emit()
        logger.info("脚本播放已停止")
        
    def run(self):
        """执行脚本"""
        import pyautogui
        
        self.is_paused = False
        self.is_stopped = False
        self.playback_started.emit()
        
        logger.info(f"开始播放脚本，共 {len(self.actions)} 个动作")
        
        last_time = 0
        
        try:
            for i, action in enumerate(self.actions):
                # 检查是否停止
                if self.is_stopped:
                    break
                    
                # 检查是否暂停
                while self.is_paused and not self.is_stopped:
                    self.msleep(100)
                    
                if self.is_stopped:
                    break
                    
                # 计算延迟时间
                action_time = action.get('time', 0)
                delay = (action_time - last_time) / self.speed_multiplier
                if delay > 0:
                    time.sleep(delay)
                last_time = action_time
                
                # 执行动作
                action_type = action.get('type')
                
                if action_type == 'click':
                    x = action.get('x', 0)
                    y = action.get('y', 0)
                    button = action.get('button', 'left')
                    pyautogui.click(x, y, button=button)
                    logger.debug(f"执行点击: ({x}, {y})")
                    
                elif action_type == 'drag':
                    start_x = action.get('start_x', 0)
                    start_y = action.get('start_y', 0)
                    end_x = action.get('end_x', 0)
                    end_y = action.get('end_y', 0)
                    pyautogui.moveTo(start_x, start_y)
                    pyautogui.drag(end_x - start_x, end_y - start_y, duration=0.3)
                    logger.debug(f"执行拖拽: ({start_x}, {start_y}) -> ({end_x}, {end_y})")
                    
                elif action_type == 'key_press':
                    key = action.get('key', '')
                    if len(key) == 1:
                        pyautogui.press(key)
                    else:
                        pyautogui.press(key)
                    logger.debug(f"执行按键: {key}")
                    
                elif action_type == 'move':
                    x = action.get('x', 0)
                    y = action.get('y', 0)
                    pyautogui.moveTo(x, y)
                    logger.debug(f"执行移动: ({x}, {y})")
                    
                self.action_executed.emit(i, action)
                
        except Exception as e:
            logger.error(f"脚本播放错误: {e}")
            self.error_occurred.emit(str(e))
            
        self.playback_finished.emit()
        logger.info("脚本播放完成")


class ColorPicker(QObject):
    """取色器"""
    
    color_picked = pyqtSignal(tuple)  # (r, g, b)
    picking_cancelled = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_picking = False
        self.mouse_listener = None
        self.keyboard_listener = None
        
    def start_picking(self):
        """开始取色"""
        self.is_picking = True
        
        # 启动鼠标监听
        self.mouse_listener = mouse.Listener(on_click=self._on_click)
        self.mouse_listener.start()
        
        # 启动键盘监听（ESC取消）
        self.keyboard_listener = keyboard.Listener(on_press=self._on_key_press)
        self.keyboard_listener.start()
        
        logger.info("取色模式已启动，点击屏幕取色，ESC取消")
        
    def stop_picking(self):
        """停止取色"""
        self.is_picking = False
        
        if self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        if self.keyboard_listener:
            self.keyboard_listener.stop()
            self.keyboard_listener = None
            
    def _on_click(self, x, y, button, pressed):
        """鼠标点击取色"""
        if not self.is_picking or not pressed:
            return
            
        # 获取点击位置的颜色
        try:
            import pyautogui
            from PIL import ImageGrab
            
            # 截取屏幕上该点的颜色
            screenshot = ImageGrab.grab(bbox=(x, y, x+1, y+1))
            color = screenshot.getpixel((0, 0))
            
            self.stop_picking()
            self.color_picked.emit(color)
            logger.info(f"取色成功: RGB{color} 位置({x}, {y})")
            
        except Exception as e:
            logger.error(f"取色失败: {e}")
            self.stop_picking()
            
    def _on_key_press(self, key):
        """键盘按键"""
        try:
            if key == keyboard.Key.esc:
                self.stop_picking()
                self.picking_cancelled.emit()
                logger.info("取色已取消")
        except:
            pass
