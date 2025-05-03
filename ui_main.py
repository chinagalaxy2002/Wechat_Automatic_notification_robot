import sys
import traceback
import logging
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout,
    QFileDialog, QApplication, QProgressBar, QMessageBox, QFrame,
    QGroupBox, QScrollArea, QSplitter, QTableWidget, QTableWidgetItem,
    QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
import pandas as pd
import wxauto
import pyautogui
import pyperclip
import time

# 配置日志
log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wechat_notifier.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理函数"""
    logging.error("未捕获的异常", exc_info=(exc_type, exc_value, exc_traceback))
    QMessageBox.critical(None, "错误", f"程序发生错误：\n{str(exc_value)}\n\n详细信息已记录到日志文件。")

# 设置全局异常处理器
sys.excepthook = handle_exception

class MainWindow(QWidget):
    start_send_signal = pyqtSignal(str, list)
    wx = None

    def __init__(self):
        try:
            super().__init__()
            logging.info("初始化主窗口")
            self.setWindowTitle('微信通知助手')
            self.resize(1200, 800)
            self.setStyleSheet("""
                QWidget {
                    font-family: 'Microsoft YaHei';
                    font-size: 23px;
                    background-color: #f8f9fa;
                }
                QGroupBox {
                    border: none;
                    margin-top: 1ex;
                    font-weight: bold;
                    color: #2c3e50;
                    font-size: 25px;
                    background-color: white;
                    border-radius: 12px;
                    padding: 15px;
                    margin-top: 20px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 15px;
                    padding: 0 5px 0 5px;
                    color: #2c3e50;
                }
                QPushButton {
                    background-color: #4a90e2;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    min-width: 150px;
                    font-weight: bold;
                    font-size: 23px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                QPushButton:hover {
                    background-color: #357abd;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
                }
                QPushButton:pressed {
                    background-color: #2c6aa0;
                    box-shadow: 0 1px 2px rgba(0,0,0,0.1);
                }
                QPushButton:disabled {
                    background-color: #bdc3c7;
                    box-shadow: none;
                }
                QPushButton#upload_btn {
                    background-color: #2ecc71;
                    font-size: 21px;
                }
                QPushButton#upload_btn:hover {
                    background-color: #27ae60;
                }
                QPushButton#login_btn {
                    background-color: #4a90e2;
                }
                QPushButton#login_btn:hover {
                    background-color: #357abd;
                }
                QPushButton#send_btn {
                    background-color: #e74c3c;
                }
                QPushButton#send_btn:hover {
                    background-color: #c0392b;
                }
                QTextEdit {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 15px;
                    background-color: white;
                    selection-background-color: #4a90e2;
                    font-size: 23px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                QTextEdit:focus {
                    border: 2px solid #4a90e2;
                    box-shadow: 0 4px 8px rgba(74,144,226,0.2);
                }
                QProgressBar {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    text-align: center;
                    background-color: white;
                    height: 30px;
                    font-size: 23px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                QProgressBar::chunk {
                    background-color: #2ecc71;
                    border-radius: 6px;
                }
                QLabel#file_label {
                    color: #7f8c8d;
                    padding: 12px;
                    background-color: white;
                    border-radius: 8px;
                    border: 2px solid #e0e0e0;
                    font-size: 23px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                }
                QSplitter::handle {
                    background-color: #e0e0e0;
                    height: 2px;
                }
                QTableWidget {
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: white;
                    gridline-color: #e0e0e0;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                    font-size: 23px;
                }
                QTableWidget::item {
                    padding: 15px;
                    border-bottom: 1px solid #e0e0e0;
                }
                QTableWidget::item:selected {
                    background-color: #4a90e2;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border: none;
                    border-bottom: 2px solid #e0e0e0;
                    font-weight: bold;
                    font-size: 23px;
                }
            """)
            self.init_ui()
            self.text_content = ''
            self.name_list = []
            logging.info("主窗口初始化完成")
        except Exception as e:
            logging.error(f"初始化失败: {str(e)}")
            raise

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # 创建分割器
        splitter = QSplitter(Qt.Vertical)
        splitter.setHandleWidth(2)

        # 上半部分：通知内容和名单
        top_widget = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setSpacing(30)
        top_layout.setContentsMargins(20, 20, 20, 20)

        # 通知内容组
        notice_group = QGroupBox("通知内容")
        notice_layout = QVBoxLayout()
        notice_layout.setSpacing(15)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText('请输入通知内容，或点击下方按钮上传txt文件...')
        self.text_edit.setMinimumHeight(400)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 25px;
                line-height: 2.0;
                padding: 25px;
            }
        """)
        
        upload_btn = QPushButton('上传通知文本')
        upload_btn.setObjectName("upload_btn")
        upload_btn.clicked.connect(self.upload_text_file)
        
        notice_layout.addWidget(self.text_edit)
        notice_layout.addWidget(upload_btn)
        notice_group.setLayout(notice_layout)

        # 名单组
        name_group = QGroupBox("待通知人员名单")
        name_layout = QVBoxLayout()
        name_layout.setSpacing(15)
        
        self.btn_upload_name = QPushButton('上传名单Excel')
        self.btn_upload_name.setObjectName("upload_btn")
        self.btn_upload_name.clicked.connect(self.upload_name_file)
        
        # 创建表格显示名单
        self.name_table = QTableWidget()
        self.name_table.setColumnCount(2)
        self.name_table.setHorizontalHeaderLabels(['姓名', '备注'])
        self.name_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.name_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.name_table.setMinimumHeight(400)
        self.name_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        name_layout.addWidget(self.btn_upload_name)
        name_layout.addWidget(self.name_table)
        name_group.setLayout(name_layout)

        top_layout.addWidget(notice_group, 2)
        top_layout.addWidget(name_group, 1)
        top_widget.setLayout(top_layout)

        # 下半部分：操作和日志
        bottom_widget = QWidget()
        bottom_layout = QVBoxLayout()
        bottom_layout.setSpacing(15)
        bottom_layout.setContentsMargins(20, 20, 20, 20)

        # 操作按钮组
        button_group = QGroupBox("操作")
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        
        self.btn_login = QPushButton('连接桌面端微信')
        self.btn_login.setObjectName("login_btn")
        self.btn_send = QPushButton('开始发送')
        self.btn_send.setObjectName("send_btn")
        self.btn_send.setEnabled(False)
        
        button_layout.addStretch()
        button_layout.addWidget(self.btn_login)
        button_layout.addWidget(self.btn_send)
        button_layout.addStretch()
        button_group.setLayout(button_layout)

        # 进度条
        progress_group = QGroupBox("发送进度")
        progress_layout = QVBoxLayout()
        
        self.progress = QProgressBar()
        self.progress.setValue(0)
        
        progress_layout.addWidget(self.progress)
        progress_group.setLayout(progress_layout)

        # 日志组
        log_group = QGroupBox("日志")
        log_layout = QVBoxLayout()
        
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMinimumHeight(100)
        self.log_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                font-family: 'Consolas', 'Microsoft YaHei';
                font-size: 23px;
                line-height: 1.8;
            }
        """)
        
        log_layout.addWidget(self.log_edit)
        log_group.setLayout(log_layout)

        bottom_layout.addWidget(button_group)
        bottom_layout.addWidget(progress_group)
        bottom_layout.addWidget(log_group)
        bottom_widget.setLayout(bottom_layout)

        # 添加组件到分割器
        splitter.addWidget(top_widget)
        splitter.addWidget(bottom_widget)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        # 连接按钮点击事件
        self.btn_login.clicked.connect(self.connect_wechat)
        self.btn_send.clicked.connect(self.start_send)

    def upload_text_file(self):
        file, _ = QFileDialog.getOpenFileName(self, '选择通知文本', '', 'Text Files (*.txt)')
        if file:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            self.text_edit.setText(content)
            self.text_content = content

    def upload_name_file(self):
        try:
            file, _ = QFileDialog.getOpenFileName(self, '选择名单文件', '', 'Excel/CSV Files (*.xls *.xlsx *.csv)')
            if file:
                logging.info(f"开始导入文件: {file}")
                if file.endswith('.csv'):
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)
                
                # 清空表格
                self.name_table.setRowCount(0)
                
                # 添加数据到表格
                for index, row in df.iterrows():
                    row_position = self.name_table.rowCount()
                    self.name_table.insertRow(row_position)
                    
                    # 假设第一列是姓名，第二列是备注
                    self.name_table.setItem(row_position, 0, QTableWidgetItem(str(row.iloc[0])))
                    if len(row) > 1:
                        self.name_table.setItem(row_position, 1, QTableWidgetItem(str(row.iloc[1])))
                
                self.name_file_path = file
                self.log(f"成功导入名单文件：{file}，共 {len(df)} 条记录")
                logging.info(f"成功导入文件，共 {len(df)} 条记录")
                
        except Exception as e:
            error_msg = f"导入名单文件失败：{str(e)}"
            logging.error(error_msg)
            self.log(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def connect_wechat(self):
        try:
            logging.info("尝试连接微信")
            self.log("正在连接微信...")
            self.btn_login.setEnabled(False)
            self.btn_login.setText("连接中...")
            
            # 尝试连接微信
            self.wx = wxauto.WeChat()
            if self.wx:
                self.log("微信连接成功！")
                self.btn_send.setEnabled(True)
                self.btn_login.setText("已连接")
                logging.info("微信连接成功")
            else:
                self.log("微信连接失败，请确保微信已登录")
                self.btn_login.setEnabled(True)
                self.btn_login.setText("连接桌面端微信")
                logging.error("微信连接失败")
        except Exception as e:
            error_msg = f"连接微信失败：{str(e)}"
            logging.error(error_msg)
            self.log(error_msg)
            self.btn_login.setEnabled(True)
            self.btn_login.setText("连接桌面端微信")
            QMessageBox.critical(self, "错误", error_msg)

    def start_send(self):
        try:
            if not self.wx:
                self.log("请先连接微信")
                return

            content = self.get_text_content()
            if not content:
                self.log("请输入通知内容")
                return

            # 获取名单
            name_list = []
            for row in range(self.name_table.rowCount()):
                name = self.name_table.item(row, 0).text()
                if name:
                    name_list.append(name)

            if not name_list:
                self.log("请先导入名单")
                return

            self.log(f"开始发送通知，共 {len(name_list)} 人")
            self.progress.setMaximum(len(name_list))
            self.progress.setValue(0)

            # 发送消息
            for i, name in enumerate(name_list):
                try:
                    self.log(f"正在发送给 {name}...")
                    # 复制内容到剪贴板
                    pyperclip.copy(content)
                    
                    # 使用更简单的方式发送消息
                    try:
                        # 点击搜索框
                        pyautogui.click(100, 100)  # 需要根据实际微信窗口位置调整坐标
                        time.sleep(0.5)
                        
                        # 输入联系人名称
                        pyperclip.copy(name)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(1)
                        
                        # 点击联系人
                        pyautogui.click(100, 150)  # 需要根据实际微信窗口位置调整坐标
                        time.sleep(1)
                        
                        # 粘贴并发送消息
                        pyperclip.copy(content)
                        pyautogui.hotkey('ctrl', 'v')
                        time.sleep(0.5)
                        pyautogui.press('enter')
                        time.sleep(1)
                        
                        self.progress.setValue(i + 1)
                        self.log(f"已发送给 {name}")
                    except Exception as e:
                        self.log(f"发送给 {name} 失败：{str(e)}")
                        logging.error(f"发送给 {name} 失败: {str(e)}")
                        
                except Exception as e:
                    self.log(f"发送给 {name} 失败：{str(e)}")
                    logging.error(f"发送给 {name} 失败: {str(e)}")

            self.log("发送完成！")
        except Exception as e:
            error_msg = f"发送过程出错：{str(e)}"
            logging.error(error_msg)
            self.log(error_msg)
            QMessageBox.critical(self, "错误", error_msg)

    def log(self, msg):
        try:
            self.log_edit.append(msg)
            self.log_edit.ensureCursorVisible()
            logging.info(msg)
        except Exception as e:
            logging.error(f"日志记录失败: {str(e)}")

    def set_progress(self, value):
        self.progress.setValue(value)

    def get_text_content(self):
        return self.text_edit.toPlainText().strip()

    def get_name_file_path(self):
        return getattr(self, 'name_file_path', None)

if __name__ == '__main__':
    try:
        logging.info("启动程序")
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        logging.info("程序启动成功")
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"程序启动失败: {str(e)}")
        QMessageBox.critical(None, "错误", f"程序启动失败：\n{str(e)}") 