import pyautogui
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)

class KeyboardControl:
    """键盘控制模块，提供键盘输入、组合键等功能"""
    
    def __init__(self):
        # 设置PyAutoGUI的参数
        pyautogui.PAUSE = 0.1    # 每次操作后的暂停时间
        
        logger.info("键盘控制模块初始化成功")
    
    def press_key(self, key, presses=1, interval=0.0):
        """
        按键操作
        
        Args:
            key: 按键名称（字符串）
            presses: 按键次数
            interval: 按键间隔
        """
        try:
            pyautogui.press(key, presses=presses, interval=interval)
            logger.info(f"按键 '{key}' 被按下 {presses} 次")
        except Exception as e:
            logger.error(f"按键操作失败: {e}")
    
    def type_text(self, text, interval=0.05):
        """
        输入文本
        
        Args:
            text: 要输入的文本
            interval: 每个字符输入间隔
        """
        try:
            pyautogui.typewrite(text, interval=interval)
            logger.info(f"输入文本: '{text}'")
        except Exception as e:
            logger.error(f"文本输入失败: {e}")
    
    def hotkey(self, *args):
        """
        组合键操作
        
        Args:
            *args: 按键名称列表
        """
        try:
            pyautogui.hotkey(*args)
            logger.info(f"组合键操作: {', '.join(args)}")
        except Exception as e:
            logger.error(f"组合键操作失败: {e}")
    
    def key_down(self, key):
        """
        按下按键不释放
        
        Args:
            key: 按键名称
        """
        try:
            pyautogui.keyDown(key)
            logger.info(f"按键 '{key}' 按下")
        except Exception as e:
            logger.error(f"按键按下操作失败: {e}")
    
    def key_up(self, key):
        """
        释放按键
        
        Args:
            key: 按键名称
        """
        try:
            pyautogui.keyUp(key)
            logger.info(f"按键 '{key}' 释放")
        except Exception as e:
            logger.error(f"按键释放操作失败: {e}")
    
    def combination(self, keys):
        """
        执行复杂的按键组合
        
        Args:
            keys: 按键序列列表
        """
        try:
            for key in keys:
                if isinstance(key, list):
                    # 组合键
                    self.hotkey(*key)
                elif isinstance(key, tuple) and len(key) == 2:
                    # 按键并按住
                    key_name, duration = key
                    self.key_down(key_name)
                    time.sleep(duration)
                    self.key_up(key_name)
                else:
                    # 单键
                    self.press_key(key)
                
                time.sleep(0.1)  # 每个操作后暂停
                
            logger.info("按键组合操作完成")
        except Exception as e:
            logger.error(f"按键组合操作失败: {e}")
