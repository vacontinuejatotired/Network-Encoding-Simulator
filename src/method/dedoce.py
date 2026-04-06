import matplotlib
matplotlib.use('TkAgg')  # 换用TkAgg后端，PyCharm里显示更稳
import matplotlib.pyplot as plt

# ==================== 四种编码的解码器 ====================

def decode_nrz(signal, per_bit=16):
    """
    NRZ（不归零码）解码
    规则：高电平（>=0.5）表示 1，低电平（<0.5）表示 0
    取每个比特中间位置的采样点进行判断
    """
    print("NRZ解码:", signal)
    print("采样点总个数",len(signal))
    print("样本采样点个数", per_bit)
    print("样本理论bit数", len(signal) // per_bit)
    bits = []
    
    for i in range(0, len(signal), per_bit):
        # 取每个比特中间位置的采样点
        mid = i + per_bit // 2
        level = signal[mid]
        
        if level >= 0.5:
            print("1")
            bits.append(1)
        else:
            print("0")
            bits.append(0)
    
    print(bits)
    return bits


def decode_manchester(signal, per_bit=16):
    """
    曼彻斯特编码解码
    规则：低->高（前半低后半高）表示 1，高->低（前半高后半低）表示 0
    """
    print("曼彻斯特解码:", signal)
    print("样本采样点个数", per_bit)
    bits = []
    half = per_bit // 2
    
    for i in range(0, len(signal), per_bit):
        # 取前半段中间位置
        first_mid = i + half // 2
        # 取后半段中间位置
        second_mid = i + half + half // 2
        
        first = signal[first_mid]
        second = signal[second_mid]
        
        # 低->高 是 1，高->低 是 0
        if first < 0.5 and second >= 0.5:
            print("1")
            bits.append(1)
        else:
            print("0")
            bits.append(0)
    
    print(bits)
    return bits


def decode_diff_manchester(signal, per_bit=16):
    """
    差分曼彻斯特编码解码
    规则：每个比特中间有跳变
          比特开始处有跳变 = 0，无跳变 = 1
    """
    print("差分曼彻斯特解码:", signal)
    print("样本采样点个数", per_bit)
    bits = []
    half = per_bit // 2
    
    # 上一个比特结束时的电平（初始假设为高电平）
    prev_end = 1.0
    
    for i in range(0, len(signal), per_bit):
        # 取比特开始处的电平（跳过前几个点，避开可能的跳变边缘）
        start_idx = i + 2
        start_level = signal[start_idx]
        
        # 判断开始处是否有跳变
        if abs(start_level - prev_end) > 0.5:
            bits.append(0)   # 有跳变 = 0
        else:
            bits.append(1)   # 无跳变 = 1
        
        # 更新上一个结束电平（取这个比特结束处）
        end_idx = i + per_bit - 2
        prev_end = signal[end_idx]
    
    print(bits)
    return bits


def decode_rz(signal, per_bit=16):
    """
    RZ（归零码）解码
    规则：正脉冲（电平 > 0.5）表示 1，负脉冲（电平 < -0.5）表示 0
    取每个比特前半段中间位置的采样点进行判断
    """
    print("RZ解码:", signal)
    print("样本采样点个数", per_bit)
    bits = []
    half = per_bit // 2
    
    for i in range(0, len(signal), per_bit):
        # 取前半段中间位置的采样点（脉冲的最高点或最低点）
        mid = i + half // 2
        level = signal[mid]
        
        if level > 0.5:
            print("1")
            bits.append(1)      # 正脉冲 = 1
        elif level < -0.5:
            print("0")
            bits.append(0)      # 负脉冲 = 0
        else:
            # 电平接近 0，可能是噪声或错误，默认当作 0
            print("0")
            bits.append(0)
    
    print(bits)
    return bits

if __name__ == "__main__":
    s = input("请输入采样数组（如 11111111111111110000000000000000）: ")
    data = [int(ch) for ch in s if ch in '01']
    print("解码结果",decode_nrz(data))
    print("解码结果",decode_rz(data))
    print("解码结果",decode_manchester(data))
    print("解码结果",decode_diff_manchester(data))