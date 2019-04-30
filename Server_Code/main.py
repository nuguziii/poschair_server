import datetime
import sqlite3
import numpy as np
import time
import os
from data_generator import data
#from utils import * #not using yet
from flask import Flask
from flask import g
from flask import redirect
from flask import request
from flask import session
from flask import url_for, abort, render_template, flash
from functools import wraps
from peewee import *
import json
import os


DATABASE = '../POSCHAIR.db'

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)

# create a peewee database instance -- our models will use this database to
# persist information
database = SqliteDatabase(DATABASE)



# model definitions -- the standard "pattern" is to define a base model class
# that specifies which database to use.  then, any subclasses will automatically
# use the correct storage. for more information, see:
# http://charlesleifer.com/docs/peewee/peewee/models.html#model-api-smells-like-django
class BaseModel(Model):
    class Meta:
        database = database

# the user model specifies its fields (or columns) declaratively, like django
class User(BaseModel):
    name = CharField()
    pwd = CharField()
    ID = CharField(unique=True)
    pos_upper = CharField()
    pos_lower = CharField()


class Median(BaseModel):
    ID = CharField()
    lower_median = IntegerField()
    upper_median = IntegerField()
    lower_median_total = IntegerField()
    upper_median_total = IntegerField()


total_pressure = []
total_ultra = []
num_of_sensor_real_time = 10
num_of_sensor_total = 10
interval = 0.2
total_hour = 0
real_time_count = 0
total_time_count = 0


@app.before_request
def before_request():
    print('before_request')
    g.db = database
    g.db.connect()


@app.after_request
def after_request(response):
  print('close_request')
  g.db.close()
  return response


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

@app.route('/image/',methods=['GET','POST'])
def getImage():
        return redirect(url_for('static',filename='posture_sample.png'))

# views -- these are the actual mappings of url to view function
@app.route('/login/', methods=['GET', 'POST'])
def login():
	print('login')
	if request.method == 'POST' and request.form['email']:
		try:
			print ('in try')
			user = User.select(
                    (User.ID == request.form['email']) &
                    (User.pwd == request.form['password'])
                    )
			print ('get success')

		except User.DoesNotExist:
			print ('wrong_pw')
			return 'wrong_pw'

		else:
			print ('success')
			return 'success'
	return 'success'


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
	print('signup')
	if request.method == 'POST':

		try:
			print('post')
			with database.atomic():
				user = User.create(
					name=request.form['name'],
					pwd=request.form['password'],
                    ID=request.form['email'])
			return "success"

		except IntegrityError:
			return 'already_existed'

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
        if request.form['isVideoLike']==0: #추천 영상 비디오
            return
        else: #사용자가 좋아한 비디오
            return



@app.route('/changeVideoLike/',methods=['GET','POST'])
def updateVideoLike():
    if request.method == 'POST':
        user_id = request.form['user_id']
        videoID = request.form['videoID']
        isLike = request.form['isLike']

        if isLike == "like": # 좋아요 x -> 좋아요 db 업데이트

        else: #isLike=="unlike" : 좋아요 -> 좋아요 취소 db 업데이트



@app.route('/posture/', methods=['GET', 'POST'])
def getLabel():
	#label(int 값) string으로 반환한다
	if request.method == 'GET':



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
