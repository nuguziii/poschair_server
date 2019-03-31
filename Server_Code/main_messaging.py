import numpy as np
import time
import os
from data_generator import data
from utils import *

if __name__ == '__main__':
    d = data()

    '''DB에서 초기자세 데이터 받아올 것'''
    lower_origin = None #DB에서 초기 압력센서 자세값 받아옴
    upper_origin = None #DB에서 초기 초음파센서 자세값 받아옴

    '''오늘 총 시간 DB에서 받아옴'''
    total_hour = 0

    #계속 돌면서 실시간 메세지 전송
    while(True):

        '''lower_median DB에서 가져옴'''
        lower_median = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160]
        upper_median = [0,0]

        if np.count_nonzero(lower_median-10)>6: #사용자가 의자에 앉아있는지 판단

            '''DB에 총 시간 계속 업데이트'''
            total_hour += interval*num_of_sensor_tatal

            '''각 센서값으로 자세 lower/upper 자세 판단 (이건 median 값)'''
            lower = LBCNet("model_0326.pth", d.generator(lower_median)) #딥러닝 모델로 lower 자세값 받아옴.
            upper = upper_balance_check(upper_origin, upper_median) #upper 자세값 받아옴.

            '''안드로이드로 실시간 메세지 전송'''
            messaging(upper, lower, send_android=True) #output은 int 형태로 나옴 이걸 안드로이드로 전송해서 안드로이드에서 메세지 생성