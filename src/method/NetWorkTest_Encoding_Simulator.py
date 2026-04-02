import matplotlib.pyplot as plt

def NRC(data):
    for i in range(len(data)):
        plt.hlines(y=data[i], xmin=i, xmax=i+1, colors='blue', linewidth=2)
        
    plt.xlim(0, len(data)+1)
    plt.ylim(-2, 2)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.show()