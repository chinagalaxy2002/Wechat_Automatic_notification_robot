import sys
import logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from ui_main import MainWindow
from wechat_bot import WeChatBot
from utils import parse_name_list

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('wechat_notifier.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class SendThread(QThread):
    progress_signal = pyqtSignal(int)
    log_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(list, list)

    def __init__(self, bot, name_list, msg):
        super().__init__()
        self.bot = bot
        self.name_list = name_list
        self.msg = msg
        self._is_running = True

    def run(self):
        total = len(self.name_list)
        success, fail = [], []
        for idx, name in enumerate(self.name_list):
            if not self._is_running:
                break
            if self.bot.send_message(name, self.msg):
                success.append(name)
            else:
                fail.append(name)
            self.progress_signal.emit(int((idx+1)/total*100))
        self.finished_signal.emit(success, fail)

    def stop(self):
        self._is_running = False
        self.wait()

def main():
    try:
        logging.info("程序启动")
        app = QApplication(sys.argv)
        win = MainWindow()
        bot = WeChatBot(log_func=win.log)
        send_thread = None

        def on_login():
            try:
                if bot.login():
                    win.log('登录成功！')
                    win.btn_send.setEnabled(True)
                else:
                    win.log('登录失败，请确保微信已登录')
                    QMessageBox.warning(win, '警告', '登录失败，请确保微信已登录')
            except Exception as e:
                logging.error(f"登录失败: {str(e)}", exc_info=True)
                win.log(f'登录失败：{str(e)}')
                QMessageBox.critical(win, '错误', f'微信登录失败：{str(e)}')

        def on_send():
            nonlocal send_thread
            msg = win.get_text_content()
            name_file = win.get_name_file_path()
            if not msg:
                QMessageBox.warning(win, '提示', '请填写通知内容')
                return
            if not name_file:
                QMessageBox.warning(win, '提示', '请上传名单文件')
                return
            try:
                name_list = parse_name_list(name_file)
            except Exception as e:
                logging.error(f"名单解析失败: {str(e)}", exc_info=True)
                win.log(f'名单解析失败：{str(e)}')
                QMessageBox.critical(win, '错误', f'名单解析失败：{str(e)}')
                return
            win.log(f'共需通知 {len(name_list)} 人')
            win.set_progress(0)
            win.btn_send.setEnabled(False)
            win.btn_login.setEnabled(False)
            
            send_thread = SendThread(bot, name_list, msg)
            send_thread.progress_signal.connect(win.set_progress)
            send_thread.log_signal.connect(win.log)
            
            def on_finished(success, fail):
                win.log(f'发送完成，成功：{len(success)}，失败：{len(fail)}')
                if fail:
                    win.log('未匹配/发送失败名单：' + ', '.join(fail))
                win.btn_send.setEnabled(True)
                win.btn_login.setEnabled(True)
                send_thread = None
            
            send_thread.finished_signal.connect(on_finished)
            send_thread.start()

        def closeEvent(event):
            if send_thread and send_thread.isRunning():
                send_thread.stop()
            event.accept()

        win.btn_login.clicked.connect(on_login)
        win.btn_send.clicked.connect(on_send)
        win.closeEvent = closeEvent
        win.show()
        logging.info("主窗口初始化完成")
        sys.exit(app.exec_())
    except Exception as e:
        logging.error("未捕获的异常", exc_info=True)
        QMessageBox.critical(None, '错误', f'程序发生错误：{str(e)}')
        sys.exit(1)

if __name__ == '__main__':
    main() 