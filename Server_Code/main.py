import numpy as np
import time
import os
from data_generator import data
from utils import *

app = Flask(__name__)

@app.route('/', methods=['POST'])
def result():
    if request.method=='POST':
        d = data()

        total_pressure = []
        total_ultra = []
        num_of_sensor_real_time = 10 # interval초 동안 받아오는 자세 데이터의 수
        num_of_sensor_total = 10 # n초 동안 받아오는 자세 데이터의 수
        interval = 0.2
        total_hour = 0

        for i in range(num_of_sensor_total):
            '''서버로부터 센서값 받아와서 value에 list 형태로 저장'''

            pressure_list = []
            ultra_list = []

            for i in range(num_of_sensor_real_time):
                pressure_value = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160] #압력센서 값만 받아와야함
                ultra_value = [30,30]

                pressure_list.append(pressure_value)
                ultra_list.append(ultra_value)

                image = d.generator(value) #압력센서 값을 이미지로 전송
                d.save_image(image, os.path.join(path, "temp.png")) #실시간으로 보낼 이미지 폴더에 저장


            '''각 값 DB에 저장'''
            lower_median = np.median(np.asarray(pressure_list), axis=0)
            upper_median = np.median(np.asarray(ultra_list), axis=0)

            total_pressure.append(lower_median)
            total_ultra.append(upper_median)

        '''각 값 DB에 저장'''
        lower_median_total = np.median(np.asarray(total_pressure), axis=0)
        upper_median_total = np.median(np.asarray(total_ultra), axis=0)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
