#!/usr/bin/env python3



# -*- coding: utf-8 -*-



"""



主窗口界面



IDJ脚本自动化软件的主界面



"""







import sys



import os



import logging







# 添加项目根目录到模块搜索路径



sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



from PyQt5.QtWidgets import (



    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,



    QGroupBox, QLabel, QPushButton, QListWidget, QSplitter,



    QFileDialog, QMessageBox, QTextEdit, QComboBox, QLineEdit,



    QSpinBox, QDoubleSpinBox, QCheckBox, QProgressBar, QDialog,



    QScrollArea, QMenuBar, QMenu, QAction



)



from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal



from PyQt5.QtGui import QIcon, QFont







from core.window_detector import WindowDetector



from modules.screenshot_tool import ScreenshotManager



from blocks.block_editor import BlockEditor



from modules.image_recognition import ImageRecognition



from modules.mouse_control import MouseControl



from modules.keyboard_control import KeyboardControl







logger = logging.getLogger(__name__)







class MainWindow(QMainWindow):



    """主窗口"""


    VERSION = "1.0.7"
    AUTHOR = "张翰文"


    



    def __init__(self):



        super().__init__()
        self.show_license_dialog()



        self.setup_ui()



        self.init_components()



    



    def setup_ui(self):



        """设置界面"""



        self.setWindowTitle("IDJ 脚本自动化软件")



        self.setGeometry(100, 100, 1000, 650)  # 缩小窗口尺寸



        



        # 设置主窗口样式



        self.setStyleSheet("""



            QMainWindow {



                background-color: #f8f9fa;



            }



            QGroupBox {



                background-color: #ffffff;



                border: 1px solid #e0e0e0;



                border-radius: 5px;



                margin-top: 10px;



            }



            QGroupBox::title {



                subcontrol-origin: margin;



                subcontrol-position: top left;



                padding-left: 10px;



                padding-top: 5px;



                color: #333333;



            }



            QPushButton {

                background-color: #4CAF50;

                color: white;

                border: none;

                padding: 8px 16px;

                border-radius: 4px;

                font-family: "Microsoft YaHei", "SimSun", Arial, sans-serif;

                font-size: 12px;

                min-height: 30px;



            }



            QPushButton:hover {



                background-color: #45a049;



            }



            QPushButton:pressed {



                background-color: #388E3C;



            }



            QPushButton:disabled {



                background-color: #cccccc;



                color: #666666;



            }



        """)



        



        # 创建中心部件



        central_widget = QWidget()



        self.setCentralWidget(central_widget)



        



        # 主布局



        main_layout = QHBoxLayout(central_widget)



        



        # 左控制面板



        left_panel = QWidget()



        left_layout = QVBoxLayout(left_panel)



        left_panel.setFixedWidth(280)



        



        # 窗口绑定区域



        window_group = QGroupBox("窗口绑定")



        window_layout = QVBoxLayout(window_group)



        



        self.window_list = QListWidget()



        self.window_list.setSelectionMode(QListWidget.SingleSelection)



        self.window_list.setMinimumHeight(150)



        window_layout.addWidget(self.window_list)



        



        self.refresh_windows_btn = QPushButton("刷新窗口列表")



        self.refresh_windows_btn.clicked.connect(self.refresh_window_list)



        window_layout.addWidget(self.refresh_windows_btn)



        



        self.bind_window_btn = QPushButton("绑定选中窗口")



        self.bind_window_btn.clicked.connect(self.bind_window)



        self.bind_window_btn.setEnabled(False)



        window_layout.addWidget(self.bind_window_btn)



        



        # 窗口列表选择事件



        self.window_list.currentRowChanged.connect(self.on_window_list_selection_changed)



        



        left_layout.addWidget(window_group)



        



        # 截图工具区域



        # 脚本管理区域



        script_group = QGroupBox("脚本管理")



        script_layout = QVBoxLayout(script_group)



        



        self.script_list = QListWidget()



        self.script_list.setMinimumHeight(100)



        script_layout.addWidget(self.script_list)



        



        script_control_layout = QHBoxLayout()



        self.create_script_btn = QPushButton("创建脚本")



        self.create_script_btn.clicked.connect(self.create_script)



        script_control_layout.addWidget(self.create_script_btn)



        



        self.load_script_btn = QPushButton("加载脚本")



        self.load_script_btn.clicked.connect(self.load_script)



        script_control_layout.addWidget(self.load_script_btn)



        



        script_layout.addLayout(script_control_layout)



        



        left_layout.addWidget(script_group)



        



        # 右侧工作区



        right_panel = QWidget()



        right_layout = QVBoxLayout(right_panel)



        



        # 模式选择标签页



        self.mode_tab = QTabWidget()



        



        # 积木模式页面



        self.block_mode_widget = QWidget()



        self.block_mode_layout = QVBoxLayout(self.block_mode_widget)



        



        self.block_editor = BlockEditor(self)



        self.block_mode_layout.addWidget(self.block_editor)



        



        self.mode_tab.addTab(self.block_mode_widget, "积木模式")



        
        # 代码编辑器（隐藏，仅用于内部代码生成）
        self.code_editor = QTextEdit()
        self.code_editor.setFont(QFont("Consolas", 10))
        self.code_editor.hide()  # 隐藏代码编辑器
        
        # 隐藏标签栏，因为只有一个模式
        self.mode_tab.tabBar().hide()



        



        right_layout.addWidget(self.mode_tab)



        



        # 控制按钮区域



        control_layout = QHBoxLayout()



        control_layout.setSpacing(10)



        



        self.start_btn = QPushButton("开始执行")
        self.start_btn.clicked.connect(self.start_script)
        self.start_btn.setMinimumWidth(100)
        control_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("暂停")
        self.pause_btn.clicked.connect(self.pause_script)
        self.pause_btn.setMinimumWidth(100)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("停止")
        self.stop_btn.clicked.connect(self.stop_script)
        self.stop_btn.setMinimumWidth(100)
        control_layout.addWidget(self.stop_btn)
        
        self.save_script_btn = QPushButton("保存脚本")



        self.save_script_btn.clicked.connect(self.save_script)



        self.save_script_btn.setMinimumWidth(100)



        control_layout.addWidget(self.save_script_btn)



        



        right_layout.addLayout(control_layout)
        
        # 执行选项
        options_layout = QHBoxLayout()
        self.hide_window_checkbox = QCheckBox("执行时隐藏窗口")
        self.hide_window_checkbox.setChecked(False)
        self.hide_window_checkbox.setToolTip("勾选后，执行脚本时将自动隐藏主窗口")
        options_layout.addWidget(self.hide_window_checkbox)
        options_layout.addStretch()
        right_layout.addLayout(options_layout)
        
        # 状态和进度显示
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("状态 就绪")
        status_layout.addWidget(self.status_label)
        
        # 添加当前执行步骤显示
        self.step_label = QLabel("当前步骤: 无")
        self.step_label.setMinimumWidth(150)
        status_layout.addWidget(self.step_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimumWidth(200)
        status_layout.addWidget(self.progress_bar)
        
        right_layout.addLayout(status_layout)



        



        # 使用分割器



        splitter = QSplitter(Qt.Horizontal)



        splitter.addWidget(left_panel)



        splitter.addWidget(right_panel)



        splitter.setSizes([280, 1020])



        



        main_layout.addWidget(splitter)



    



    def show_license_dialog(self):
        """显示用户协议对话框"""
        license_text = """IDJ 版权声明

郑重声明

一、作品名称：IDJ 可视化点击编程工具（以下简称 "本软件"），包括但不限于软件源代码、运行程序、图形界面、功能模块、文档资料、设计元素等全部相关成果。

二、著作权归属：本软件的全部著作权（含著作权法规定的复制权、发行权、信息网络传播权、修改权、保护作品完整权等全部法定权利）均归张翰文（以下简称 "著作权人"）独家所有。著作权人已依法享有该软件的著作权，未经著作权人书面许可，任何单位或个人不得侵犯。

三、权利限制与禁止行为：
• 禁止擅自复制、仿制：任何单位或个人不得未经许可，以任何形式（包括但不限于复制源代码、拷贝运行程序、镜像软件安装包等）复制、仿制本软件的全部或部分内容；
• 禁止修改与破解：不得擅自对本软件进行反向工程、反向编译、反汇编、破解加密措施，或修改软件代码、功能模块、界面设计、版权标识等，不得制作本软件的衍生作品（包括但不限于二次开发、版本篡改、功能增减等）；
• 禁止非法分发与传播：不得未经许可将本软件或其破解版、修改版、仿制版通过网络平台、存储介质等任何渠道进行发布、传播、销售、转让或提供给第三方使用；
• 禁止侵犯衍生权利：不得擅自使用本软件的名称、图标、设计元素、功能逻辑等用于其他产品的开发、推广或商业活动，不得混淆公众对本软件的认知。

四、法律责任：任何单位或个人违反本声明第三条约定的，均构成对著作权人合法权益的侵犯。著作权人有权依据《中华人民共和国著作权法》《中华人民共和国反不正当竞争法》等相关法律法规，要求侵权方立即停止侵权行为、消除影响、赔偿经济损失，并保留追究侵权方法律责任（包括但不限于民事赔偿、行政处罚、刑事责任）的全部权利。

五、其他：本声明自本软件首次发布之日起生效，著作权人对本声明拥有最终解释权；如需获得本软件的使用授权、合作开发等相关权利，需与著作权人签订书面授权协议，具体授权范围、期限、方式等以协议约定为准。

著作权人：张翰文
声明日期：2026年1月9日
"""
        
        dialog = QDialog()
        dialog.setWindowTitle(f"IDJ 用户协议 - 版本 {self.VERSION}")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # 标题
        title_label = QLabel(f"IDJ 可视化点击编程工具 v{self.VERSION}")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        author_label = QLabel(f"作者: {self.AUTHOR}")
        author_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(author_label)
        
        # 协议文本
        text_edit = QTextEdit()
        text_edit.setPlainText(license_text)
        text_edit.setReadOnly(True)
        text_edit.setFont(QFont("Microsoft YaHei", 10))
        layout.addWidget(text_edit)
        
        # 按钮
        btn_layout = QHBoxLayout()
        agree_btn = QPushButton("我已阅读并同意")
        agree_btn.clicked.connect(dialog.accept)
        disagree_btn = QPushButton("不同意并退出")
        disagree_btn.clicked.connect(lambda: sys.exit(0))
        btn_layout.addWidget(agree_btn)
        btn_layout.addWidget(disagree_btn)
        layout.addLayout(btn_layout)
        
        dialog.exec_()

    def init_components(self):



        """初始化组件"""



        # 窗口探测器



        self.window_detector = WindowDetector()



        



        # 截图管理器



        self.screenshot_manager = ScreenshotManager(self)



        



        # 图像识别模块



        self.image_recognizer = ImageRecognition()



        



        # 鼠标控制模块



        self.mouse_controller = MouseControl()



        



        # 键盘控制模块



        self.keyboard_controller = KeyboardControl()
        
        # 脚本录制器
        try:
            from modules.script_recorder import ScriptRecorder
            self.script_recorder = ScriptRecorder()
            logger.info("脚本录制器初始化成功")
        except Exception as e:
            logger.error(f"脚本录制器初始化失败: {e}")
            self.script_recorder = None



        



        # 定时器



        self.refresh_timer = QTimer()



        self.refresh_timer.timeout.connect(self.refresh_window_list)



        self.refresh_timer.start(5000)



        



        # 初始化窗口列表



        self.refresh_window_list()



        



        # 注册全局快捷键Ctrl+Shift+S 用于快速截图
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        self.screenshot_shortcut = QShortcut(QKeySequence("Ctrl+Shift+S"), self)
        self.screenshot_shortcut.activated.connect(self.quick_region_screenshot)
        
        # 注册全局快捷键Ctrl+Shift+X 用于暂停/恢复脚本
        self.pause_shortcut = QShortcut(QKeySequence("Ctrl+Shift+X"), self)
        self.pause_shortcut.activated.connect(self.pause_script)
        
        # 注册全局快捷键Ctrl+Shift+C 用于停止脚本
        self.stop_shortcut = QShortcut(QKeySequence("Ctrl+Shift+C"), self)
        self.stop_shortcut.activated.connect(self.stop_script)
        
        logger.info("全局快捷键已注册: Ctrl+Shift+S(截图), Ctrl+Shift+X(暂停), Ctrl+Shift+C(停止)")

    def refresh_window_list(self):



        """刷新窗口列表"""



        try:



            windows = self.window_detector.get_all_windows()



            self.window_list.clear()



            self.window_list_data = windows  # 保存完整的窗口信息



            for window in windows:



                item_text = f"{window['title']} ({window['process_name']})"



                self.window_list.addItem(item_text)



            



            logger.info(f"窗口列表刷新成功，共找到 {len(windows)} 个窗口")



        except Exception as e:



            logger.error(f"刷新窗口列表失败: {e}")



            QMessageBox.critical(self, "错误", f"刷新窗口列表失败: {str(e)}")



    



    def on_window_list_selection_changed(self, index):



        """窗口列表选择事件"""



        self.bind_window_btn.setEnabled(index >= 0)



    



    def bind_window(self):



        """绑定选中窗口"""



        try:



            selected_index = self.window_list.currentRow()



            if selected_index >= 0 and selected_index < len(self.window_list_data):



                selected_window = self.window_list_data[selected_index]



                hwnd = selected_window["hwnd"]



                



                self.bound_window = hwnd



                self.status_label.setText(f"状态 已绑定窗口- {selected_window['title']}")



                self.bind_window_btn.setEnabled(False)



                logger.info(f"成功绑定窗口: {selected_window['title']} ({selected_window['process_name']})")



                QMessageBox.information(self, "成功", f"已成功绑定窗? {selected_window['title']}\n进程: {selected_window['process_name']}")



                



                # 开始监测绑定的窗口



                self.window_detector.start_monitoring(hwnd)



            else:



                QMessageBox.warning(self, "警告", "请先选择要绑定的窗口")



        except Exception as e:



            logger.error(f"绑定窗口失败: {e}")



            QMessageBox.critical(self, "错误", f"绑定窗口失败: {str(e)}")



    



    def open_screenshot_tool(self):



        """打开截图工具"""



        try:



            tool = self.screenshot_manager.create_screenshot_tool()



            tool.show()



            logger.info("截图工具已打开")



        except Exception as e:



            logger.error(f"打开截图工具失败: {e}")



            QMessageBox.critical(self, "错误", f"打开截图工具失败: {str(e)}")



    



    def quick_region_screenshot(self):



        """快速区域截图"""



        try:

            # 隐藏主窗口，确保在最下层

            self.hide()

            

            # 定义截图完成后的回调函数

            def on_screenshot_complete(pixmap):

                # 截图完成后显示主窗口（无论成功或取消）

                self.show()

                if pixmap:

                    logger.info("快速区域截图成功")

                else:

                    logger.info("快速区域截图已取消")

            

            # 保存对截图工具实例的引用，防止被GC回收

            self.current_screenshot_tool = self.screenshot_manager.capture_region(callback=on_screenshot_complete)

            logger.info("快速区域截图工具已打开")



        except Exception as e:

            logger.error(f"快速区域截图失败 {e}")

            # 确保发生错误时主窗口也能显示

            self.show()

            QMessageBox.critical(self, "错误", f"快速区域截图失败 {str(e)}")



    



    def create_script(self):



        """创建新脚本"""



        try:



            # 清空编辑器



            self.block_editor.clear_script()



            self.code_editor.clear()



            self.status_label.setText("状态 已创建新脚本")



            logger.info("新脚本已创建")



            QMessageBox.information(self, "成功", "新脚本已创建")



        except Exception as e:



            logger.error(f"创建脚本失败: {e}")



            QMessageBox.critical(self, "错误", f"创建脚本失败: {str(e)}")



    



    def load_script(self):



        """加载脚本"""



        try:



            file_path, _ = QFileDialog.getOpenFileName(



                self,



                "加载脚本",



                "",



                "JSON脚本 (*.json);;Python脚本 (*.py);;所有文件(*)"



            )



            



            if file_path:



                # 根据文件扩展名判断脚本类型



                if file_path.endswith(".json"):



                    self.mode_tab.setCurrentIndex(0)



                    self.block_editor.load_script(file_path)



                elif file_path.endswith(".py"):



                    self.mode_tab.setCurrentIndex(1)



                    with open(file_path, 'r', encoding='utf-8') as f:



                        content = f.read()



                        self.code_editor.setPlainText(content)



                



                self.current_script_path = file_path



                self.status_label.setText(f"状态 已加载脚本- {os.path.basename(file_path)}")



                logger.info(f"脚本加载成功: {file_path}")



                QMessageBox.information(self, "成功", "脚本加载成功")



        except Exception as e:



            logger.error(f"加载脚本失败: {e}")



            QMessageBox.critical(self, "错误", f"加载脚本失败: {str(e)}")



    



    def save_script(self):



        """保存脚本"""



        try:



            if hasattr(self, 'current_script_path'):



                file_path = self.current_script_path



            else:



                file_path, _ = QFileDialog.getSaveFileName(



                    self,



                    "保存脚本",



                    "",



                    "JSON脚本 (*.json);;Python脚本 (*.py);;所有文件(*)"



                )



            



            if file_path:



                if file_path.endswith(".json"):



                    self.block_editor.save_script(file_path)



                else:



                    with open(file_path, 'w', encoding='utf-8') as f:



                        f.write(self.code_editor.toPlainText())



                



                self.current_script_path = file_path



                self.status_label.setText(f"状态 脚本已保存- {os.path.basename(file_path)}")



                logger.info(f"脚本保存成功: {file_path}")



                QMessageBox.information(self, "成功", "脚本保存成功")



        except Exception as e:



            logger.error(f"保存脚本失败: {e}")



            QMessageBox.critical(self, "错误", f"保存脚本失败: {str(e)}")



    



    def start_script(self):



        """开始执行脚本"""



        try:



            # 检查是否绑定了窗口



            if not hasattr(self, 'bound_window'):



                QMessageBox.warning(self, "警告", "请先绑定目标窗口")



                return



            
            # 如果勾选了隐藏窗口选项，则隐藏主窗口
            if self.hide_window_checkbox.isChecked():
                self.hide()
            


            # 根据当前模式执行脚本



            if self.mode_tab.currentIndex() == 0:



                # 积木模式



                self.execute_block_script()



            else:



                # 代码模式



                self.execute_code_script()



            



            self.status_label.setText("状态 执行中")



            logger.info("脚本开始执行")



        except Exception as e:



            logger.error(f"执行脚本失败: {e}")
            # 如果出错，确保窗口显示
            self.show()



            QMessageBox.critical(self, "错误", f"执行脚本失败: {str(e)}")



    



    def execute_block_script(self):
        """执行积木模式脚本"""
        try:
            # 获取可执行代码
            executable_code = self.block_editor.get_executable_code()
            logger.info(f"生成的可执行代码:\n{executable_code}")
            
            # 在独立线程中执行代码，避免阻塞UI
            self.execution_thread = ExecutionThread(executable_code)
            self.execution_thread.finished.connect(self.on_execution_finished)
            self.execution_thread.error.connect(self.on_execution_error)
            self.execution_thread.step_changed.connect(self.on_step_changed)
            self.execution_thread.start()
            
            logger.info("积木脚本开始执行")
        except Exception as e:
            logger.error(f"执行积木脚本失败: {e}")
            QMessageBox.critical(self, "执行失败", f"执行积木脚本失败: {str(e)}")
    
    def execute_code_script(self):
        """执行代码模式脚本"""
        try:
            code = self.code_editor.toPlainText()
            logger.info(f"代码模式执行代码:\n{code}")
            
            # 在独立线程中执行代码，避免阻塞UI
            self.execution_thread = ExecutionThread(code)
            self.execution_thread.finished.connect(self.on_execution_finished)
            self.execution_thread.error.connect(self.on_execution_error)
            self.execution_thread.step_changed.connect(self.on_step_changed)
            self.execution_thread.start()
            
            logger.info("代码脚本开始执行")
        except Exception as e:
            logger.error(f"执行代码脚本失败: {e}")
            QMessageBox.critical(self, "执行失败", f"执行代码脚本失败: {str(e)}")
    
    def on_step_changed(self, step_name):
        """执行步骤改变时的回调"""
        self.step_label.setText(f"当前步骤: {step_name}")
        logger.info(f"执行步骤: {step_name}")



    



    def on_mode_changed(self, index):
        """模式切换事件处理（已禁用代码模式）"""
        pass  # 不再需要模式切换处理

    def pause_script(self):
        """暂停/恢复脚本"""
        if hasattr(self, 'execution_thread') and self.execution_thread.isRunning():
            if self.execution_thread.is_paused:
                # 当前是暂停状态，恢复执行
                self.execution_thread.resume()
                self.status_label.setText("状态 执行中")
                self.pause_btn.setText("暂停")
                logger.info("脚本已恢复执行")
            else:
                # 当前是执行状态，暂停执行
                self.execution_thread.pause()
                self.status_label.setText("状态 暂停中")
                self.pause_btn.setText("恢复")
                logger.info("脚本已暂停")



    def stop_script(self):
        """停止脚本"""
        if hasattr(self, 'execution_thread') and self.execution_thread.isRunning():
            self.execution_thread.stop()
            self.status_label.setText("状态 已停止")
            
            # 重置暂停按钮文本
            if hasattr(self, 'pause_btn'):
                self.pause_btn.setText("暂停")
            
            # 如果窗口被隐藏，则恢复显示
            if not self.isVisible():
                self.show()

            logger.info("脚本已停止")
    
    def quick_record_script(self):
        """快速录制脚本"""
        import os
        
        # 隐藏主窗口
        self.hide()
        
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
                    
                    # 显示主窗口
                    self.show()
                    
                    QMessageBox.information(self, "录制完成", 
                        f"脚本已保存到: {script_path}\n共录制 {len(actions)} 个动作")
                else:
                    self.show()
                    QMessageBox.information(self, "录制完成", "未录制任何动作")
            
            self.script_recorder.recording_stopped.connect(on_recording_stopped)
            self.script_recorder.start_recording()
            
        except Exception as e:
            logger.error(f"启动脚本录制失败: {e}")
            self.show()
            QMessageBox.critical(self, "错误", f"启动脚本录制失败: {str(e)}")

    def on_execution_finished(self):
        """执行完成回调"""
        self.status_label.setText("状态 执行完成")
        self.step_label.setText("当前步骤: 无")
        
        # 重置暂停按钮文本
        if hasattr(self, 'pause_btn'):
            self.pause_btn.setText("暂停")
        
        # 如果窗口被隐藏，则恢复显示
        if not self.isVisible():
            self.show()
            
        logger.info("脚本执行完成")
        QMessageBox.information(self, "执行完成", "脚本执行完成")
    
    def on_execution_error(self, error):
        """执行错误回调"""
        self.status_label.setText("状态 执行出错")
        self.step_label.setText("当前步骤: 无")
        
        # 重置暂停按钮文本
        if hasattr(self, 'pause_btn'):
            self.pause_btn.setText("暂停")
        
        # 如果窗口被隐藏，则恢复显示
        if not self.isVisible():
            self.show()
            
        logger.error(f"脚本执行错误: {error}")
        QMessageBox.critical(self, "执行错误", f"脚本执行出错: {str(error)}")











class ExecutionThread(QThread):

    """执行线程类"""
    
    finished = pyqtSignal()
    error = pyqtSignal(str)
    step_changed = pyqtSignal(str)



    



    def __init__(self, code):



        super().__init__()



        self.code = code



        self.is_paused = False



        self.is_stopped = False



    



    def run(self):
        """线程运行方法"""
        try:
            # 创建执行代码的命名空间，包含 step_changed 信号和控制变量
            namespace = {
                '__name__': '__main__',
                'step_changed': self.step_changed,
                'execution_thread': self,  # 传递线程对象以便代码中检查状态
                'check_execution_control': self.check_execution_control  # 检查控制状态的函数
            }
            # 执行代码
            exec(self.code, namespace)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))
    
    def check_execution_control(self):
        """检查执行控制状态，供生成的代码调用"""
        while self.is_paused and not self.is_stopped:
            self.msleep(100)  # 暂停时每100ms检查一次
        
        if self.is_stopped:
            raise InterruptedError("脚本已被用户停止")
        
        return True



    



    def pause(self):



        """暂停执行"""



        self.is_paused = True
        logger.info("执行线程已暂停")
    
    def resume(self):
        """恢复执行"""
        self.is_paused = False
        logger.info("执行线程已恢复")



    



    def stop(self):



        """停止执行"""



        self.is_stopped = True



        self.quit()







if __name__ == "__main__":



    import sys



    from PyQt5.QtWidgets import QApplication



    



    app = QApplication(sys.argv)



    window = MainWindow()



    window.show()



    sys.exit(app.exec_())



