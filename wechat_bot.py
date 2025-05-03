import wxauto
import time
import os
import pyautogui
import pyperclip
import win32gui
import win32con
import logging

class WeChatBot:
    def __init__(self, log_func=print):
        self.log_func = log_func
        self.wx = None
        self.logged_in = False
        self.max_retries = 3
        self.retry_delay = 2

    def login(self, block=True):
        self.log_func('正在连接桌面端微信...')
        
        for attempt in range(self.max_retries):
            try:
                # 尝试初始化微信对象
                self.wx = wxauto.WeChat()
                
                # 检查微信是否已登录
                if not self.wx.GetSessionList():
                    self.log_func('未检测到已登录的微信，请先登录微信桌面版')
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay)
                        continue
                    return False
                
                self.logged_in = True
                self.log_func('微信连接成功！')
                return True
                
            except Exception as e:
                self.log_func(f'微信连接失败（尝试 {attempt + 1}/{self.max_retries}）：{str(e)}')
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                return False

    def activate_wechat(self):
        """激活微信窗口"""
        try:
            # 查找微信窗口
            hwnd = win32gui.FindWindow("WeChatMainWndForPC", None)
            if not hwnd:
                # 尝试其他可能的窗口标题
                hwnd = win32gui.FindWindow(None, "微信")
                if not hwnd:
                    self.log_func('无法找到微信窗口')
                    return False

            # 如果窗口最小化，则恢复
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 激活窗口
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            return True
            
        except Exception as e:
            self.log_func(f'激活微信窗口失败：{str(e)}')
            return False

    def find_friend(self, name):
        """根据昵称查找联系人"""
        try:
            self.log_func(f'正在搜索联系人：{name}')
            
            # 确保微信窗口是激活的
            if not self.activate_wechat():
                self.log_func('无法激活微信窗口')
                return None
            
            # 复制要搜索的名称到剪贴板
            pyperclip.copy(name)
            time.sleep(0.5)
            
            # 模拟Ctrl+F快捷键
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.5)
            
            # 粘贴搜索内容
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            
            # 按回车键确认搜索
            pyautogui.press('enter')
            time.sleep(1)
            
            return name
            
        except Exception as e:
            self.log_func(f'查找联系人失败：{str(e)}')
            return None

    def send_message(self, name, msg):
        try:
            self.log_func(f'准备发送消息给：{name}')
            
            # 查找并打开聊天窗口
            if not self.find_friend(name):
                self.log_func(f'未找到联系人：{name}')
                return False
            
            # 确保聊天窗口是激活的
            time.sleep(0.5)
            
            # 发送消息
            self.log_func(f'正在发送消息：{msg}')
            # 复制消息到剪贴板
            pyperclip.copy(msg)
            time.sleep(0.5)
            # 粘贴消息
            pyautogui.hotkey('ctrl', 'v')
            time.sleep(0.5)
            # 发送消息
            pyautogui.press('enter')
            time.sleep(0.5)
            
            self.log_func(f'消息发送成功：{name}')
            return True
            
        except Exception as e:
            self.log_func(f'发送失败：{name}，原因：{str(e)}')
            return False

    def batch_send(self, name_list, msg):
        success, fail = [], []
        for name in name_list:
            if self.send_message(name, msg):
                success.append(name)
            else:
                fail.append(name)
            time.sleep(1)  # 防止频繁操作
        return success, fail 