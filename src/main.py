import matplotlib.pyplot as plt
import sys
import os

# 将 src/method 目录添加到模块搜索路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'method'))

# 导入具体的模块文件
import NetWorkTest_Encoding_Simulator as mt

if __name__ == "__main__":
    s = input("请输入数据: ")
    # 过滤非 0/1 字符并转换为整数列表
    data = [int(ch) for ch in s if ch in '01']
    
    # 调用曼彻斯特编码方法
    mt.Manchester(data)
