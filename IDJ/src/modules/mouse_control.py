import pyautogui
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)

class MouseControl:
    """鼠标控制模块，提供鼠标移动、点击、拖拽等功能"""
    
    def __init__(self):
        # 设置PyAutoGUI的参数
        pyautogui.FAILSAFE = True  # 启用安全模式
        pyautogui.PAUSE = 0.1    # 每次操作后的暂停时间
        
        logger.info("鼠标控制模块初始化成功")
    
    def move_to(self, x, y, duration=0.5):
        """
        移动鼠标到指定坐标
        
        Args:
            x, y: 目标坐标
            duration: 移动时间（秒）
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
            logger.info(f"鼠标移动到: ({x}, {y})")
        except Exception as e:
            logger.error(f"鼠标移动失败: {e}")
    
    def click(self, x=None, y=None, button='left', clicks=1, interval=0.0):
        """
        点击鼠标
        
        Args:
            x, y: 点击坐标（可选，默认当前位置）
            button: 鼠标按钮（'left', 'right', 'middle'）
            clicks: 点击次数
            interval: 点击间隔
        """
        try:
            if x is not None and y is not None:
                pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
                logger.info(f"鼠标{button}键点击: ({x}, {y})")
            else:
                pyautogui.click(clicks=clicks, interval=interval, button=button)
                logger.info(f"鼠标{button}键点击")
        except Exception as e:
            logger.error(f"鼠标点击失败: {e}")
    
    def double_click(self, x=None, y=None, button='left'):
        """
        双击鼠标
        
        Args:
            x, y: 点击坐标（可选，默认当前位置）
            button: 鼠标按钮
        """
        try:
            if x is not None and y is not None:
                pyautogui.doubleClick(x, y, button=button)
                logger.info(f"鼠标{button}键双击: ({x}, {y})")
            else:
                pyautogui.doubleClick(button=button)
                logger.info(f"鼠标{button}键双击")
        except Exception as e:
            logger.error(f"鼠标双击失败: {e}")
    
    def right_click(self, x=None, y=None):
        """
        右键点击
        
        Args:
            x, y: 点击坐标（可选，默认当前位置）
        """
        try:
            if x is not None and y is not None:
                pyautogui.rightClick(x, y)
                logger.info(f"鼠标右键点击: ({x}, {y})")
            else:
                pyautogui.rightClick()
                logger.info("鼠标右键点击")
        except Exception as e:
            logger.error(f"鼠标右键点击失败: {e}")
    
    def drag_to(self, x1, y1, x2, y2, duration=0.5, button='left'):
        """
        拖拽操作
        
        Args:
            x1, y1: 起点坐标
            x2, y2: 终点坐标
            duration: 拖拽时间（秒）
            button: 鼠标按钮
        """
        try:
            pyautogui.moveTo(x1, y1)
            pyautogui.dragTo(x2, y2, duration=duration, button=button)
            logger.info(f"鼠标{button}键拖拽: ({x1}, {y1}) -> ({x2}, {y2})")
        except Exception as e:
            logger.error(f"鼠标拖拽失败: {e}")
    
    def get_position(self):
        """
        获取当前鼠标位置
        
        Returns:
            (x, y): 鼠标坐标
        """
        try:
            x, y = pyautogui.position()
            logger.info(f"获取鼠标位置: ({x}, {y})")
            return (x, y)
        except Exception as e:
            logger.error(f"获取鼠标位置失败: {e}")
            return None
    
    def scroll(self, amount, x=None, y=None):
        """
        滚动鼠标滚轮
        
        Args:
            amount: 滚动量（正数向上，负数向下）
            x, y: 滚动位置（可选，默认当前位置）
        """
        try:
            if x is not None and y is not None:
                pyautogui.scroll(amount, x, y)
                logger.info(f"鼠标滚轮滚动: {amount}，位置: ({x}, {y})")
            else:
                pyautogui.scroll(amount)
                logger.info(f"鼠标滚轮滚动: {amount}")
        except Exception as e:
            logger.error(f"鼠标滚轮滚动失败: {e}")
