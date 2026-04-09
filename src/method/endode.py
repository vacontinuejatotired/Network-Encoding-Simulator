import matplotlib
matplotlib.use('TkAgg')  # 换用TkAgg后端，PyCharm里显示更稳
import matplotlib.pyplot as plt
import numpy as np
# 中文字体设置，防乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False


def plot_all(data,sample_nums=10):
    # 搞4个子图，上下排，共享X轴
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    nrz(data, axes[0],sample_nums)
    manchester(data, axes[1],sample_nums)
    diff_manchester(data, axes[2],sample_nums)
    rz(data, axes[3],sample_nums)
    
    axes[-1].set_xlabel('Time (bit interval)')
    plt.tight_layout()
    plt.show()


# 不归零码：1蓝高，0红低
def nrz(data, ax, sample_nums=10):
    # 写标题
    ax.set_title('NRZ(不归零码)')
    
    # 生成采样点序列
    time_points = []
    voltage_levels = []
    
    for i, bit in enumerate(data):
        # 每个bit的起始时间和结束时间
        t_start = i
        t_end = i + 1
        # 每个bit内均匀采样（包括起点，不包括终点，避免重复）
        t_bit = np.linspace(t_start, t_end, sample_nums, endpoint=False)
        # 电平值：整个bit保持不变
        v_bit = [bit] * sample_nums
        
        time_points.extend(t_bit)
        voltage_levels.extend(v_bit)
    
    # 添加最后一个终点（为了波形完整）
    time_points.append(len(data))
    voltage_levels.append(data[-1])
    
    # 根据比特值设置颜色（分段着色需要特殊处理，这里先用统一颜色）
    ax.plot(time_points, voltage_levels, color='blue', linewidth=2)
    
    # 用散点标记实际采样点（可选，便于观察）
    ax.scatter(time_points[:-1], voltage_levels[:-1], c=voltage_levels[:-1], 
               cmap='coolwarm', s=10, alpha=0.5, zorder=5)
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage (V)')
    ax.grid(True, alpha=0.3)
    
    # 画虚线，标一下每个bit的分界
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 在底部标出是0还是1
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10, 
                color='blue' if bit == 1 else 'red')


# 曼彻斯特：0是低->高（上升沿），1是高->低（下降沿）
def manchester(data, ax, sample_nums=10):
    ax.set_title('Manchester - 0=上升沿(0→1) 1=下降沿(1→0)')
    
    time_points = []
    voltage_levels = []
    
    for i, bit in enumerate(data):
        t_start = i
        t_mid = i + 0.5   # 中间跳变点
        t_end = i + 1
        
        # 每个半段分配采样点
        half_samples = sample_nums // 2
        if sample_nums % 2 == 1:
            half_samples_first = half_samples + 1
            half_samples_second = half_samples
        else:
            half_samples_first = half_samples
            half_samples_second = half_samples
        
        # 生成时间轴
        t_first = np.linspace(t_start, t_mid, half_samples_first, endpoint=False)
        t_second = np.linspace(t_mid, t_end, half_samples_second, endpoint=False)
        
        if bit == 1:
            # 1：高 → 低（下降沿）
            start, end = 1, 0
        else:
            # 0：低 → 高（上升沿）
            start, end = 0, 1
        
        # 前半段电平
        v_first = [start] * half_samples_first
        # 后半段电平
        v_second = [end] * half_samples_second
        
        time_points.extend(t_first)
        voltage_levels.extend(v_first)
        time_points.extend(t_second)
        voltage_levels.extend(v_second)
    
    # 添加最后一个终点
    time_points.append(len(data))
    voltage_levels.append(voltage_levels[-1])
    
    # 绘制波形（用绿色表示曼彻斯特编码）
    ax.plot(time_points, voltage_levels, color='green', linewidth=2)
    
    # 可选：标记采样点
    ax.scatter(time_points[:-1], voltage_levels[:-1], c='lightgreen', s=10, alpha=0.5, zorder=5)
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage (V)')
    ax.grid(True, alpha=0.3)
    
    # 画虚线标出每个bit的分界
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 在底部标出是0还是1
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10,
                color='red' if bit == 0 else 'blue')

def diff_manchester(data, ax, sample_nums=10):
    ax.set_title('Differential Manchester - 蓝1红0, 假设前置电平=1')
    
    time_points = []
    voltage_levels = []
    
    prev_level = 1      # 假设上一条尾巴是高电平
    
    for i, bit in enumerate(data):
        t_start = i
        t_mid = i + 0.5   # 中间跳变点
        t_end = i + 1
        
        # 每个半段分配采样点
        half_samples = sample_nums // 2
        if sample_nums % 2 == 1:
            half_samples_first = half_samples + 1
            half_samples_second = half_samples
        else:
            half_samples_first = half_samples
            half_samples_second = half_samples
        
        # 生成时间轴
        t_first = np.linspace(t_start, t_mid, half_samples_first, endpoint=False)
        t_second = np.linspace(t_mid, t_end, half_samples_second, endpoint=False)
        
        if bit == 0:
            # 0: 开头要跳一下，所以起始电平跟上一尾巴相反
            cur_start = 1 - prev_level
        else:
            # 1: 开头不跳，起始电平不变
            cur_start = prev_level
        
        cur_end = 1 - cur_start   # 中间必跳，所以结尾跟开头相反
        
        # 前半段电平
        v_first = [cur_start] * half_samples_first
        # 后半段电平
        v_second = [cur_end] * half_samples_second
        
        time_points.extend(t_first)
        voltage_levels.extend(v_first)
        time_points.extend(t_second)
        voltage_levels.extend(v_second)
        
        prev_level = cur_end   # 更新上一个电平，用于下一个bit
    
    # 添加最后一个终点
    time_points.append(len(data))
    voltage_levels.append(voltage_levels[-1])
    
    # 绘制波形（用紫色表示差分曼彻斯特）
    ax.plot(time_points, voltage_levels, color='purple', linewidth=2)
    
    # 可选：标记采样点
    ax.scatter(time_points[:-1], voltage_levels[:-1], c='plum', s=10, alpha=0.5, zorder=5)
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage (V)')
    ax.grid(True, alpha=0.3)
    
    # 画虚线标出每个bit的分界
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 在底部标出是0还是1（颜色：蓝1红0）
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')

def rz(data, ax, sample_nums=10):
    ax.set_title('RZ (Return to Zero) - 蓝1正脉冲(+1), 红0负脉冲(-1), 四等分')
    
    time_points = []
    voltage_levels = []
    
    for i, bit in enumerate(data):
        t_start = i
        t_rise = i + 0.25    # 从0跳变到脉冲
        t_fall = i + 0.75    # 从脉冲跳变回0
        t_end = i + 1
        
        # 分配采样点：三段 [start, rise), [rise, fall), [fall, end]
        # 每段需要的采样点数按时间长度比例分配（0.25 : 0.5 : 0.25 = 1:2:1）
        total_samples = sample_nums
        # 前段：占 1/4，中段：占 1/2，后段：占 1/4
        first_samples = max(1, total_samples // 4)
        mid_samples = max(1, total_samples // 2)
        last_samples = total_samples - first_samples - mid_samples
        if last_samples < 1:
            last_samples = 1
            # 调整前段和中段
            first_samples = max(1, first_samples - 1)
            mid_samples = total_samples - first_samples - last_samples
        
        # 生成时间轴
        t_first = np.linspace(t_start, t_rise, first_samples, endpoint=False)
        t_mid = np.linspace(t_rise, t_fall, mid_samples, endpoint=False)
        t_last = np.linspace(t_fall, t_end, last_samples, endpoint=False)
        
        # 确定脉冲电平
        if bit == 1:
            pulse = 1   # 正脉冲
        else:
            pulse = -1  # 负脉冲
        
        # 三段电平：归零(0) → 脉冲(±1) → 归零(0)
        v_first = [0] * first_samples
        v_mid = [pulse] * mid_samples
        v_last = [0] * last_samples
        
        time_points.extend(t_first)
        voltage_levels.extend(v_first)
        time_points.extend(t_mid)
        voltage_levels.extend(v_mid)
        time_points.extend(t_last)
        voltage_levels.extend(v_last)
    
    # 添加最后一个终点
    time_points.append(len(data))
    voltage_levels.append(0)
    
    # 绘制波形（用蓝色/红色区域填充区分？这里用黑色统一线条）
    ax.plot(time_points, voltage_levels, color='black', linewidth=2)
    
    # 可选：根据正负脉冲给采样点不同颜色
    scatter_colors = []
    for v in voltage_levels[:-1]:
        if v == 1:
            scatter_colors.append('blue')
        elif v == -1:
            scatter_colors.append('red')
        else:
            scatter_colors.append('gray')
    ax.scatter(time_points[:-1], voltage_levels[:-1], c=scatter_colors, s=10, alpha=0.5, zorder=5)
    
    ax.set_ylim(-1.5, 1.5)
    ax.set_ylabel('Voltage (V)')
    ax.grid(True, alpha=0.3)
    
    # 画虚线标出每个bit的分界
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 在底部标出是0还是1
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -1.3, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')