import datetime
import sqlite3
import numpy as np
import time
import os
import json
from data_generator import data
#from utils import *
from functools import wraps

if __name__ == '__main__':
    d = data()
    conn = sqlite3.connect("../../POSCHAIR.db")
    c = conn.cursor()
    #DB에서 초기자세 데이터 받아올 것
    
    c.execute("SELECT init_pos_lower FROM User WHERE ID = ?", ("choo@naver.com"))
    rows = c.fetchall()
    print(rows, type(rows))
    for row in rows:
        print(row)

#    		init_upper_data = User.select(User.init_pos_upper).where(User.ID == "choo@naver.com")
 #   		init_lower_data = User.select(User.init_pos_lower).where(User.ID == "choo@naver.com")
  #  		init_upper_data.execute()
   # 		init_lower_data.execute()
    	


'''


    #DB에서 초기자세 데이터 받아올 것
    lower_origin = None #DB에서 초기 압력센서 자세값 받아옴
    upper_origin = None #DB에서 초기 초음파센서 자세값 받아옴

    #DB에서 초기 압력센서 자세값 받아옴
    init_lower_string = json.loads(init_lower_data)

    #DB에서 초기 초음파센서 자세값 받아옴
    init_upper_string = json.loads(init_upper_data)

    #계속 돌면서 keyword 저장
    while(True):

        #lower_median_total, upper_median_total DB에서 가져옴
        try:
        	with database.atomic():
        		lower_median_total_data = Median.select(Median.lower_median_total)
        		upper_median_total_data = Median.select(Median.upper_median_total)
        	return "success"
        except: IntegrityError
        	return "IntegrityError"

        lower_median_total = json.loads(lower_median_total_data)
        upper_median_total = json.loads(upper_median_total_data)

        if np.count_nonzero(lower_median-10)>6: #사용자가 의자에 앉아있는지 판단

            #각 센서값으로 자세 lower/upper 자세 판단 (이건 median 값)
            lower = LBCNet("model_0326.pth", d.generator(lower_median_total)) #딥러닝 모델로 lower 자세값 받아옴.
            upper = upper_balance_check(upper_origin, upper_median_total) #upper 자세값 받아옴.

            #실시간 자세 DB에 저장
            current_posture = messaging(upper, lower, save_db=True) #output은 int 형태로 나옴 이걸 안드로이드로 전송해서 안드로이드에서 메세지 생성

            #키워드 매칭 알고리즘(DB에 저장하는 함수)
            keyword_matching(upper, lower) #자세 값을 기반으로 디비에 해당 키워드 별 +1 해줌

            #알림 확인 및 전송
            alarm_list = is_alarm() #알람 보낼 리스트가 있는지 확인
            if len(alarm_list) is not 0: #알람 리스트가 있으면
                result = generate_alarm(alarm_list) #알람 전송
'''
