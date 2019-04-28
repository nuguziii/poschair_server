# -*- coding: utf-8 -*-

# =============================================================================
# Test deep learning model PosCNN in model.py
#
# by Chae Eun Lee (02/2019)
# nuguziii@naver.com
# https://github.com/nuguziii
# =============================================================================

# run this to test the model

import numpy as np
import torch
import torch.nn as nn
import time
import os
import sqlite3
import datetime
from data_generator import data
from model import vgg19
import firebase_admin
from firebase_admin import credentials
from peewee import *
from datetime import datetime



def LBCNet(image, guide):
    #=======================================
    # deep learning model LBCNet
    # (Lower Balance Check Network)
    # - input: (90*90*3) image
    # - output: posture label(0-15)
    #=======================================
    start_time = time.time()
    model = torch.load('model.pth', map_location='cpu')
    vgg = vgg19()

    model.eval()
    vgg.eval()

    vgg = vgg.cpu()
    model = model.cpu()

    x = image.astype('float32')/255
    x = x.reshape(1,x.shape[0],x.shape[1],x.shape[2])
    x_ = torch.from_numpy(x.transpose((0, 3, 1, 2)))
    x_ = x_.cpu()

    g = guide.astype('float32')/255
    g = g.reshape(1,g.shape[0],g.shape[1],g.shape[2])
    g_ = torch.from_numpy(g.transpose((0, 3, 1, 2)))
    g_ = g_.cpu()

    #print(vgg(x_).size())
    y_p = []
    x_ = vgg(x_)
    g_ = vgg(g_)
    cat = torch.cat((x_,g_),1)

    temp_y = model(cat)
    temp_y = temp_y.detach().numpy()
    y_p = np.rint(temp_y)

    elapsed_time = time.time() - start_time
    print(y_p, elapsed_time)

    return y_p

def upper_balance_check(value):
    #=====================================
    # upper posture Check
    # input:
    #  value: ultrasonic sensor value
    #          [sensor1, sensor2]
    # output: upper posture
    #======================================
    posture_list = {"Alright":0, "Turtle/Bowed":1, "Slouched":2}
    # 센서 계산 과정 통해서 result 결과 출력
    result = None

    if (value[0] == -1 and value[1] <= 20):
        result = posture_list["Alright"]
    elif (value[0] == -1 and value[1] >= 150):
        result = posture_list["Turtle/Bowed"]
    else:
        result = posture_list["Slouched"]

    return result

def messaging(upper, lower, save_db=False, send_android=False):
    #=====================================
    # generate message list, save DB and send android
    # - input
    #  upper: int type
    #  lower: list type [0,0,0,0]
    #======================================
    # 메세지는 int 형태로 안드로이드에 전송하고, 안드로이드에서 메세지 정의
    messaging_list = {"Alright":0, "moreThanOne":1, "turtle/bowed":2, "legsOnChair":3, "crossedLegs":4, "backbone":5, "others":6}
    send_result = None

    if upper[0]==1 and sum(lower)==0: #둘다 바른자세일 경우 (바른 자세입니다.)
        send_result = messaging_list["Alright"]

    if (upper[1]==1 or upper[2]==1) and (lower[0]==1 or lower[2]==1 or lower[3]==1): #전체적으로 바른자세 유지
        # 전체적으로 몸이 틀어져있습니다.
        send_result = messaging_list["moreThanOne"]
    elif upper[1]==1:
        # 혹시 목을 숙이고 있으신가요?
        send_result = messaging_list["turtle/bowed"]
    elif lower[3]==1:
        # 혹시 다리를 꼬고 계신가요?
        send_result = messaging_list["legsOnChair"]
    elif lower[2]==1:
        # 혹시 다리를 의자 위에 올려놓고 계신가요?
        send_result = messaging_list["crossedLegs"]
    elif lower[1]==1:
        # 허리를 바르게 유지하고 계신가요?
        send_result = messaging_list["backbone"]
    else:
        send_result = messaging_list["others"]

    if save_db:
    	#conn = sqlite3.connect("../../POSCHAIR.db")
    	#c = conn.cursor()
        '''try:
            with database.atomic():
                save = Posture_data.create(
                    ID='choo@naver.com',
                    timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    pos_upper=upper,
                    pos_lower=lower
                    )
                return "success"
        except IntegrityError:
            return "Integrity Error"
		'''
        return send_list

    if send_android:
        '''send_result 안드로이드에 전송'''

def is_alarm():
    #=====================================
    # check if we should alert alarm
    # - output: list type (alarm_list)
    #======================================
    #{"바른자세":0, "목":2, "어깨":3, "다리꼬기":4, "앞으로 기울임":5, "뒤로기댐":6, "양반다리":7, "불균형":8, "error":-1}
    alarm_list = []
    '''DB에서 10분간 데이터 계산해서 85% 비율을 차지한 자세를 alarm_list에 넣음'''
    #bring data of 10 minutes from the database
    t_now = datetime.datetime.now()
    t_old = t_now - datetime.timedelta(minutes = 10)
    #posture_data 이용해서 판단하기 10분전
    #cur.execute("SELECT * FROM Posture_data WHERE date BETWEEN t_old AND t_now")
    #rows = cur.fetchall()
    #count = 0
    
    #for row in rows:
    #	print(row)


    #check if the percentage is over 85%

    #put the posture in the alarm_list
    #교집합 구하기
    result = [0]*len(a)
    for i in range(len(a)):
        if a[i]==b[i]:
            result[i]=a[i]

    notification_list = {"Alright":0, "moreThanOne":1, "turtle/bowed":2, "backbone":3, "legs":4, "others":5}
    if sum(result)==0: #바른자세
        return notification_list["Alright"]
    elif sum(result)>=2: #전체적으로 바른 자세 유지 알람
        return notification_list["moreThanOne"]
    elif result[1]==1: #목 운동 알람
        return notification_list["turtle/bowed"]
    elif result[4]==1: #허리 운동 알람
        return notification_list["backbone"]
    elif result[5]==1 or result[6]==1: #다리 바르게 알람
        return notification_list["legs"]
    else: #자세 바르게 알람
        return notification_list["others"]





    return alarm_list

def generate_alarm(alarm_value):
    #=====================================
    # send alarm alert to android
    # - input:
    #     integer(indicates the current posture alarm label)
    #======================================

    '''
    1. current_posture와 alarm_list 비교해서 교집합 현재 alarm_list에 저장
    3. alarm_list 가 0이 아닐 경우 android에 alarm_list 전송
    '''
    posture = None

    #예시임 5까지 추가해야하고 메세지 바꿔야함
    if alarm_value == 0:
    	return 0 #don't send the alarm
    elif alarm_value == 1:
        posture = 'turtle neck'
    elif (alarm_value ==2):
        posture = 'slouched'

    cred = credentials.Certificate('/root/poschair-134c8-firebase-adminsdk-1i2vn-01f260312b.json')
    app = firebase_admin.initialize_app(cred)

    # This registration token comes from the client FCM SDKs.
    registration_token = 'YOUR_REGISTRATION_TOKEN'

    # See documentation on defining a message payload.
    message = messaging.Message(
        android=messaging.AndroidConfig(
            ttl=0, #즉시 보낸다는 뜻
            priority='normal',
            notification=messaging.AndroidNotification(
                title='Mind your posture!',
                body=posture,
            ),
        )
    )

    # Send a message to the device corresponding to the provided
    # registration token.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)





def keyword_matching(upper, lower):
    #=====================================
    # save in Keyword Database
    # - input:
    #   upper: int type
    #   lower: list type
    #======================================
	'''    
	keyword_list = {"목디스크":"k0", "거북목":"k1", "어깨굽음":"k2", "골반불균형":"k3", "척추틀어짐":"k4", "고관절통증":"k5", "무릎통증":"k6", "혈액순환":"k7"}
    now = datetime.datetime.now()
     DB에서 해당되는 키워드에 +1을 해줌 (Upper 경우)
    if upper is 1:
        keyword_list["목디스크"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k0).where(Keyword.ID == "choo@naver.com"))
                temp += 1
                query = Keyword.update(
                    Keyword.k0 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"

    elif upper is 2:
        keyword_list["거북목"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k1).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k1 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"


    elif upper is 3 or upper is 4:
        keyword_list["어깨굽음"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k2).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k2 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"

     DB에서 해당되는 키워드에 +1을 해줌 (Lower 경우)
    if lower[2] is 1:
        keyword_list["골반불균형"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k3).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k3 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"

        keyword_list["척추틀어짐"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k4).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k4 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"


        keyword_list["고관절통증"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k5).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k5 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"



        keyword_list["무릎통증"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k6).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k6 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"


    elif lower[3] is 1:
        keyword_list["골반불균형"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k3).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k3 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"

        keyword_list["척추틀어짐"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k4).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k4 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"


        keyword_list["혈액순환"]
        try:
            with database.atomic():
                temp = int(Keyword.select(Keyword.k7).where(Keyword.ID == "choo@naver.com"))
                temp ++
                query = Keyword.update(
                    Keyword.k7 = int(temp)
                    ).where(Keyword.ID == "choo@naver.com")
            return "keyword_update_success"
        except IntegrityError:
            return "Integrity Error"


    elif lower[0] is 1:
        keyword_list["골반불균형"]
        keyword_list["척추틀어짐"]

    if lower[1] is 1 and upper is not 3:
        keyword_list["어깨굽음"]
	'''

def generate_keyword_for_video_matching():
    #=====================================
    # generate keyword from Database
    # DB에 n시간 정도의 자세 키워드 데이터를 확인한 다음
    # 각 키워드, 시간을 출력함
    # - output: dictionary
    # ex) {0: 128, 1:330 ...}
    #======================================
    '''
    1. DB에서 n시간 정도의 자세 키워드 데이터 가져옴
    2. 각 키워드 별 시간 계산해서 dictionary 형태로 출력
    '''
    keyword_dict = None
    return keyword_dict

def video_matching(keyword):
    #=====================================
    # generate_keyword_for_video_matching 으로부터 keyword 받아와서
    # video url list string 형태로 안드로이드에 보냄
    # - input: keyword(dictionary)
    #======================================
    keyword_list = {"목디스크":0, "거북목":1, "어깨굽음":2, "골반불균형":3, "척추틀어짐":4, "고관절통증":5, "무릎통증":6, "혈액순환":7}
    video_dict = {0:"목운동", 1:"거북목운동", 2:"어깨/허리스트레칭", 3:"골반교정운동/체형교정운동", 4:"척추교정운동", 5:"고관절스트레칭", 6:"무릎운동", 7:"다리스트레칭/혈액순환", 8:"전신"}
    import operator
    sorted_key = sorted(keyword.items(), key=operator.itemgetter(1), reverse=True) #시간 많은 순으로 정렬

    video_list = []

    for k, v in dictionary.items():
    	if v == sorted_key[0][0]: 
        	video_list.append(video_dict[k])

    	if len(video_list)>3:
        	video_list = [video_dict[8]]

    '''
    video_list에 해당하는 url들 db에서 가져오기
    가져올 때 조희수/like 수 등 생각해서 높은 순서대로 상위 5개 가져오기.
    '''

    ''' url list 안드로이드에 전송 '''
