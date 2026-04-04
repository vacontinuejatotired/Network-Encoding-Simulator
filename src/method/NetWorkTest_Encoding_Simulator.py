import matplotlib
matplotlib.use('TkAgg')  # 换用TkAgg后端，PyCharm里显示更稳
import matplotlib.pyplot as plt
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
                      colors=color, linewidth=2)
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
                      colors=color, linewidth=2)
        
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
                      colors=color, linewidth=2)
        
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


# 归零码：1画个高脉冲然后归零，0一直趴在地上
def rz(data, ax):
    ax.set_title('RZ - 蓝1红0')
    prev_end = None
    
    for i in range(len(data)):
        if data[i] == 1:
            color = 'blue'
            start, mid, end = 1, 0, 0   # 高->归零
        else:
            color = 'red'
            start, mid, end = 0, 0, 0   # 全程低
        
        if i > 0 and prev_end != start:
            ax.vlines(x=i, ymin=min(prev_end, start), ymax=max(prev_end, start),
                      colors=color, linewidth=2)
        
        if data[i] == 1:
            # 先高
            ax.hlines(y=start, xmin=i, xmax=i+0.5, colors=color, linewidth=2)
            # 跳下来
            ax.vlines(x=i+0.5, ymin=mid, ymax=start, colors=color, linewidth=2)
            # 归零后半段
            ax.hlines(y=mid, xmin=i+0.5, xmax=i+1, colors=color, linewidth=2)
            prev_end = mid
        else:
            # 0就一直低
            ax.hlines(y=start, xmin=i, xmax=i+1, colors=color, linewidth=2)
            prev_end = start
    
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage')
    ax.grid(True, alpha=0.3)
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')
