import datetime
from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
#from data_generator import data
from functools import wraps
import sqlite3
import json
import random
from utils import LBCNet
from utils import data
from utils import messaging
from utils import upper_balance_check
import numpy as np



# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)


@app.route('/image/',methods=['GET','POST'])
def getImage():
        return redirect(url_for('static',filename='posture_sample.png'))


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST' and request.form['email']:
        conn = sqlite3.connect("/root/POSCHAIR.db")
        c = conn.cursor()
        iemail = request.form['email']
        ipwd = request.form['pwd']
        c.execute("SELECT count(*) FROM User WHERE ID = '{}'".format(iemail))
        isUser = c.fetchone()[0]

        if isUser == 1:
            c.execute("select count(*) from User where ID='{}' and pwd='{}'".format(iemail,ipwd))
            isRightPwd = c.fetchone()[0]

            if isRightPwd == 1:
                return "success"
            else:
                return "wrong_pw"
        else:
            return "non_email"


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
            conn = sqlite3.connect("/root/POSCHAIR.db")
            c = conn.cursor()
            email = request.form['email']
            name = request.form['name']
            pwd = request.form['pwd']

            c.execute("select count(*) from User where ID='{}'".format(email))
            isEmail = c.fetchone()[0]

            if isEmail == 1:
                return "already_existed"
            else:
                c.execute("INSERT INTO User(ID, name, pwd) VALUES (?,?,?)", [email,name,pwd])
                conn.commit()
                conn.close()
                return 'success'

# main_video 구현 후 지워야
@app.route('/video/',methods=['GET','POST']) #추천 영상 비디오
def sendVideoList():
    if request.method == 'GET':
        conn = sqlite3.connect("/root/POSCHAIR.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        rows = c.execute('''
                         select vidID,vidTitle,view,uploadDate,liked from Youtube_Video
                         ''').fetchall()

        conn.close()

        return json.dumps([dict(i) for i in rows])



@app.route('/likeVideo/',methods=['GET','POST'])  #사용자가 좋아한 비디오
def sendlikeVideoList():
    if request.method == 'GET':
        conn = sqlite3.connect("/root/POSCHAIR.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        rows = c.execute('''
                         select vidID,vidTitle,view,uploadDate,liked from Youtube_Video where liked=1
                         ''').fetchall()
        conn.close()

        if rows == None:
            return json.dumps([])
        else:
            return json.dumps([dict(i) for i in rows])


@app.route('/changeVideoLike/',methods=['GET','POST'])
def updateVideoLike():
    if request.method == 'POST':
        user_id = request.form['user_id']
        videoID = request.form['videoID']
        isLike = request.form['isLike']

        conn = sqlite3.connect("/root/POSCHAIR.db")
        c = conn.cursor()

        if isLike == "like": # 좋아요 x -> 좋아요 db 업데이트
            c.execute("update Youtube_Video set liked=1 where vidID='{}'".format(videoID))
            conn.commit()
            conn.close()

            return "success"

        else: #isLike=="unlike" : 좋아요 -> 좋아요 취소 db 업데이트
            c.execute("update Youtube_Video set liked=0 where vidID='{}'".format(videoID))
            conn.commit()
            conn.close()

            return "success"

@app.route('/dayChart/', methods=['GET', 'POST'])
def sendDayChartInfo():
    if request.method == 'GET':
        print("sendDayChartInfo")
        #date =  request.form['date'] #보내는 기준 날짜 - 해당 날짜부터 7일 이전 날짜까지의 데이터 조회 후 모두 전송

        conn = sqlite3.connect("/root/POSCHAIR.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        rows = c.execute('''
                         select DATE,TOTAL_SITTING,CORRECT_SITTING,k0,k1,k2,k3,k4,k5,k6,CORRECT_PELVIS,LEFT_PELVIS from dayChart
                         ''').fetchall()

        conn.close()

        print(json.dumps([dict(i) for i in rows]))

        return json.dumps([dict(i) for i in rows])


@app.route('/posture/', methods=['GET', 'POST'])
def getLabel():
	#label(int 값) string으로 반환한다
    if request.method == 'GET':
        conn = sqlite3.connect("/root/POSCHAIR.db")
        c = conn.cursor()

        d = data()
        c.execute("SELECT init_pos_lower FROM User WHERE ID = ?", ("choo@naver.com",))
        lower_origin = c.fetchone()[0]
        print(lower_origin)

        lower_origin_list = json.loads(lower_origin)

        c.execute("SELECT total_time FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        total_hour = c.fetchone()[0]
        print(total_hour)

        '''lower_median DB에서 가져옴'''
        c.execute("SELECT lower_median FROM Median WHERE ID = ?", ("choo@naver.com",))
        lower_median = c.fetchone()[0]
        lower_median_list = json.loads(lower_median)
        c.execute("SELECT upper_median FROM Median WHERE ID = ?", ("choo@naver.com",))
        upper_median = c.fetchone()[0]
        upper_median_list = json.loads(upper_median)

        label = 0

        if np.count_nonzero(np.asarray(lower_median_list)-10 > 6): #사용자가 의자에 앉아있는지 판단
            #각 센서값으로 자세 lower/upper 자세 판단 (이건 median
            lower = LBCNet(d.generator(lower_median_list), d.generator(lower_origin_list))
            upper = upper_balance_check(upper_median_list) #upper 자세값 받아옴.
            label = messaging(upper, lower)

        return str(label)


if __name__=='__main__':
	print('connection succeeded')
	app.run(host='0.0.0.0',port=80,debug=True)
