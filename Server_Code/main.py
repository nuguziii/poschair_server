import datetime

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

        
        if real_time_count == num_of_sensor_real_time:
          real_time_count = 0
          lower_median = np.median(np.asarray(pressure_list), axis=0)
          upper_median = np.median(np.asarray(ultra_list), axis=0)
          print("lower_median: "+ str(lower_median))
          print("upper_median: "+ str(upper_median))
          #DB에 저장하기
          try:
            with database.atomic():
              query1 = Median.update(
                lower_median=(lower_median),
                upper_median=(upper_median)
                ).where(Median.ID=='choo@naver.com')
              query1.execute()
              print("query1 finished")
          except IntegrityError:
            print('IntegrityError')
          global total_pressure
          global total_ultra
          total_pressure.append(lower_median)
          total_ultra.append(upper_median)
          print('success')

        
        if total_time_count == num_of_sensor_total * num_of_sensor_real_time:
          total_time_count = 0
          lower_median_total = np.median(np.asarray(total_pressure), axis=0)
          upper_median_total = np.median(np.asarray(total_ultra), axis=0)
          print("lower_median_total: "+ str(lower_median_total))
          print("upper_median_total: "+ str(upper_median_total))
          #DB에 저장하기
          try:
            with database.atomic():
              query2 = Median.update(
                lower_median_total=(lower_median_total),
                upper_median_total=(upper_median_total)
                ).where(Median.ID=='choo@naver.com')
              query2.execute()
              print("query2 finished")
          except IntegrityError:
            print('IntegrityError')
          print('succeess')
    print('post success')
    return 'complete'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
