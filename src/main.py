
import sys
import os

# 将 src/method 目录添加到模块搜索路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'method'))

# 导入具体的模块文件
import NetWorkTest_Encoding_Simulator as mt
# 入口：输入一串0和1
if __name__ == "__main__":
    s = input("请输入二进制比特串（如 11010010）: ")
    data = [int(ch) for ch in s if ch in '01']
    mt.plot_all(data)
