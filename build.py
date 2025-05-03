import PyInstaller.__main__
import os
import shutil

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 清理旧的构建文件
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

PyInstaller.__main__.run([
    'ui_main.py',
    '--name=微信通知助手',
    '--onefile',  # 生成单个可执行文件
    '--windowed',
    '--clean',
    '--noconfirm',
    '--debug=all',  # 添加调试信息
    '--log-level=DEBUG',  # 设置日志级别为DEBUG
    '--add-data=requirements.txt;.',
    # PyQt5相关
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    # 数据处理相关
    '--hidden-import=pandas',
    '--hidden-import=numpy',  # 添加 numpy 隐藏导入
    '--hidden-import=openpyxl',
    '--hidden-import=xlrd',
    # 微信相关
    '--hidden-import=wxauto',
    '--hidden-import=itchat',
    '--hidden-import=pyautogui',
    '--hidden-import=pyperclip',
    '--hidden-import=pywin32',
    # 收集所有必要的包
    '--collect-all=wxauto',
    '--collect-all=itchat',
    '--collect-all=pyautogui',
    '--collect-all=pyperclip',
    '--collect-all=pywin32',
    '--collect-all=PyQt5',
    '--collect-all=pandas',
    '--collect-all=numpy',  # 添加 numpy 收集
    '--collect-all=openpyxl',
    '--collect-all=xlrd',
    # 添加额外的DLL
    '--add-binary=C:\\Windows\\System32\\msvcp140.dll;.',
    '--add-binary=C:\\Windows\\System32\\vcruntime140.dll;.',
    '--add-binary=C:\\Windows\\System32\\vcruntime140_1.dll;.',
    # 排除不必要的包
    '--exclude-module=matplotlib',
    '--exclude-module=scipy',
    '--exclude-module=PyQt5.QtWebEngine',
    '--exclude-module=PyQt5.QtWebEngineCore',
    '--exclude-module=PyQt5.QtWebEngineWidgets',
]) 