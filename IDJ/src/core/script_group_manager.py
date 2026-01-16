#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
脚本组管理器 - 管理并行执行的多个脚本组
"""

import logging
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, QMutexLocker
import time

logger = logging.getLogger(__name__)


class ScriptGroupThread(QThread):
    """脚本组执行线程"""
    
    # 信号定义
    started = pyqtSignal(str)  # 脚本组开始执行
    finished = pyqtSignal(str)  # 脚本组执行完成
    error = pyqtSignal(str, str)  # 脚本组执行错误 (group_id, error_message)
    progress = pyqtSignal(str, int, int)  # 执行进度 (group_id, current, total)
    block_executed = pyqtSignal(str, str)  # 积木执行完成 (group_id, block_name)
    
    def __init__(self, group_id, group_name, blocks, executor):
        super().__init__()
        self.group_id = group_id
        self.group_name = group_name
        self.blocks = blocks
        self.executor = executor  # 积木执行器
        
        self.is_running = True
        self.is_paused = False
        self.mutex = QMutex()
        
    def run(self):
        """执行脚本组"""
        try:
            self.started.emit(self.group_id)
            logger.info(f"脚本组 '{self.group_name}' (ID: {self.group_id}) 开始执行")
            
            total_blocks = len(self.blocks)
            
            for i, block in enumerate(self.blocks):
                # 检查是否需要停止
                with QMutexLocker(self.mutex):
                    if not self.is_running:
                        logger.info(f"脚本组 '{self.group_name}' 被停止")
                        break
                
                # 检查是否暂停
                while True:
                    with QMutexLocker(self.mutex):
                        if not self.is_paused:
                            break
                    time.sleep(0.1)
                
                # 执行积木
                try:
                    self.executor.execute_block(block)
                    self.block_executed.emit(self.group_id, block.get('name', '未命名积木'))
                    self.progress.emit(self.group_id, i + 1, total_blocks)
                except Exception as e:
                    logger.error(f"执行积木 '{block.get('name')}' 时出错: {e}")
                    self.error.emit(self.group_id, str(e))
            
            self.finished.emit(self.group_id)
            logger.info(f"脚本组 '{self.group_name}' 执行完成")
            
        except Exception as e:
            logger.error(f"脚本组 '{self.group_name}' 执行失败: {e}")
            self.error.emit(self.group_id, str(e))
    
    def pause(self):
        """暂停执行"""
        with QMutexLocker(self.mutex):
            self.is_paused = True
            logger.info(f"脚本组 '{self.group_name}' 已暂停")
    
    def resume(self):
        """恢复执行"""
        with QMutexLocker(self.mutex):
            self.is_paused = False
            logger.info(f"脚本组 '{self.group_name}' 已恢复")
    
    def stop(self):
        """停止执行"""
        with QMutexLocker(self.mutex):
            self.is_running = False
            self.is_paused = False
            logger.info(f"脚本组 '{self.group_name}' 停止信号已发送")


class ScriptGroup:
    """脚本组数据类"""
    
    def __init__(self, group_id, name, start_block, blocks):
        self.group_id = group_id
        self.name = name
        self.start_block = start_block  # 启动积木
        self.blocks = blocks  # 脚本组中的所有积木
        self.thread = None  # 执行线程
        self.is_running = False
        self.is_paused = False
        self.auto_start = True  # 是否自动启动
    
    def __repr__(self):
        return f"ScriptGroup(id={self.group_id}, name={self.name}, blocks={len(self.blocks)})"


class ScriptGroupManager:
    """脚本组管理器 - 管理多个并行执行的脚本组"""
    
    # 信号定义（需要在QObject子类中使用）
    
    def __init__(self, executor):
        self.executor = executor  # 积木执行器
        self.groups = {}  # {group_id: ScriptGroup}
        self.running_threads = {}  # {group_id: ScriptGroupThread}
        self.next_group_id = 1
        
        logger.info("脚本组管理器初始化完成")
    
    def identify_groups(self, all_blocks):
        """
        识别所有脚本组
        从启动积木开始，沿着连接关系识别每个脚本组
        """
        self.groups.clear()
        
        # 查找所有启动积木
        start_blocks = [block for block in all_blocks if block.get('type') == 'start']
        
        if not start_blocks:
            logger.warning("未找到启动积木，将所有积木作为一个默认脚本组")
            # 如果没有启动积木，创建一个默认脚本组
            if all_blocks:
                group_id = self._generate_group_id()
                group = ScriptGroup(
                    group_id=group_id,
                    name="默认脚本",
                    start_block=None,
                    blocks=all_blocks
                )
                self.groups[group_id] = group
            return self.groups
        
        # 为每个启动积木创建一个脚本组
        for start_block in start_blocks:
            group_id = self._generate_group_id()
            group_name = start_block.get('properties', {}).get('name', f'脚本{group_id}')
            
            # 收集该脚本组的所有积木（沿着连接关系）
            group_blocks = self._collect_connected_blocks(start_block, all_blocks)
            
            group = ScriptGroup(
                group_id=group_id,
                name=group_name,
                start_block=start_block,
                blocks=group_blocks
            )
            
            self.groups[group_id] = group
            logger.info(f"识别到脚本组: {group}")
        
        return self.groups
    
    def _collect_connected_blocks(self, start_block, all_blocks):
        """收集从启动积木开始连接的所有积木"""
        collected = []
        visited = set()
        
        def collect_recursive(block):
            if block is None or id(block) in visited:
                return
            
            visited.add(id(block))
            collected.append(block)
            
            # 查找连接的下一个积木
            # 这里需要根据实际的连接关系来实现
            # 简化版本：按位置顺序收集
            
        collect_recursive(start_block)
        
        # 简化实现：收集启动积木下方的所有积木
        start_y = start_block.get('position', [0, 0])[1]
        start_x = start_block.get('position', [0, 0])[0]
        
        # 收集在启动积木下方且水平位置接近的积木
        for block in all_blocks:
            if block == start_block:
                continue
            
            block_y = block.get('position', [0, 0])[1]
            block_x = block.get('position', [0, 0])[0]
            
            # 如果积木在启动积木下方且水平位置接近（±100像素）
            if block_y > start_y and abs(block_x - start_x) < 100:
                collected.append(block)
        
        # 按y坐标排序
        collected.sort(key=lambda b: b.get('position', [0, 0])[1])
        
        return collected
    
    def _generate_group_id(self):
        """生成唯一的脚本组ID"""
        group_id = f"group_{self.next_group_id}"
        self.next_group_id += 1
        return group_id
    
    def run_all(self):
        """运行所有自动启动的脚本组"""
        logger.info("开始运行所有脚本组")
        
        for group_id, group in self.groups.items():
            if group.auto_start:
                self.run_group(group_id)
        
        logger.info(f"已启动 {len(self.running_threads)} 个脚本组")
    
    def run_group(self, group_id):
        """运行指定的脚本组"""
        if group_id not in self.groups:
            logger.error(f"脚本组 {group_id} 不存在")
            return False
        
        group = self.groups[group_id]
        
        # 如果已经在运行，先停止
        if group_id in self.running_threads:
            self.stop_group(group_id)
        
        # 创建并启动执行线程
        thread = ScriptGroupThread(
            group_id=group_id,
            group_name=group.name,
            blocks=group.blocks,
            executor=self.executor
        )
        
        # 连接信号
        thread.finished.connect(lambda gid=group_id: self._on_group_finished(gid))
        thread.error.connect(lambda gid, err: self._on_group_error(gid, err))
        
        self.running_threads[group_id] = thread
        group.thread = thread
        group.is_running = True
        
        thread.start()
        logger.info(f"脚本组 '{group.name}' (ID: {group_id}) 已启动")
        
        return True
    
    def pause_group(self, group_id):
        """暂停指定的脚本组"""
        if group_id in self.running_threads:
            thread = self.running_threads[group_id]
            thread.pause()
            self.groups[group_id].is_paused = True
            return True
        return False
    
    def resume_group(self, group_id):
        """恢复指定的脚本组"""
        if group_id in self.running_threads:
            thread = self.running_threads[group_id]
            thread.resume()
            self.groups[group_id].is_paused = False
            return True
        return False
    
    def stop_group(self, group_id):
        """停止指定的脚本组"""
        if group_id in self.running_threads:
            thread = self.running_threads[group_id]
            thread.stop()
            thread.wait(2000)  # 等待最多2秒
            
            del self.running_threads[group_id]
            self.groups[group_id].is_running = False
            self.groups[group_id].is_paused = False
            self.groups[group_id].thread = None
            
            logger.info(f"脚本组 {group_id} 已停止")
            return True
        return False
    
    def stop_all(self):
        """停止所有脚本组"""
        logger.info("停止所有脚本组")
        
        group_ids = list(self.running_threads.keys())
        for group_id in group_ids:
            self.stop_group(group_id)
        
        logger.info("所有脚本组已停止")
    
    def pause_all(self):
        """暂停所有脚本组"""
        for group_id in self.running_threads.keys():
            self.pause_group(group_id)
    
    def resume_all(self):
        """恢复所有脚本组"""
        for group_id in self.running_threads.keys():
            self.resume_group(group_id)
    
    def get_running_groups(self):
        """获取正在运行的脚本组列表"""
        return [self.groups[gid] for gid in self.running_threads.keys()]
    
    def get_all_groups(self):
        """获取所有脚本组列表"""
        return list(self.groups.values())
    
    def is_group_running(self, group_id):
        """检查脚本组是否正在运行"""
        return group_id in self.running_threads
    
    def _on_group_finished(self, group_id):
        """脚本组执行完成的回调"""
        if group_id in self.running_threads:
            del self.running_threads[group_id]
        
        if group_id in self.groups:
            self.groups[group_id].is_running = False
            self.groups[group_id].thread = None
        
        logger.info(f"脚本组 {group_id} 执行完成并清理")
    
    def _on_group_error(self, group_id, error_message):
        """脚本组执行错误的回调"""
        logger.error(f"脚本组 {group_id} 执行错误: {error_message}")
