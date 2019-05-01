import datetime

from flask import Flask
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
import sqlite3
import json



# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)

# create a peewee database instance -- our models will use this database to
# persist information

# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django

@app.route('/image/',methods=['GET','POST'])
def getImage():
        return redirect(url_for('static',filename='posture_sample.png'))

# views -- these are the actual mappings of url to view function
@app.route('/login/', methods=['GET', 'POST'])
def login():
	print('login')
	if request.method == 'POST' and request.form['email']:
            conn = sqlite3.connect("../../POSCHAIR.db")
            c = conn.cursor()

            c.excute("select count(*) from User where ID={}".format(request.form['email']))
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

@app.route('/signup/', methods=['GET', 'POST'])
def signup():
	print('signup')
	if request.method == 'POST':
			print('post')

            conn = sqlite3.connect("../../POSCHAIR.db")
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



@app.route('/addInfo/', methods=['GET', 'POST'])
def addInfo():
	#age, sex, height, weight
	if request.method == 'POST':
		try:
			print('addInfo')
			#with database.atomic():
			#	query = User.update(
			#		age=int(request.form['age']),
			#		gender=request.form['sex'],
			#		height=int(request.form['height']),
			#		weight=int(request.form['weight'])).where(User.ID == "choo@naver.com")
			#	query.execute()
			return "success"

		except IntegrityError:
			return 'addInfo_error'

@app.route('/video/',methods=['GET','POST'])
def sendVideoList():
    if request.method == 'GET':
        user_id = request.form['user_id']

        conn = sqlite3.connect("../../POSCHAIR.db")
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if request.form['isVideoLike']==0: #추천 영상 비디오
            rows = c.execute('''
                             select * from Youtube_Video
                             ''').fetchall()

            conn.close()

            return json.dumps([dict(i) for i in rows])

        else: #사용자가 좋아한 비디오
            rows = c.execute('''
                             select * from Youtube_Video where liked=1
                             ''').fetchall()
            conn.commit()
            conn.close()

            return json.dumps([dict(i) for i in rows])


@app.route('/changeVideoLike/',methods=['GET','POST'])
def updateVideoLike():
    if request.method == 'POST':
        user_id = request.form['user_id']
        videoID = request.form['videoID']
        isLike = request.form['isLike']

        conn = sqlite3.connect("../../POSCHAIR.db")
        c = conn.cursor()

        if isLike == "like": # 좋아요 x -> 좋아요 db 업데이트
            c.execute("update Youtube_Video set liked=1 where vidID={}".format(videoID))
            conn.commit()
            conn.close()

            return "success"

        else: #isLike=="unlike" : 좋아요 -> 좋아요 취소 db 업데이트
            c.execute("update Youtube_Video set liked=0 where vidID={}".format(videoID))
            conn.commit()
            conn.close()

            return "success"

@app.route('/posture/', methods=['GET', 'POST'])
def getLabel():
    label=-1
	#label(int 값) string으로 반환한다
    if request.method == 'GET':
        if label>7:
            label=0
        else:
            label+=1
        return str(label)


if __name__=='__main__':
	print('connection succeeded')
	app.run(host='0.0.0.0',port=80,debug=True)
