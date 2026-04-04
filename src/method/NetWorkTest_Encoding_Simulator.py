import matplotlib
matplotlib.use('TkAgg')  # 换用TkAgg后端，PyCharm里显示更稳
import matplotlib.pyplot as plt

# 中文字体设置，防乱码
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC']
plt.rcParams['axes.unicode_minus'] = False


def plot_all(data):
    # 搞4个子图，上下排，共享X轴
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    nrc(data, axes[0])
    manchester(data, axes[1])
    diff_manchester(data, axes[2])
    rz(data, axes[3])
    
    axes[-1].set_xlabel('Time (bit interval)')
    plt.tight_layout()
    plt.show()


# 不归零码：1蓝高，0红低
def nrc(data, ax):
    ax.set_title('NRZ - 蓝1红0')
    prev = None
    for i in range(len(data)):
        color = 'blue' if data[i] == 1 else 'red'
        level = data[i]
        ax.hlines(y=level, xmin=i, xmax=i+1, colors=color, linewidth=2)
        
        # 跟前一个电平不一样就画条竖线接上，不然看着是断的
        if i > 0 and prev != level:
            ax.vlines(x=i, ymin=min(prev, level), ymax=max(prev, level), 
                      colors='black', linewidth=2)
        prev = level
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage')
    ax.grid(True, alpha=0.3)
    # 画虚线，标一下每个bit的分界
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    # 在底部标出是0还是1，颜色跟着走
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10, 
                color='blue' if bit == 1 else 'red')


# 曼彻斯特：1是低->高（上升沿），0是高->低（下降沿）
def manchester(data, ax):
    ax.set_title('Manchester - 蓝1红0')
    prev_end = None
    for i in range(len(data)):
        if data[i] == 1:
            start, end = 0, 1
            color = 'blue'
        else:
            start, end = 1, 0
            color = 'red'
        
        # 跟前一个bit的尾巴对不上就加竖线
        if i > 0 and prev_end != start:
            ax.vlines(x=i, ymin=min(prev_end, start), ymax=max(prev_end, start), 
                      colors='black', linewidth=2)
        
        # 前半段
        ax.hlines(y=start, xmin=i, xmax=i+0.5, colors=color, linewidth=2)
        # 中间的跳变竖线
        ax.vlines(x=i+0.5, ymin=min(start, end), ymax=max(start, end), 
                  colors=color, linewidth=2)
        # 后半段
        ax.hlines(y=end, xmin=i+0.5, xmax=i+1, colors=color, linewidth=2)
        
        prev_end = end
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage')
    ax.grid(True, alpha=0.3)
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')


# 差分曼彻斯特：每个bit中间必跳，开始处跳变=0，不跳=1
def diff_manchester(data, ax):
    ax.set_title('Differential Manchester - 蓝1红0')
    prev_level = 1      # 假设上一条尾巴是高电平
    prev_end = prev_level
    
    for i in range(len(data)):
        if data[i] == 0:
            # 0: 开头要跳一下，所以起始电平跟上一尾巴相反
            cur_start = 1 - prev_level
            color = 'red'
        else:
            # 1: 开头不跳，起始电平不变
            cur_start = prev_level
            color = 'blue'
        
        cur_end = 1 - cur_start   # 中间必跳，所以结尾跟开头相反
        
        # 跟上一个bit的尾巴接上
        if i > 0 and prev_end != cur_start:
            ax.vlines(x=i, ymin=min(prev_end, cur_start), ymax=max(prev_end, cur_start),
                      colors='black', linewidth=2)
        
        ax.hlines(y=cur_start, xmin=i, xmax=i+0.5, colors=color, linewidth=2)
        ax.vlines(x=i+0.5, ymin=min(cur_start, cur_end), ymax=max(cur_start, cur_end),
                  colors=color, linewidth=2)
        ax.hlines(y=cur_end, xmin=i+0.5, xmax=i+1, colors=color, linewidth=2)
        
        prev_level = cur_end
        prev_end = cur_end
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage')
    ax.grid(True, alpha=0.3)
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')
def rz(data, ax):
    ax.set_title('RZ - 蓝1红0（正脉冲1，负脉冲0，四等分）')
    
    for i, bit in enumerate(data):
        x0 = i          # 0.0
        x1 = i + 0.25   # 第一个分隔
        x2 = i + 0.75   # 第二个分隔  
        x3 = i + 1      # 1.0
        
        if bit == 1:
            color = 'blue'
            pulse = 1    # 正脉冲
        else:
            color = 'red'
            pulse = -1   # 负脉冲
        
        # 0.00-0.25: 归零（0电平）
        ax.hlines(y=0, xmin=x0, xmax=x1, colors=color, linewidth=2)
        # 0.25处: 跳变到脉冲电平
        ax.vlines(x=x1, ymin=0, ymax=pulse, colors=color, linewidth=2)
        # 0.25-0.75: 脉冲电平
        ax.hlines(y=pulse, xmin=x1, xmax=x2, colors=color, linewidth=2)
        # 0.75处: 跳变归零
        ax.vlines(x=x2, ymin=0, ymax=pulse, colors=color, linewidth=2)
        # 0.75-1.00: 归零
        ax.hlines(y=0, xmin=x2, xmax=x3, colors=color, linewidth=2)
    
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlim(0, len(data))
    ax.set_ylabel('Voltage')
    ax.set_xlabel('Time (bit interval)')
    ax.grid(True, alpha=0.3)
    
    # 比特分隔线
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 比特值标注
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -1.3, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')