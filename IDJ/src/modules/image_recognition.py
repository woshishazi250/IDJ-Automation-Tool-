#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图像识别模块
提供图像匹配、文字识别等功能
"""

import logging
import cv2
import numpy as np
from PIL import Image
import pytesseract

logger = logging.getLogger(__name__)

class ImageRecognition:
    """图像识别主类"""
    
    def __init__(self):
        self.init_recognition()
    
    def init_recognition(self):
        """初始化图像识别模块"""
        try:
            # 检查依赖
            if not hasattr(cv2, 'matchTemplate'):
                logger.warning("OpenCV图像匹配功能未找到")
            
            if not hasattr(pytesseract, 'image_to_string'):
                logger.warning("Tesseract OCR功能未找到")
            
            logger.info("图像识别模块初始化成功")
        except Exception as e:
            logger.error(f"图像识别模块初始化失败: {e}")
    
    def find_image(self, template_path, threshold=0.8):
        """
        在屏幕上寻找指定图像
        
        Args:
            template_path: 模板图像路径
            threshold: 匹配阈值
            
        Returns:
            (x, y) 匹配位置坐标，未找到返回None
        """
        try:
            # 加载模板图像
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                logger.error(f"无法加载模板图像: {template_path}")
                return None
            
            # 获取屏幕截图
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # 模板匹配
            result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
            
            # 找到匹配位置
            locations = np.where(result >= threshold)
            
            if len(locations[0]) > 0:
                # 取第一个匹配位置
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                x, y = max_loc
                h, w = template.shape[:2]
                
                # 返回中心点坐标
                center_x = x + w // 2
                center_y = y + h // 2
                
                logger.info(f"找到图像匹配，位置: ({center_x}, {center_y})，匹配度: {max_val:.2f}")
                return (center_x, center_y)
            else:
                logger.info("未找到匹配的图像")
                return None
                
        except Exception as e:
            logger.error(f"图像匹配失败: {e}")
            return None
    
    def find_text(self, target_text, font=None, size=None, color=None, threshold=0.8):
        """
        在屏幕上寻找指定文字
        
        Args:
            target_text: 目标文字
            font: 字体
            size: 字体大小
            color: 文字颜色
            threshold: 匹配阈值
            
        Returns:
            (x, y) 文字位置坐标，未找到返回None
        """
        try:
            # 获取屏幕截图
            import pyautogui
            screenshot = pyautogui.screenshot()
            screenshot = np.array(screenshot)
            
            # 文字识别
            text = pytesseract.image_to_string(screenshot)
            
            if target_text in text:
                logger.info(f"找到文字: {target_text}")
                return (100, 100)  # 临时返回固定位置
            else:
                logger.info(f"未找到文字: {target_text}")
                return None
                
        except Exception as e:
            logger.error(f"文字识别失败: {e}")
            return None
    
    def image_match(self, image1_path, image2_path, threshold=0.8):
        """
        比较两张图像的相似度
        
        Args:
            image1_path: 第一张图像路径
            image2_path: 第二张图像路径
            threshold: 相似度阈值
            
        Returns:
            相似度值 [0, 1]，超过阈值返回True
        """
        try:
            # 读取图像
            img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
            img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)
            
            if img1 is None or img2 is None:
                logger.error("无法读取图像文件")
                return False
            
            # 调整图像大小
            img1 = cv2.resize(img1, (300, 300))
            img2 = cv2.resize(img2, (300, 300))
            
            # 计算相似度
            orb = cv2.ORB_create()
            kp1, des1 = orb.detectAndCompute(img1, None)
            kp2, des2 = orb.detectAndCompute(img2, None)
            
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(des1, des2)
            
            # 计算匹配率
            if len(kp1) > 0 and len(kp2) > 0:
                similarity = len(matches) / max(len(kp1), len(kp2))
                logger.info(f"图像相似度: {similarity:.2f}")
                
                return similarity >= threshold
            else:
                logger.warning("图像特征提取失败")
                return False
                
        except Exception as e:
            logger.error(f"图像相似度计算失败: {e}")
            return False
    
    def find_color(self, color, tolerance=10, region=None):
        """
        在屏幕上寻找指定颜色
        
        Args:
            color: 目标颜色，可以是:
                   - RGB元组 (R, G, B)，如 (255, 0, 0) 表示红色
                   - 十六进制字符串，如 "#FF0000" 或 "FF0000"
            tolerance: 颜色容差 (0-255)，默认10
            region: 搜索区域 (x, y, width, height)，None表示全屏
            
        Returns:
            (x, y) 找到的颜色位置坐标，未找到返回None
        """
        try:
            import pyautogui
            
            # 解析颜色
            if isinstance(color, str):
                # 十六进制颜色
                color = color.lstrip('#')
                if len(color) == 6:
                    r = int(color[0:2], 16)
                    g = int(color[2:4], 16)
                    b = int(color[4:6], 16)
                    target_color = (r, g, b)
                else:
                    logger.error(f"无效的颜色格式: {color}")
                    return None
            elif isinstance(color, (tuple, list)) and len(color) == 3:
                target_color = tuple(color)
            else:
                logger.error(f"无效的颜色格式: {color}")
                return None
            
            # 获取屏幕截图
            if region:
                screenshot = pyautogui.screenshot(region=region)
                offset_x, offset_y = region[0], region[1]
            else:
                screenshot = pyautogui.screenshot()
                offset_x, offset_y = 0, 0
            
            # 转换为numpy数组 (RGB格式)
            screenshot_np = np.array(screenshot)
            
            # 计算颜色差异
            r_diff = np.abs(screenshot_np[:, :, 0].astype(np.int16) - target_color[0])
            g_diff = np.abs(screenshot_np[:, :, 1].astype(np.int16) - target_color[1])
            b_diff = np.abs(screenshot_np[:, :, 2].astype(np.int16) - target_color[2])
            
            # 找到在容差范围内的像素
            mask = (r_diff <= tolerance) & (g_diff <= tolerance) & (b_diff <= tolerance)
            
            # 找到匹配的位置
            locations = np.where(mask)
            
            if len(locations[0]) > 0:
                # 返回第一个匹配位置
                y, x = locations[0][0], locations[1][0]
                result_x = x + offset_x
                result_y = y + offset_y
                
                logger.info(f"找到颜色 RGB{target_color}，位置: ({result_x}, {result_y})")
                return (result_x, result_y)
            else:
                logger.info(f"未找到颜色 RGB{target_color}")
                return None
                
        except Exception as e:
            logger.error(f"颜色查找失败: {e}")
            return None
    
    def find_all_colors(self, color, tolerance=10, region=None, max_count=100):
        """
        在屏幕上寻找所有指定颜色的位置
        
        Args:
            color: 目标颜色 (RGB元组或十六进制字符串)
            tolerance: 颜色容差 (0-255)
            region: 搜索区域 (x, y, width, height)
            max_count: 最大返回数量
            
        Returns:
            [(x, y), ...] 所有找到的位置列表
        """
        try:
            import pyautogui
            
            # 解析颜色
            if isinstance(color, str):
                color = color.lstrip('#')
                if len(color) == 6:
                    r = int(color[0:2], 16)
                    g = int(color[2:4], 16)
                    b = int(color[4:6], 16)
                    target_color = (r, g, b)
                else:
                    logger.error(f"无效的颜色格式: {color}")
                    return []
            elif isinstance(color, (tuple, list)) and len(color) == 3:
                target_color = tuple(color)
            else:
                logger.error(f"无效的颜色格式: {color}")
                return []
            
            # 获取屏幕截图
            if region:
                screenshot = pyautogui.screenshot(region=region)
                offset_x, offset_y = region[0], region[1]
            else:
                screenshot = pyautogui.screenshot()
                offset_x, offset_y = 0, 0
            
            screenshot_np = np.array(screenshot)
            
            # 计算颜色差异
            r_diff = np.abs(screenshot_np[:, :, 0].astype(np.int16) - target_color[0])
            g_diff = np.abs(screenshot_np[:, :, 1].astype(np.int16) - target_color[1])
            b_diff = np.abs(screenshot_np[:, :, 2].astype(np.int16) - target_color[2])
            
            mask = (r_diff <= tolerance) & (g_diff <= tolerance) & (b_diff <= tolerance)
            locations = np.where(mask)
            
            results = []
            for i in range(min(len(locations[0]), max_count)):
                y, x = locations[0][i], locations[1][i]
                results.append((x + offset_x, y + offset_y))
            
            logger.info(f"找到 {len(results)} 个颜色 RGB{target_color} 的位置")
            return results
            
        except Exception as e:
            logger.error(f"颜色查找失败: {e}")
            return []
