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
        conn = sqlite3.connect("../POSCHAIR.db")
        c = conn.cursor()
        iemail = request.form['email']
        ipwd = request.form['pwd']
        c.execute("SELECT ID, pwd FROM User WHERE ID = ?", (iemail,))
        k = c.fetchone()[0]

        if k[0]==iemail and k[1] == ipwd :
            print('fetch success')
        else:
            print('fetch failed')

        return 'success'
        '''
            c.execute("select count(*) from User where ID={}".format(request.form['email']))
            isUser = c.fetchone()

            if isUser == 1:
                c.excute("select count(*) from User where ID={} and pwd={}".format(request.form['email'],request.form['password']))
                isRightPwd = c.fetchone()

                if isRightPwd == 1:
                    return "success"
                else:
                    return "wrong_pw"
            else:
                return 'non_email'
        '''
@app.route('/signup/', methods=['GET', 'POST'])
def signup():
	if request.method == 'POST':
            '''
			conn = sqlite3.connect("../POSCHAIR.db")
            c = conn.cursor()

            c.excute("select count(*) from User where ID={}".format(request.form['email']))
            isUser = c.fetchone()

            if isUser == 1:
                return "already_existed"
            else:
                c.excute("insert into User(ID,name,pwd) values(?,?,?,?,?)",request.form['email'],request.form['name'],request.form['password'])
                conn.commit()
                conn.close()

                return "success"

	         return render_template('./index.html')
           '''
        conn = sqlite3.connect("../POSCHAIR.db")
        c = conn.cursor()
        input = [request.form['email'], request.form['name'], request.form['pwd']]
        c.execute("INSERT INTO User(ID, name, pwd) VALUES (?,?,?)", input)
        conn.commit()
        conn.close()

        return render_template('./index.html')

'''
@app.route('/addInfo/', methods=['GET', 'POST'])
def addInfo():
	#age, sex, height, weight
	if request.method == 'POST':

	return render_template('./index.html')
'''

# main_video 구현 후 지워야
@app.route('/video/',methods=['GET','POST']) #추천 영상 비디오
def sendVideoList():
    if request.method == 'GET':
        conn = sqlite3.connect("../POSCHAIR.db")
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
        conn = sqlite3.connect("../POSCHAIR.db")
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

        conn = sqlite3.connect("../POSCHAIR.db")
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


@app.route('/posture/', methods=['GET', 'POST'])
def getLabel():
	#label(int 값) string으로 반환한다
    if request.method == 'GET':
        label = random.randrange(0,7) #현재 random인 상태 -> main_messaging 이용해서 수정해야
        return str(label)


if __name__=='__main__':
	print('connection succeeded')
	app.run(host='0.0.0.0',port=80,debug=True)
