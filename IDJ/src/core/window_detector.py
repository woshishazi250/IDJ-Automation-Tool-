#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口绑定和监测系统
"""

import win32gui
import win32con
import win32api
import psutil
import time
import threading
from PyQt5.QtCore import QObject, pyqtSignal
import logging

logger = logging.getLogger(__name__)

class WindowInfo:
    """窗口信息类"""
    def __init__(self, hwnd, title, class_name, pid):
        self.hwnd = hwnd
        self.title = title
        self.class_name = class_name
        self.pid = pid
        self.process_name = ""
        self.rect = (0, 0, 0, 0)
        
        try:
            process = psutil.Process(pid)
            self.process_name = process.name()
        except:
            self.process_name = "未知进程"
    
    def get_rect(self):
        """获取窗口矩形"""
        try:
            rect = win32gui.GetWindowRect(self.hwnd)
            self.rect = (rect[0], rect[1], rect[2], rect[3])
            return self.rect
        except Exception as e:
            logger.error(f"获取窗口矩形失败: {e}")
            return None
    
    def is_visible(self):
        """检查窗口是否可见"""
        try:
            return win32gui.IsWindowVisible(self.hwnd) and self.get_rect()[2] > 0 and self.get_rect()[3] > 0
        except:
            return False
    
    def __str__(self):
        return f"{self.title} ({self.process_name})"

class WindowDetector(QObject):
    """窗口检测器"""
    window_list_updated = pyqtSignal(list)
    window_monitored = pyqtSignal(object)
    window_updated = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        self.monitored_windows = []
        self.monitoring = False
        self.monitor_thread = None
    
    def enum_windows(self):
        """枚举所有顶级窗口"""
        windows = []
        def callback(hwnd, param):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    class_name = win32gui.GetClassName(hwnd)
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    windows.append(WindowInfo(hwnd, title, class_name, pid))
            return True
        
        import win32process
        win32gui.EnumWindows(callback, None)
        return windows
    
    def find_window_by_title(self, title):
        """通过标题查找窗口"""
        hwnd = win32gui.FindWindow(None, title)
        if hwnd:
            class_name = win32gui.GetClassName(hwnd)
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            return WindowInfo(hwnd, title, class_name, pid)
        return None
    
    def find_window_by_process(self, process_name):
        """通过进程名查找窗口"""
        windows = self.enum_windows()
        return [w for w in windows if w.process_name.lower() == process_name.lower()]
    
    def start_monitoring(self, hwnd):
        """开始监测特定窗口"""
        if hwnd in self.monitored_windows:
            logger.warning(f"窗口 {hwnd} 已在监测中")
            return
        
        window_info = None
        windows = self.enum_windows()
        for w in windows:
            if w.hwnd == hwnd:
                window_info = w
                break
        
        if window_info:
            self.monitored_windows.append(hwnd)
            self.window_monitored.emit(window_info)
            logger.info(f"开始监测窗口: {window_info}")
            
            # 启动监测线程
            if not self.monitoring:
                self.monitoring = True
                self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
                self.monitor_thread.start()
        else:
            logger.error(f"未找到窗口: {hwnd}")
    
    def stop_monitoring(self, hwnd):
        """停止监测特定窗口"""
        if hwnd in self.monitored_windows:
            self.monitored_windows.remove(hwnd)
            logger.info(f"停止监测窗口: {hwnd}")
        
        if not self.monitored_windows:
            self.monitoring = False
            self.monitor_thread = None
    
    def _monitor_loop(self):
        """监测循环"""
        while self.monitoring:
            for hwnd in self.monitored_windows.copy():
                try:
                    # 检查窗口是否存在
                    if not win32gui.IsWindow(hwnd):
                        self.monitored_windows.remove(hwnd)
                        logger.warning(f"窗口 {hwnd} 已关闭，停止监测")
                        continue
                        
                    title = win32gui.GetWindowText(hwnd)
                    class_name = win32gui.GetClassName(hwnd)
                    rect = win32gui.GetWindowRect(hwnd)
                    
                    # 获取进程ID
                    import win32process
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    
                    # 创建窗口信息对象
                    window_info = WindowInfo(hwnd, title, class_name, pid)
                    window_info.rect = rect
                    
                    # 发送窗口更新信号
                    self.window_updated.emit(window_info)
                    
                except Exception as e:
                    logger.error(f"监测窗口 {hwnd} 失败: {e}")
                    self.monitored_windows.remove(hwnd)
            
            time.sleep(0.5)
    
    def get_all_windows(self):
        """获取所有可见窗口信息"""
        try:
            windows = self.enum_windows()
            window_data = []
            for w in windows:
                # 确保获取到有效的窗口信息
                rect = w.get_rect()
                window_data.append({
                    "hwnd": w.hwnd,
                    "title": w.title,
                    "class_name": w.class_name,
                    "pid": w.pid,
                    "process_name": w.process_name,
                    "rect": rect if rect else (0, 0, 0, 0)
                })
            
            logger.info(f"成功获取到 {len(window_data)} 个可见窗口")
            return window_data
        except Exception as e:
            logger.error(f"获取窗口列表失败: {e}")
            return []
