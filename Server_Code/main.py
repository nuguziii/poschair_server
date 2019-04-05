import numpy as np
import time
import os
from data_generator import data
#from utils import * #not using yet
from flask import Flask, request, g
import json
import os

app = Flask(__name__)

global total_pressure
global total_ultra
global num_of_sensor_real_time = 10
global num_of_sensor_total = 10
global interval = 0.2
global total_hour = 0
global real_time_count = 0
global total_time_count = 0

@app.route('/', methods=['POST'])
def result():
    if request.method=='POST':
        d = data()

        pressure_list = []
        ultra_list = []

        data_string = request.form['data']
        data_list = json.loads(data_string) # pressure and ultrasonic value from arduino

        pressure_value = data_list[:-2]
        ultra_value = data_list[-2:]

        pressure_list.append(pressure_value)
        ultra_list.append(ultra_value)

        image = d.generator(pressure_value) #압력센서 값을 이미지로 전송

        d.save_image(image, "../temp.png") #실시간으로 보낼 이미지 폴더에 저장

        real_time_count+=1
        total_time_count+=1

        if real_time_count == num_of_sensor_real_time:
           lower_median = np.median(np.asarray(pressure_list), axis=0)
           upper_median = np.median(np.asarray(ultra_list), axis=0)
           print("lower_median: "+lower_median)
           print("upper_median: "+upper_median)
           #DB에 저장하기

           total_pressure.append(lower_median)
           total_ultra.append(upper_median)

        if total_time_count == num_of_sensor_total * num_of_sensor_real_time:
           lower_median_total = np.median(np.asarray(total_pressure), axis=0)
           upper_median_total = np.median(np.asarray(total_ultra), axis=0)
           print("lower_median_total: "+lower_median_total)
           print("upper_median_total: "+upper_median_total)
            #DB에 저장하기
        return "Complete!!"

if __name__ == '__main__':
    total_pressure = []
    total_ultra = []
    num_of_sensor_real_time = 10
    num_of_sensor_total = 10
    interval = 0.2
    total_hour = 0
    real_time_count = 0
    total_time_count = 0
    app.run(host='0.0.0.0', port=80, debug=False)
