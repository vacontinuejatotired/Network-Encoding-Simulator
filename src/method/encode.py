import matplotlib
matplotlib.use('TkAgg')  # 切换matplotlib后端为TkAgg，PyCharm里弹窗显示更稳定不闪退
import matplotlib.pyplot as plt  # 导入绘图库，plt是约定俗成的别名
import numpy as np  # 导入数值计算库，np是约定俗成的别名

# 中文字体设置，防止图表标题和标签显示成乱码方框
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'PingFang SC', 'Noto Sans CJK SC']  # 按优先级尝试中文字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示成方块的问题，用普通减号代替


def plot_all(data, sample_nums=10):  # 主函数，一次性画出四种编码对比图，sample_nums是每个bit采多少个点
    # 创建画布，4行1列的子图布局，figsize设置画布大小12英寸宽10英寸高，sharex=True让四个子图共用X轴刻度
    fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
    
    # 挨个调用四个编码函数，每个函数负责画一个子图，把采样点数传进去
    nrz(data, axes[0], sample_nums)           # 第1个子图画不归零码
    manchester(data, axes[1], sample_nums)    # 第2个子图画曼彻斯特码
    diff_manchester(data, axes[2], sample_nums)  # 第3个子图画差分曼彻斯特码
    rz(data, axes[3], sample_nums)            # 第4个子图画归零码
    
    # 只在最底下那个子图设置X轴标签，因为四个图共用X轴
    axes[-1].set_xlabel('Time (bit interval)')
    
    plt.tight_layout()  # 自动调整子图间距，防止标题和标签互相重叠
    plt.show()  # 弹出窗口显示图表，程序会在这里卡住直到你关闭窗口


# 不归零码：1用蓝色高电平表示，0用红色低电平表示，整个bit周期电平保持不变
def nrz(data, ax, sample_nums=10):  # data是比特列表如[1,0,0,0,1,0,0,1,1,1]，ax是matplotlib子图对象
    # 设置这个子图的标题
    ax.set_title('NRZ(不归零码)')
    
    # 准备两个空列表，用来存所有采样点的时间和电压值
    time_points = []      # 横坐标：时间点
    voltage_levels = []   # 纵坐标：对应的电平值
    
    # 遍历每个比特，i是索引从0开始，bit是值1或0
    for i, bit in enumerate(data):
        # 当前bit的起始时间，比如第0个bit从0开始，第1个bit从1开始
        t_start = i
        # 当前bit的结束时间，比如第0个bit到1结束
        t_end = i + 1
        
        # 在当前bit时间段内均匀撒sample_nums个点，endpoint=False表示不采终点（下一位会采）
        # 比如sample_nums=10，就在0到1之间生成10个等间距的点[0, 0.1, 0.2, ..., 0.9]
        t_bit = np.linspace(t_start, t_end, sample_nums, endpoint=False)
        
        # NRZ特性：整个bit周期电平不变，1就是高1，0就是低0
        # 生成sample_nums个相同的电平值，比如bit=1就生成[1,1,1,1,1,1,1,1,1,1]
        v_bit = [bit] * sample_nums
        
        # 把当前bit的10个时间点和10个电平值，分别追加到总列表里
        time_points.extend(t_bit)      # extend是把列表元素一个个加进去
        voltage_levels.extend(v_bit)   # 同上，追加电平值
    
    # 循环结束后，补上最后一个bit的终点，让波形画到最右边不中断
    # 比如10个bit，最后一个终点是时间10，电平等于最后一个bit的值
    time_points.append(len(data))
    voltage_levels.append(data[-1])
    
    # 用蓝色折线连接所有采样点，linewidth=2是线宽2像素
    # 注意：这里其实应该区分颜色，1用蓝0用红，但代码里偷懒用了统一蓝色
    ax.plot(time_points, voltage_levels, color='blue', linewidth=2)
    
    # 在采样点位置画小圆点，c=voltage_levels用coolwarm颜色映射，1偏红0偏蓝，s=10是点大小
    # zorder=5让散点在最上层，不会被线盖住，[:-1]是去掉最后一个点因为时间列表多一个终点
    ax.scatter(time_points[:-1], voltage_levels[:-1], c=voltage_levels[:-1], 
               cmap='coolwarm', s=10, alpha=0.5, zorder=5)
    
    # 设置Y轴显示范围从-0.5到1.5，给文字标注留空间
    ax.set_ylim(-0.5, 1.5)
    # 设置Y轴标签为Voltage (V)
    ax.set_ylabel('Voltage (V)')
    # 打开网格线，alpha=0.3让网格半透明不刺眼
    ax.grid(True, alpha=0.3)
    
    # 画灰色虚线标出每个bit的分界线，比如x=0,1,2,3...，一共len(data)+1条线
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 在每个bit底部中央写数字，1用蓝色字，0用红色字，ha='center'水平居中
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10, 
                color='blue' if bit == 1 else 'red')


# 曼彻斯特编码：0是前半低后半高（上升沿），1是前半高后半低（下降沿），每位中心必有跳变
def manchester(data, ax, sample_nums=10):  # 参数同上
    # 设置标题，注明编码规则和颜色约定
    ax.set_title('Manchester - 0=上升沿(0→1) 1=下降沿(1→0)')
    
    # 同样准备空列表存采样点
    time_points = []
    voltage_levels = []
    
    # 遍历每个比特
    for i, bit in enumerate(data):
        t_start = i       # bit开始时间
        t_mid = i + 0.5   # 中间跳变点，曼彻斯特每位中间必须跳变
        t_end = i + 1     # bit结束时间
        
        # 把采样点分成两半，前半段和后半段各占一半
        half_samples = sample_nums // 2  # 整除2，比如10变成5
        
        # 如果采样点数是奇数，比如11，前半段多一个点，后半段少一个，保证总共还是sample_nums个
        if sample_nums % 2 == 1:  # %是取余，余1说明是奇数
            half_samples_first = half_samples + 1  # 前半段6个
            half_samples_second = half_samples      # 后半段5个
        else:  # 偶数就平分
            half_samples_first = half_samples
            half_samples_second = half_samples
        
        # 前半段时间轴，从t_start到t_mid，采half_samples_first个点，不含终点
        t_first = np.linspace(t_start, t_mid, half_samples_first, endpoint=False)
        # 后半段时间轴，从t_mid到t_end，采half_samples_second个点，不含终点
        t_second = np.linspace(t_mid, t_end, half_samples_second, endpoint=False)
        
        # 根据bit值决定前半后半的电平
        if bit == 1:
            # 1是下降沿：前半高(1)，后半低(0)，中间从高跳到低
            start, end = 1, 0
        else:
            # 0是上升沿：前半低(0)，后半高(1)，中间从低跳到高
            start, end = 0, 1
        
        # 前半段所有点都是start电平
        v_first = [start] * half_samples_first
        # 后半段所有点都是end电平
        v_second = [end] * half_samples_second
        
        # 把前后两半的时间和电平，追加到总列表
        time_points.extend(t_first)
        voltage_levels.extend(v_first)
        time_points.extend(t_second)
        voltage_levels.extend(v_second)
    
    # 补上最后一个终点，时间是最右边，电平是最后采到的那个值
    time_points.append(len(data))
    voltage_levels.append(voltage_levels[-1])
    
    # 用绿色画曼彻斯特波形
    ax.plot(time_points, voltage_levels, color='green', linewidth=2)
    
    # 用浅绿色画采样点
    ax.scatter(time_points[:-1], voltage_levels[:-1], c='lightgreen', s=10, alpha=0.5, zorder=5)
    
    # Y轴范围、标签、网格，同上
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage (V)')
    ax.grid(True, alpha=0.3)
    
    # 画bit分界线，同上
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 底部标注bit值，0用红色，1用蓝色（和NRZ反过来的逻辑，其实没必要）
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10,
                color='red' if bit == 0 else 'blue')


# 差分曼彻斯特编码：每位中心必有跳变，bit边界有跳变代表0，无跳变代表1，差分编码看相对变化
def diff_manchester(data, ax, sample_nums=10):
    # 标题注明编码规则和假设的初始电平
    ax.set_title('Differential Manchester - 假设前置电平=1')
    
    # 准备列表
    time_points = []
    voltage_levels = []
    
    # 关键：差分编码需要知道前一个bit结束时的电平，作为当前bit的参考
    # 假设上一条尾巴是高电平1，这是初始条件，会影响第一个bit的画法
    prev_level = 1
    
    # 遍历每个bit
    for i, bit in enumerate(data):
        t_start = i       # bit开始
        t_mid = i + 0.5   # 中间跳变点，差分曼彻斯特也是中心必有跳变
        t_end = i + 1     # bit结束
        
        # 同样分成两半采样
        half_samples = sample_nums // 2
        
        # 奇偶处理，同上
        if sample_nums % 2 == 1:
            half_samples_first = half_samples + 1
            half_samples_second = half_samples
        else:
            half_samples_first = half_samples
            half_samples_second = half_samples
        
        # 生成两半段时间轴，同上
        t_first = np.linspace(t_start, t_mid, half_samples_first, endpoint=False)
        t_second = np.linspace(t_mid, t_end, half_samples_second, endpoint=False)
        
        # 差分编码的核心逻辑：看bit边界有没有跳变
        if bit == 0:
            # 0：bit边界必须有跳变，所以当前起始电平跟上一个结束电平相反
            # 1-prev_level就是翻转，比如prev=1则cur_start=0，prev=0则cur_start=1
            cur_start = 1 - prev_level
        else:
            # 1：bit边界无跳变，起始电平保持不变，跟上一位结束一样
            cur_start = prev_level
        
        # 差分曼彻斯特也是中心必有跳变，所以结尾电平跟起始相反
        cur_end = 1 - cur_start
        
        # 前半段电平
        v_first = [cur_start] * half_samples_first
        # 后半段电平
        v_second = [cur_end] * half_samples_second
        
        # 追加到总列表
        time_points.extend(t_first)
        voltage_levels.extend(v_first)
        time_points.extend(t_second)
        voltage_levels.extend(v_second)
        
        # 更新prev_level为当前bit的结束电平，供下一个bit使用
        prev_level = cur_end
    
    # 补终点
    time_points.append(len(data))
    voltage_levels.append(voltage_levels[-1])
    
    # 用紫色画差分曼彻斯特波形
    ax.plot(time_points, voltage_levels, color='purple', linewidth=2)
    
    # 用plum色（淡紫）画采样点
    ax.scatter(time_points[:-1], voltage_levels[:-1], c='plum', s=10, alpha=0.5, zorder=5)
    
    # Y轴设置
    ax.set_ylim(-0.5, 1.5)
    ax.set_ylabel('Voltage (V)')
    ax.grid(True, alpha=0.3)
    
    # bit分界线
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 底部标注，1蓝色0红色
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -0.4, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')


# 归零码：1是正脉冲（高电平），0是负脉冲（低电平），每个bit中间都回到零，四等分结构
def rz(data, ax, sample_nums=10):
    # 标题说明编码规则：四等分，正负脉冲，归零
    ax.set_title('RZ (Return to Zero) - 1正脉冲(+1), 0负脉冲(-1), 四等分')
    
    # 准备列表
    time_points = []
    voltage_levels = []
    
    # 遍历每个bit
    for i, bit in enumerate(data):
        t_start = i        # 0.0，bit开始
        t_rise = i + 0.25  # 0.25，从0跳变到脉冲电平的时刻
        t_fall = i + 0.75  # 0.75，从脉冲跳变回0的时刻
        t_end = i + 1      # 1.0，bit结束
        
        # RZ特性：脉冲只占中间50%，前后各25%是归零保护带
        # 三段的时间比例是 0.25 : 0.5 : 0.25 = 1:2:1
        total_samples = sample_nums  # 总共要采多少点
        
        # 前段（归零）占1/4，至少保证1个点防止除零
        first_samples = max(1, total_samples // 4)
        # 中段（脉冲）占1/2
        mid_samples = max(1, total_samples // 2)
        # 后段（归零）占剩下的，理论上是1/4
        last_samples = total_samples - first_samples - mid_samples
        
        # 如果算出来最后一段不够1个点，强行调成1，然后往前挤
        if last_samples < 1:
            last_samples = 1
            first_samples = max(1, first_samples - 1)  # 前段减1
            mid_samples = total_samples - first_samples - last_samples  # 中段重新算
        
        # 生成三段时间轴，都是左闭右开
        t_first = np.linspace(t_start, t_rise, first_samples, endpoint=False)   # 0到0.25
        t_mid = np.linspace(t_rise, t_fall, mid_samples, endpoint=False)        # 0.25到0.75
        t_last = np.linspace(t_fall, t_end, last_samples, endpoint=False)     # 0.75到1.0
        
        # 确定脉冲电平，1是正脉冲+1，0是负脉冲-1
        if bit == 1:
            pulse = 1   # 正脉冲，蓝色
        else:
            pulse = -1  # 负脉冲，红色
        
        # 三段电平：前归零(0) -> 中脉冲(±1) -> 后归零(0)
        v_first = [0] * first_samples      # 前25%是0
        v_mid = [pulse] * mid_samples      # 中间50%是脉冲
        v_last = [0] * last_samples        # 后25%是0
        
        # 三段都追加到总列表
        time_points.extend(t_first)
        voltage_levels.extend(v_first)
        time_points.extend(t_mid)
        voltage_levels.extend(v_mid)
        time_points.extend(t_last)
        voltage_levels.extend(v_last)
    
    # 补终点，RZ结束一定在0电平
    time_points.append(len(data))
    voltage_levels.append(0)
    
    # 用黑色统一画波形线条
    ax.plot(time_points, voltage_levels, color='black', linewidth=2)
    
    # 采样点按实际电平着色：1用蓝，-1用红，0用灰
    scatter_colors = []  # 准备颜色列表
    for v in voltage_levels[:-1]:  # 遍历每个电平值，去掉最后补的终点
        if v == 1:
            scatter_colors.append('blue')    # 正脉冲蓝色
        elif v == -1:
            scatter_colors.append('red')     # 负脉冲红色
        else:
            scatter_colors.append('gray')    # 零电平灰色
    
    # 画彩色采样点
    ax.scatter(time_points[:-1], voltage_levels[:-1], c=scatter_colors, s=10, alpha=0.5, zorder=5)
    
    # Y轴范围扩大到-1.5到1.5，因为要显示负脉冲
    ax.set_ylim(-1.5, 1.5)
    ax.set_ylabel('Voltage (V)')
    ax.grid(True, alpha=0.3)
    
    # bit分界线
    for i in range(len(data) + 1):
        ax.axvline(x=i, color='gray', linestyle='--', alpha=0.4, linewidth=0.5)
    
    # 底部标注，位置往下调到-1.3因为Y轴范围扩大了，1蓝色0红色
    for i, bit in enumerate(data):
        ax.text(i + 0.5, -1.3, str(bit), ha='center', fontsize=10,
                color='blue' if bit == 1 else 'red')