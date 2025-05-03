import pandas as pd
import os

def parse_name_list(file_path):
    """
    解析Excel或CSV名单文件，返回姓名列表。
    假设名单文件有一列为"姓名"或"name"。
    """
    ext = os.path.splitext(file_path)[-1].lower()
    if ext in ['.xls', '.xlsx']:
        df = pd.read_excel(file_path)
    elif ext == '.csv':
        df = pd.read_csv(file_path)
    else:
        raise ValueError('仅支持Excel或CSV文件')
    # 尝试找到姓名列
    for col in df.columns:
        if '姓名' in col or 'name' in col.lower():
            return df[col].dropna().astype(str).tolist()
    # 如果没有找到，默认取第一列
    return df.iloc[:, 0].dropna().astype(str).tolist() 