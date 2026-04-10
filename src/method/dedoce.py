
import matplotlib  # 导入matplotlib库
matplotlib.use('TkAgg')  # 设置后端为TkAgg，用于弹出窗口显示图表
import matplotlib.pyplot as plt  # 导入绘图模块，plt是常用别名
import numpy as np  # 导入数值计算库，np是常用别名


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
    bits = []  # 准备一个空列表，存解码出来的比特
    
    # 计算总共有多少个比特，总采样点数除以每个比特的采样点数
    # 比如64个采样点，每个比特采16个，那就是4个比特
    total_bits = len(signal) // sample_nums
    
    # 遍历每个比特，i从0到total_bits-1
    for i in range(total_bits):
        # 计算当前比特中间位置的索引
        # i * sample_nums 是当前比特的起始位置
        # 加上 sample_nums // 2 就是中间位置（整除2）
        mid = i * sample_nums + sample_nums // 2
        
        # 取出中间位置的电平值
        level = signal[mid]
        
        # 判断电平高低，阈值设为0.5
        if level >= 0.5:
            bits.append(1)  # 高电平判为1
        else:
            bits.append(0)  # 低电平判为0
    
    # 返回解码后的比特列表
    return bits

#曼切彻斯特编码解密函数
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
    bits = []  # 准备空列表存结果
    
    # 计算总比特数
    total_bits = len(signal) // sample_nums
    
    # 计算半比特的采样点数，比如16个点就是8个
    half = sample_nums // 2
    
    # 遍历每个比特
    for i in range(total_bits):
        # 当前比特的起始索引
        start_idx = i * sample_nums
        
        # 取前半段中间位置的索引，start_idx加四分之一位置
        # 避开边缘，取中间更稳定
        first_mid = start_idx + half // 2
        
        # 取后半段中间位置的索引，start_idx加半比特再加四分之一
        second_mid = start_idx + half + half // 2
        
        # 取出前半段的电平值
        first = signal[first_mid]
        
        # 取出后半段的电平值
        second = signal[second_mid]
        
        # 判断跳变方向：低->高是上升沿，高->低是下降沿
        if first < 0.5 and second >= 0.5:
            bits.append(0)   # 上升沿（低变高）表示0
        elif first >= 0.5 and second < 0.5:
            bits.append(1)   # 下降沿（高变低）表示1
        else:
            # 异常情况：没有明显跳变，可能是噪声太大
            #  fallback策略：看前半段电平，低就判0，高就判1
            bits.append(0 if first < 0.5 else 1)
    
    # 返回解码结果
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
    bits = []  # 准备空列表存结果
    
    # 计算总比特数
    total_bits = len(signal) // sample_nums
    
    # 计算半比特采样点数
    half = sample_nums // 2
    
    # 设置初始参考电平，默认是1（高电平）
    # 这个值很关键，要和编码时的初始假设一致
    prev_end = float(initial_level)
    
    # 遍历每个比特
    for i in range(total_bits):
        # 当前比特的起始索引
        start_idx = i * sample_nums
        
        # 取比特开始处的电平，跳过前2个点避开跳变边缘
        # 如果采样点数太少（<=4），就直接取第一个点
        start_level = signal[start_idx + 2] if sample_nums > 4 else signal[start_idx]
        
        # 判断开始处是否有跳变：当前电平和上一个结束电平差值超过0.5
        if abs(start_level - prev_end) > 0.5:
            bits.append(0)   # 有跳变表示0
        else:
            bits.append(1)   # 无跳变表示1
        
        # 更新prev_end为当前比特的结束电平，供下一个比特参考
        # 取结束位置前2个点，同样避开边缘
        end_idx = start_idx + sample_nums - 2
        
        # 如果索引没超界就取，超界了就取最后一个点
        prev_end = signal[end_idx] if end_idx < len(signal) else signal[-1]
    
    # 返回解码结果
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
    bits = []  # 准备空列表存结果
    
    # 计算总比特数
    total_bits = len(signal) // sample_nums
    
    # 计算半比特采样点数
    half = sample_nums // 2
    
    # 遍历每个比特
    for i in range(total_bits):
        # 当前比特的起始索引
        start_idx = i * sample_nums
        
        # 取前半段中间位置，脉冲最高点/最低点应该在这里
        mid = start_idx + half // 2
        
        # 取出该位置的电平
        level = signal[mid]
        
        # 判断脉冲极性
        if level > 0.5:
            bits.append(1)      # 正脉冲表示1
        elif level < -0.5:
            bits.append(0)      # 负脉冲表示0
        else:
            # 电平接近0，可能是噪声或采样位置不对
            # fallback：看前半段的最大值，有正脉冲就判1，否则判0
            segment = signal[start_idx:start_idx + half]  # 切片取前半段
            if max(segment) > 0.5:
                bits.append(1)
            else:
                bits.append(0)
    
    # 返回解码结果
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
    # 生成高斯噪声，均值0，标准差noise_level，长度和信号一样
    noise = np.random.normal(0, noise_level, len(signal))
    
    # 把噪声加到原信号上，用zip配对相加
    noisy_signal = [s + n for s, n in zip(signal, noise)]
    
    # 返回加噪后的信号
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
    # 调用编码函数，把比特转成电平信号
    signal = encode_func(data, sample_nums)
    
    # 如果开了加噪开关，就加噪声
    if add_noise_flag:
        signal = add_noise(signal, noise_level)
    
    # 调用解码函数，把电平信号转回比特
    decoded = decode_func(signal, sample_nums)
    
    # 比较原始数据和解码数据是否一致
    success = data == decoded
    
    # 返回三元组：是否成功、原始数据、解码数据
    return success, data, decoded


# ==================== 将编码函数转换为返回采样列表的版本 ====================

def encode_nrz_to_signal(data, sample_nums=10):
    """NRZ编码，返回采样电平列表"""
    signal = []  # 准备空列表存电平序列
    
    # 遍历每个比特
    for bit in data:
        # 把bit重复sample_nums次， extend是展开追加
        signal.extend([bit] * sample_nums)
    
    # 返回电平列表
    return signal


def encode_manchester_to_signal(data, sample_nums=10):
    """曼彻斯特编码，返回采样电平列表（0=上升沿，1=下降沿）"""
    signal = []  # 准备空列表
    
    # 计算半比特采样点数
    half = sample_nums // 2
    
    # 处理奇偶：如果总采样点是奇数，前半段多一个点
    if sample_nums % 2 == 1:
        first_half = half + 1
        second_half = half
    else:
        first_half = half
        second_half = half
    
    # 遍历每个比特
    for bit in data:
        if bit == 1:
            # 1是下降沿：前半高(1)，后半低(0)
            signal.extend([1] * first_half)
            signal.extend([0] * second_half)
        else:
            # 0是上升沿：前半低(0)，后半高(1)
            signal.extend([0] * first_half)
            signal.extend([1] * second_half)
    
    # 返回电平列表
    return signal


def encode_diff_manchester_to_signal(data, sample_nums=10, initial_level=1):
    """差分曼彻斯特编码，返回采样电平列表"""
    signal = []  # 准备空列表
    
    # 计算半比特采样点数
    half = sample_nums // 2
    
    # 处理奇偶
    if sample_nums % 2 == 1:
        first_half = half + 1
        second_half = half
    else:
        first_half = half
        second_half = half
    
    # 当前电平，从初始电平开始
    current_level = initial_level
    
    # 遍历每个比特
    for bit in data:
        if bit == 0:
            # 0要求边界有跳变，电平翻转
            current_level = 1 - current_level
        
        # 前半段保持当前电平
        signal.extend([current_level] * first_half)
        
        # 中间必有跳变，电平翻转
        current_level = 1 - current_level
        
        # 后半段用翻转后的电平
        signal.extend([current_level] * second_half)
    
    # 返回电平列表
    return signal


def encode_rz_to_signal(data, sample_nums=10):
    """RZ编码，返回采样电平列表（正脉冲=1，负脉冲=0）"""
    signal = []  # 准备空列表
    
    # 三段分配：前段0.25，中段0.5，后段0.25
    first_samples = max(1, sample_nums // 4)  # 至少1个点
    mid_samples = max(1, sample_nums // 2)    # 至少1个点
    last_samples = sample_nums - first_samples - mid_samples  # 剩下的给后段
    
    # 如果后段不够1个，调整前段
    if last_samples < 1:
        last_samples = 1
        first_samples = max(1, first_samples - 1)
        mid_samples = sample_nums - first_samples - last_samples
    
    # 遍历每个比特
    for bit in data:
        # 确定脉冲极性，1是正脉冲+1，0是负脉冲-1
        pulse = 1 if bit == 1 else -1
        
        # 前段归零（0电平）
        signal.extend([0] * first_samples)
        
        # 中段脉冲（正或负）
        signal.extend([pulse] * mid_samples)
        
        # 后段归零（0电平）
        signal.extend([0] * last_samples)
    
    # 返回电平列表
    return signal


# ==================== 测试代码 ====================
if __name__ == "__main__":
    # 测试数据：原始比特 [1, 0, 1, 0]
    sample_nums = 16
    
    # 从上面的测试结果中提取的编码结果（写死），每个比特16个采样点
    # NRZ：1就是16个1，0就是16个0
    nrz_signal = [1, 1, 1, 1, 1, 1, 0.7, 0.8, 0.6, 1, 1, 1, 1, 1, 1, 1,  # 第1个bit=1
                  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  # 第2个bit=0
                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,  # 第3个bit=1
                  0, 0, 0, 0, 0, 0, 0, 0, 0.2, 0, 0.4, 0.3, 0, 0, 0, 0]  # 第4个bit=0
    
    # 曼彻斯特：1是前8个1后8个0（下降沿），0是前8个0后8个1（上升沿）
    manchester_signal = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,  # 1=高->低
                         0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,  # 0=低->高
                         1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,  # 1=高->低
                         0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]  # 0=低->高
    
    # 差分曼彻斯特：假设初始电平=1，1无跳变0有跳变，中心必有跳变
    # bit1=1: 无跳变(1)->中心跳(0)  bit2=0: 有跳变(1)->中心跳(0)
    # bit3=1: 无跳变(0)->中心跳(1)  bit4=0: 有跳变(0)->中心跳(1)
    diff_manchester_signal = [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,  # bit1=1
                               1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0,  # bit2=0（边界跳了）
                               0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1,  # bit3=1（边界无跳）
                               0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1]  # bit4=0（边界跳了）
    
    # RZ：四等分，前后各4个0，中间8个脉冲（1是+1，0是-1）
    rz_signal = [0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,   # bit1=1，正脉冲
                 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0,  # bit2=0，负脉冲
                 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0,   # bit3=1，正脉冲
                 0, 0, 0, 0, -1, -1, -1, -1, -1, -1, -1, -1, 0, 0, 0, 0]  # bit4=0，负脉冲
    
    # 打印测试信息
    print(f"原始比特: [1, 0, 1, 0]")
    print(f"每比特采样点: {sample_nums}")
    print()  # 空行
    
    # NRZ解码测试
    decoded_nrz = decode_nrz(nrz_signal, sample_nums)
    print(f"NRZ解码结果:      {decoded_nrz}")
    
    # 曼彻斯特解码测试
    decoded_manchester = decode_manchester(manchester_signal, sample_nums)
    print(f"曼彻斯特解码结果:  {decoded_manchester}")
    
    # 差分曼彻斯特解码测试
    decoded_diff = decode_diff_manchester(diff_manchester_signal, sample_nums)
    print(f"差分曼彻斯特解码:  {decoded_diff}")
    
    # RZ解码测试
    decoded_rz = decode_rz(rz_signal, sample_nums)
    print(f"RZ解码结果:       {decoded_rz}")