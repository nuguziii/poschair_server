import numpy as np
import time
import os
from data_generator import data
from utils import *
import sqlite3
from flask import Flask
from flask import request


app = Flask(__name__)

@app.route('/messaging', methods=['POST'])
def send_msg:
    conn = sqlite3.connect("/root/POSCHAIR.db")
    c = conn.cursor()

    c.execute("SELECT init_pos_lower FROM User WHERE ID = ?", ("choo@naver.com",))
    lower_origin = c.fetchone()[0]
    print(lower_origin)

    c.execute("SELECT total_time FROM Keyword WHERE ID = ?", ("choo@naver.com",))
    total_hour = c.fetchone()[0]
    print(total_hour)

    #계속 돌면서 실시간 메세지 전송
    while(True):

        '''lower_median DB에서 가져옴'''
        c.execute("SELECT lower_median FROM Median WHERE ID = ?", ("choo@naver.com",))
        lower_median = c.fetchone()[0]
        c.execute("SELECT upper_median FROM Median WHERE ID = ?", ("choo@naver.com",))
        upper_median = c.fetchone()[0]

        if np.count_nonzero(lower_median-10)>6: #사용자가 의자에 앉아있는지 판단

            '''각 센서값으로 자세 lower/upper 자세 판단 (이건 median 값)'''
            lower = LBCNet(d.generator(lower_median), d.generator(lower_origin))
            upper = upper_balance_check(upper_median) #upper 자세값 받아옴.

            '''안드로이드로 실시간 메세지 전송'''
            label = messaging(upper, lower) #output은 int 형태로 나옴 이걸 안드로이드로 전송해서 안드로이드에서 메세지 생성
                                    #(app.py, @app.route('/posture/')에서 리턴해 줘야 함)
