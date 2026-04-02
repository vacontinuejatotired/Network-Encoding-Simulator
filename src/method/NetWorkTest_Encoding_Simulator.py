import matplotlib.pyplot as plt

def NRC(data):
    print("NRC Encoding:")
    print(data)
    for i in range(len(data)):
        plt.hlines(y=data[i], xmin=i, xmax=i+1, colors='blue', linewidth=2)
        
    plt.xlim(0, len(data)+1)
    plt.ylim(-2, 2)
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('NRC Encoding')
    plt.show()

def Manchester(data):
    print("Manchester Encoding:")
    print(data)
    for i in range(len(data)):
        if data[i] == 1:
            plt.hlines(y= 1,xmin=i,xmax=i+0.5,colors='blue',linewidth=2)
            plt.vlines(x=i+0.5, ymin=0, ymax=1, colors='blue', linewidth=2)
            plt.hlines(y= 0,xmin=i+0.5,xmax=i+1,colors='blue',linewidth=2)
        elif data[i] == 0:
            plt.hlines(y= 0,xmin=i,xmax=i+0.5,colors='red',linewidth=2)
            plt.vlines(x=i+0.5, ymin=0, ymax=1, colors='red', linewidth=2)
            plt.hlines(y= 1,xmin=i+0.5,xmax=i+1,colors='red',linewidth=2)
        plt
    plt.xlim(0, len(data)+1)
    plt.ylim(-2, 2)
    plt.xlabel('X')
    plt.ylabel('Y')
    
    plt.title('Manchester Encoding')
    plt.show()

def RZ(data):
    print("RZ Encoding:")
    print(data)
   