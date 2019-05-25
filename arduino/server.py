#Server-side script
from flask import Flask, request
import numpy as np
import torch
import torch.nn as nn
import time
import os
from data_generator import data
import json

app = Flask(__name__)

def test_model(model_name, image):
    #=======================================
    # deep learning model test
    # - input: (180*180*3) image
    # - output: posture label(0-15)
    #=======================================
    model = torch.load("model0225.pth", map_location='cpu')
    model.eval()
    model=model.cpu()

    x = image.astype('float32')/255
    x = x.reshape(1, x.shape[0], x.shape[1], x.shape[2])
    x_ = torch.from_numpy(x.transpose((0,3,1,2)))
    x_ = x_.cpu()

    y_p = model(x_)
    y_p = y_p.detach().numpy()
    return np.argmax(y_p, axis=1)


@app.route('/', methods=['POST'])
def result():
    if request.method=='POST':
        d = data()
        
        data_string = request.form['data']
        value = json.loads(data_string) # pressure and ultrasonic value from arduino

        value = value[:-2]
        image = d.generator(value)
        y = test_model("model0225.pth", image) #model path, image array 입력 => 자세 번호 출력
        print("label predicted: ",y)

        
        return "received!"

if __name__=='__main__':
 app.run(host='0.0.0.0',port=80,debug=True)
