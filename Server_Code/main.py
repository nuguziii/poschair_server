import datetime
import sqlite3
import numpy as np
import time
import os
from data_generator import data
from utils import *
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
from functools import wraps

import json
import os


# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)


total_pressure = []
total_ultra = []
num_of_sensor_real_time = 10
num_of_sensor_total = 10
interval = 0.2
total_hour = 0
real_time_count = 0
total_time_count = 0


@app.route('/', methods=['POST'])
def result():
    print ('connection success')
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

        d.save_image(image, "../static/posture_sample.png") #실시간으로 보낼 이미지 폴더에 저장

        global real_time_count
        global total_time_count
        real_time_count+=1
        total_time_count+=1

        conn = sqlite3.connect("../POSCHAIR.db")
        c = conn.cursor()
        if real_time_count == num_of_sensor_real_time:
          real_time_count = 0
          lower_median = np.median(np.asarray(pressure_list), axis=0)
          upper_median = np.median(np.asarray(ultra_list), axis=0)
          lower_median = list(map(int, lower_median))
          upper_median = list(map(int, upper_median))
          print("lower_median: "+ str(lower_median))
          print("upper_median: "+ str(upper_median))
          #DB에 저장하기
          c.execute("UPDATE Median SET lower_median = ?, upper_median = ? WHERE ID = ?", (str(lower_median), str(upper_median), 'choo@naver.com'))
          conn.commit()

          global total_pressure
          global total_ultra
          total_pressure.append(lower_median)
          total_ultra.append(upper_median)
          print('success')

        if total_time_count == num_of_sensor_real_time * num_of_sensor_total:
          total_time_count = 0
          lower_median_total = np.median(np.asarray(total_pressure), axis=0)
          upper_median_total = np.median(np.asarray(total_ultra), axis=0)
          lower_median_total = list(map(int, lower_median_total))
          upper_median_total = list(map(int, upper_median_total))
          print("lower_median_total: "+ str(lower_median_total))
          print("upper_median_total: "+ str(upper_median_total))
          #DB에 저장하기
          c.execute("UPDATE Median SET lower_median_total = ?, upper_median_total = ? WHERE ID = ?", (str(lower_median_total), str(upper_median_total), 'choo@naver.com'))
          conn.commit()


          print('db_total_input_succeess')
        conn.close()
    print('post success')

    return 'complete'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
