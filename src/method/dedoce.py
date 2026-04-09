from uu import decode
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

def decode_nrz(signal, sample_nums=10):
    """
    NRZ（不归零码）解码
    规则：高电平（>=0.5）表示 1，低电平（<0.5）表示 0
    取每个比特中间位置的采样点进行判断
    
    参数:
        signal: 采样电平列表（连续的电压值）
        sample_nums: 每个比特的采样点数
    返回:
        解码后的比特列表
    """
    bits = []
    total_bits = len(signal) // sample_nums
    
    for i in range(total_bits):
        # 取每个比特中间位置的采样点（避开边缘）
        mid = i * sample_nums + sample_nums // 2
        level = signal[mid]
        
        if level >= 0.5:
            bits.append(1)
        else:
            bits.append(0)
    
    return bits


def decode_manchester(signal, sample_nums=10):
    """
    曼彻斯特编码解码
    规则：低->高（前半低后半高）表示 0，高->低（前半高后半低）表示 1
    注意：这里与你编码器保持一致（0=上升沿，1=下降沿）
    
    参数:
        signal: 采样电平列表（连续的电压值）
        sample_nums: 每个比特的采样点数
    返回:
        解码后的比特列表
    """
    bits = []
    total_bits = len(signal) // sample_nums
    half = sample_nums // 2
    
    for i in range(total_bits):
        start_idx = i * sample_nums
        # 取前半段中间位置
        first_mid = start_idx + half // 2
        # 取后半段中间位置
        second_mid = start_idx + half + half // 2
        
        first = signal[first_mid]
        second = signal[second_mid]
        
        # 低->高（0→1）表示 0，高->低（1→0）表示 1
        if first < 0.5 and second >= 0.5:
            bits.append(0)   # 上升沿 = 0
        elif first >= 0.5 and second < 0.5:
            bits.append(1)   # 下降沿 = 1
        else:
            # 噪声过大，根据前半段电平判断
            bits.append(0 if first < 0.5 else 1)
    
    return bits


def decode_diff_manchester(signal, sample_nums=10, initial_level=1):
    """
    差分曼彻斯特编码解码
    规则：每个比特中间有跳变
          比特开始处有跳变 = 0，无跳变 = 1
    
    参数:
        signal: 采样电平列表（连续的电压值）
        sample_nums: 每个比特的采样点数
        initial_level: 初始电平（与编码器保持一致，默认高电平1）
    返回:
        解码后的比特列表
    """
    bits = []
    total_bits = len(signal) // sample_nums
    half = sample_nums // 2
    
    # 上一个比特结束时的电平（初始为假设的起始电平）
    prev_end = float(initial_level)
    
    for i in range(total_bits):
        start_idx = i * sample_nums
        # 取比特开始处的电平（跳过前2个点，避开可能的跳变边缘）
        start_level = signal[start_idx + 2] if sample_nums > 4 else signal[start_idx]
        
        # 判断开始处是否有跳变（电平变化超过0.5）
        if abs(start_level - prev_end) > 0.5:
            bits.append(0)   # 有跳变 = 0
        else:
            bits.append(1)   # 无跳变 = 1
        
        # 更新上一个结束电平（取这个比特结束处，避开后2个点）
        end_idx = start_idx + sample_nums - 2
        prev_end = signal[end_idx] if end_idx < len(signal) else signal[-1]
    
    return bits


def decode_rz(signal, sample_nums=10):
    """
    RZ（归零码）解码
    规则：正脉冲（电平 > 0.5）表示 1，负脉冲（电平 < -0.5）表示 0
    取每个比特前半段中间位置的采样点进行判断
    
    参数:
        signal: 采样电平列表（连续的电压值）
        sample_nums: 每个比特的采样点数
    返回:
        解码后的比特列表
    """
    bits = []
    total_bits = len(signal) // sample_nums
    half = sample_nums // 2
    
    for i in range(total_bits):
        start_idx = i * sample_nums
        # 取前半段中间位置（脉冲的最高点或最低点）
        mid = start_idx + half // 2
        level = signal[mid]
        
        if level > 0.5:
            bits.append(1)      # 正脉冲 = 1
        elif level < -0.5:
            bits.append(0)      # 负脉冲 = 0
        else:
            # 电平接近 0，可能是噪声或错误，根据周围点判断
            # 检查前半段的最大值
            segment = signal[start_idx:start_idx + half]
            if max(segment) > 0.5:
                bits.append(1)
            else:
                bits.append(0)
    
    return bits


def add_noise(signal, noise_level=0.1):
    """
    给信号添加高斯噪声，测试解码器鲁棒性
    
    参数:
        signal: 原始电平列表
        noise_level: 噪声强度（标准差）
    返回:
        添加噪声后的电平列表
    """
    noise = np.random.normal(0, noise_level, len(signal))
    noisy_signal = [s + n for s, n in zip(signal, noise)]
    return noisy_signal


def test_decoder(encode_func, decode_func, data, sample_nums=10, add_noise_flag=False, noise_level=0.1):
    """
    测试编码-解码一致性
    
    参数:
        encode_func: 编码函数
        decode_func: 解码函数
        data: 原始比特列表
        sample_nums: 每比特采样点数
        add_noise_flag: 是否添加噪声
        noise_level: 噪声强度
    返回:
        (是否成功, 原始数据, 解码后数据)
    """
    # 编码
    signal = encode_func(data, sample_nums)
    
    # 可选：添加噪声
    if add_noise_flag:
        signal = add_noise(signal, noise_level)
    
    # 解码
    decoded = decode_func(signal, sample_nums)
    
    # 验证
    success = data == decoded
    return success, data, decoded


# ==================== 将编码函数转换为返回采样列表的版本 ====================

def encode_nrz_to_signal(data, sample_nums=10):
    """NRZ编码，返回采样电平列表"""
    signal = []
    for bit in data:
        signal.extend([bit] * sample_nums)
    return signal


def encode_manchester_to_signal(data, sample_nums=10):
    """曼彻斯特编码，返回采样电平列表（0=上升沿，1=下降沿）"""
    signal = []
    half = sample_nums // 2
    if sample_nums % 2 == 1:
        first_half = half + 1
        second_half = half
    else:
        first_half = half
        second_half = half
    
    for bit in data:
        if bit == 1:
            # 1: 高->低（下降沿）
            signal.extend([1] * first_half)
            signal.extend([0] * second_half)
        else:
            # 0: 低->高（上升沿）
            signal.extend([0] * first_half)
            signal.extend([1] * second_half)
    return signal


def encode_diff_manchester_to_signal(data, sample_nums=10, initial_level=1):
    """差分曼彻斯特编码，返回采样电平列表"""
    signal = []
    half = sample_nums // 2
    if sample_nums % 2 == 1:
        first_half = half + 1
        second_half = half
    else:
        first_half = half
        second_half = half
    
    current_level = initial_level
    
    for bit in data:
        if bit == 0:
            # 0: 开始处有跳变
            current_level = 1 - current_level
        
        # 前半段
        signal.extend([current_level] * first_half)
        # 中间跳变
        current_level = 1 - current_level
        # 后半段
        signal.extend([current_level] * second_half)
    
    return signal


def encode_rz_to_signal(data, sample_nums=10):
    """RZ编码，返回采样电平列表（正脉冲=1，负脉冲=0）"""
    signal = []
    # 三段比例：前段0.25，中段0.5，后段0.25
    first_samples = max(1, sample_nums // 4)
    mid_samples = max(1, sample_nums // 2)
    last_samples = sample_nums - first_samples - mid_samples
    if last_samples < 1:
        last_samples = 1
        first_samples = max(1, first_samples - 1)
        mid_samples = sample_nums - first_samples - last_samples
    
    for bit in data:
        pulse = 1 if bit == 1 else -1
        signal.extend([0] * first_samples)
        signal.extend([pulse] * mid_samples)
        signal.extend([0] * last_samples)
    
    return signal


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试数据：原始比特 [1, 0, 1, 0]
    sample_nums = 16
    
    # 从上面的测试结果中提取的编码结果（写死）
    nrz_signal = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 
                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    
    manchester_signal = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 
                         0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 
                         1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 
                         0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    
    diff_manchester_signal = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 
                               1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 
                               0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 
                               0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]
    
    rz_signal = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 
                 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0, 
                 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 
                 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0]
    
    # 解码测试
    print(f"原始比特: [1, 0, 1, 0]")
    print(f"每比特采样点: {sample_nums}")
    print()
    
    # NRZ解码
    decoded_nrz = decode_nrz(nrz_signal, sample_nums)
    print(f"NRZ解码结果:      {decoded_nrz}")
    
    # 曼彻斯特解码
    decoded_manchester = decode_manchester(manchester_signal, sample_nums)
    print(f"曼彻斯特解码结果:  {decoded_manchester}")
    
    # 差分曼彻斯特解码
    decoded_diff = decode_diff_manchester(diff_manchester_signal, sample_nums)
    print(f"差分曼彻斯特解码:  {decoded_diff}")
    
    # RZ解码
    decoded_rz = decode_rz(rz_signal, sample_nums)
    print(f"RZ解码结果:       {decoded_rz}")
