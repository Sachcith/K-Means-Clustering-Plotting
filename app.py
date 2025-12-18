from flask import Flask,render_template
from flask_socketio import SocketIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import random as r
import numpy as np
import time
import os

app = Flask(__name__)
socketio = SocketIO(app)

def K_Means(x,y,k):
    r.seed(24251)
    z = []
    for i in range(k):
        z.append([r.randint(-5,5),r.randint(-2,2)])
    maxIter = 30
    final = [-1 for i in range(len(x))]
    for maxI in range(maxIter):
        for i in range(len(x)):
            min_index = -1
            min_value = float("inf")
            for j in range(k):
                dist = ((z[j][0]-x[i])**2+(z[j][1]-y[i])**2)**2
                if dist<min_value:
                    min_value = dist
                    min_index = j
            final[i] = min_index
            z[min_index][0] = (z[min_index][0]+x[i])/2
            z[min_index][1] = (z[min_index][1]+y[i])/2
    return z,final
            
def gen(k,no,cr,cx,cy):
    datax = []
    datay = []
    theta = [i*2*np.pi/k for i in range(k)]
    temp = 2*np.pi*r.random()
    theta = [(i+temp)%(2*np.pi) for i in theta]
    for i in range(k):
        for j in range(no):
            datax.append(round(cr*np.cos(theta[i])+cx+0.1*r.gauss(mu=0,sigma=1),2))
            datay.append(round(cr*np.sin(theta[i])+cy+0.1*r.gauss(mu=0,sigma=1),2))
    return datax,datay


current = None
mat = [[],[],[]]
input1 = ""
input2 = ""
input3 = ""
x = 0
y = 0
color = [[],[],[]]

@app.route('/')
def home():
    global mat, input1, input2, input3
    i1 = ",".join([str(i) for i in input1])
    i2 = ",".join([str(i) for i in input2])
    i3 = ",".join([str(i) for i in input3])
    socketio.emit("linear_output",{"n":len(mat[0]),"table":mat,"color":color})
    return render_template("index.html",INPUT1=i1,INPUT2=i2,INPUT3=i3)

@socketio.on("output")
def output():
    global mat, input1, input2, input3
    #i1 = "".join([str(i) for i in input1])
    #i2 = "".join([str(i) for i in input2])
    socketio.emit("linear_output",{"n":len(mat[0]),"table":mat,"color":color})

@socketio.on("random")
def ran(data):
    global mat, input1, input2, input3
    temp = r.randint(20,40)
    '''
    input1 = [round(r.randint(0,9)+r.random(),2) for i in range(temp)]
    input2 = [round(r.randint(0,9)+r.random(),2) for i in range(temp)]
    '''
    k = r.randint(3,5)
    input1,input2 = gen(k,temp,5,0,0)
    input3 = [k]


    print("Inside random")
    i1 = ",".join([str(i) for i in input1])
    i2 = ",".join([str(i) for i in input2])
    i3 = ",".join([str(i) for i in input3])
    data = {
            "type" : "random",
            "input1" : i1,
            "input2" : i2,
            "input3" : i3
        }
    socketio.emit("value",{"input1":i1,"input2":i2,"input3":i3})

@socketio.on("reset")
def reset(data):
    global current, mat, input1, input2, input3
    current = None
    mat = [[],[],[]]
    color = [[],[],[]]
    input1 = ""
    input2 = ""
    input3 = ""
    socketio.emit("reset",{})
    print("x-"*30)
    print("Reset Completed")
    print("-x"*30)

@socketio.on("plot")
def p(data):
    global mat, x, y, input1, input2
    current = "circular"
    input1 = str(data["input1"]).split(",")
    input2 = str(data["input2"]).split(",")
    input3 = str(data["input3"]).split(",")
    input1 = [float(i) for i in input1]
    input2 = [float(i) for i in input2]
    input3 = [int(i) for i in input3]
    #print(input1,input2,input3)

    base = os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(base, "static", "plots")
    os.makedirs(folder, exist_ok=True)

    plt.style.use("dark_background")
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(input1,input2,"ro")
    z,index = K_Means(input1,input2,input3[0])
    print(z)
    zx = [i[0] for i in z]
    zy = [i[1] for i in z]
    ax.plot(zx,zy,"wo")
    ax.legend(["Dataset","Assumed Centers"])

    #filename = f"plot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    filename = "plot.png"
    file_path = os.path.join(folder, filename)
    url_path = f"/static/plots/{filename}"

    plt.savefig(file_path, facecolor="black")
    plt.close()
    socketio.emit("plot",{"src":url_path})
    print("Socketio Sent")
    return {"file_path": file_path, "url": url_path}


"""
def p(data):
    global mat, x, y, input1, input2
    index = findStart(mat[2])
    temp = mat[2][index:index+x+y-1]
    print(temp,input1,input2)
    plt.stem(input1)
    plt.stem(input2)
    plt.stem(temp)    
    filename = f"plot_{time.strftime('%Y%m%d_%H%M%S')}.png"
    path = f"static/plots/{filename}"
    plt.savefig(path, facecolor='black')
    plt.close()

"""


if __name__=="__main__":
    app.run(debug=True,port=6060,host="0.0.0.0")