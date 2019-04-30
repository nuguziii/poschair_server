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
#import firebase_admin
#from firebase_admin import credentials



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



    if upper==0 and sum(lower)==0: #둘다 바른자세일 경우 (바른 자세입니다.)
        send_result = messaging_list["Alright"]
    if (upper==1 or upper==2) and (lower[0]==1 or lower[2]==1 or lower[3]==1): #전체적으로 바른자세 유지
        # 전체적으로 몸이 틀어져있습니다.
        send_result = messaging_list["moreThanOne"]
    elif upper==1:
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

    d = data()
    conn = sqlite3.connect("../../POSCHAIR.db")
    c = conn.cursor()

    #bring data of 10 minutes from the database
    t_now = datetime.datetime.now()
    t_old = t_now - datetime.timedelta(minutes = 10)

    #posture_data 이용해서 판단하기 10분전
    c.execute("SELECT * FROM Posture_data WHERE date BETWEEN t_old AND t_now")
    rows = c.fetchall()

    upper1cnt = 0
    lower1cnt = 0
    lower2cnt = 0
    lower3cnt = 0
    lower4cnt = 0
    cnt = 0

    for row in rows:
        print(row)
        upper1cnt += row[2]
        lower1cnt += row[3]
        lower2cnt += row[4]
        lower3cnt += row[5]
        lower4cnt += row[6]
        cnt += 1

    #calculate whether percentage is over 85%
    percent = [0,0,0,0,0]
    percent[0] = upper1cnt / cnt
    percent[1] = lower1cnt / cnt
    percent[2] = lower2cnt / cnt
    percent[3] = lower3cnt / cnt
    percent[4] = lower4cnt / cnt

    #if it is over 85% add 1 at the end of alarm_list else add 0
    for i in range(len(percent)):
        if percent[i] >= 0.85:
            alarm_list.append(1)
        else: alarm_list.append(0)


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
    # {"Alright":0, "Turtle/Bowed":1, "Slouched":2}
    keyword_list = {"Turtle/Bowed":"k0", "Slouched":"k1", "PelvisImbalance":"k2", "Scoliosis":"k3", "HipPain":"k4", "KneePain":"k5", "PoorCirculation":"k6"}
    now = datetime.datetime.now()


    conn = sqlite3.connect("../../POSCHAIR.db")
    c = conn.cursor()

    if upper is 1:
        c.execute("SELECT k0 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k0 = ? WHERE ID = ?", (key, "choo@naver.com"))

    elif upper is 2:
        c.execute("SELECT k1 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = c.fetchone()[0]
        print(key, type(key))
        key += 1
        c.execute("UPDATE Keyword SET k1 = ? WHERE ID = ?", (key, "choo@naver.com"))

    #DB에서 해당되는 키워드에 +1을 해줌 (Lower 경우)
    if lower[2] is 1:
        c.execute("SELECT k2 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k2 = ? WHERE ID = ?", (key, "choo@naver.com"))

        c.execute("SELECT k3 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k3 = ? WHERE ID = ?", (key, "choo@naver.com"))

        c.execute("SELECT k4 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k4 = ? WHERE ID = ?", (key, "choo@naver.com"))

        c.execute("SELECT k5 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k5 = ? WHERE ID = ?", ( key, "choo@naver.com"))

    elif lower[3] is 1:
        c.execute("SELECT k2 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k2 = ? WHERE ID = ?", (key, "choo@naver.com"))

        c.execute("SELECT k3 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k3 = ? WHERE ID = ?", (key, "choo@naver.com"))


        c.execute("SELECT k6 FROM Keyword WHERE ID = ?", ( "choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k6 = ? WHERE ID = ?", (key, "choo@naver.com"))

    elif lower[0] is 1:
        c.execute("SELECT k2 FROM Keyword WHERE ID = ?", ( "choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k2 = ? WHERE ID = ?", (key, "choo@naver.com"))

        c.execute("SELECT k3 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k3 = ? WHERE ID = ?", (key, "choo@naver.com"))

    if lower[1] is 1 and upper is not 2:
        c.execute("SELECT k1 FROM Keyword WHERE ID = ?", ("choo@naver.com",))
        key = int(c.fetchone()[0])
        key += 1
        c.execute("UPDATE Keyword SET k1 = ? WHERE ID = ?", (key, "choo@naver.com"))

    conn.commit()


def generate_keyword_for_video_matching():
    #=====================================
    # generate keyword from Database
    # DB에 n시간 정도의 자세 키워드 데이터를 확인한 다음
    # 각 키워드, 시간을 출력함
    # - output: dictionary
    # ex) {"k0": 128, 1:330 ...}
    #======================================
    '''
    1. DB에서 n시간 정도의 자세 키워드 데이터 가져옴
    2. 각 키워드 별 시간 계산해서 dictionary 형태로 출력
    '''

    conn = sqlite3.connect("../../POSCHAIR.db")
    c = conn.cursor()

    keyword_dict = {"k0":0, "k1":0, "k2":0, "k3":0, "k4":0, "k5":0, "k6":0, "k7":0}

    t_now = datetime.datetime.now()
    t_old = t_now - datetime.timedelta(hours = 48)

    c.execute("SELECT * FROM Keyword WHERE ID = ?", ("choo@naver.com",))
    rows = c.fetchall()

    for row in rows:
        for i in range(7):
            keyword_dict["k"+str(i)] += row[i+1]


    return keyword_dict

def video_matching(keyword):
    #=====================================
    # generate_keyword_for_video_matching 으로부터 keyword 받아와서
    # video url list string 형태로 안드로이드에 보냄
    # - input: keyword(dictionary)
    #======================================
    # {"Turtle/Bowed":"k0", "Slouched":"k1", "PelvisImbalance":"k2", "Scoliosis":"k3", "HipPain":"k4", "KneePain":"k5", "PoorCirculation":"k6"}
    keyword_list = {"k0":1, "k1":2, "k2":3, "k3":4, "k4":5, "k5":6, "k6":7}
    # {"k0":"거북목운동", "k1":"어깨/허리스트레칭", "k2":"골반교정운동/체형교정운동", "k3":"척추교정운동", "k4":"고관절스트레칭", "k5":"무릎운동", "k6":"다리스트레칭/혈액순환", "k7":"전신"}
    video_dict = {"k0":0, "k1":1, "k2":2, "k3":3, "k4":4, "k5":5, "k6":6, "k7":7}
    import operator
    sorted_key = sorted(keyword.items(), key=operator.itemgetter(1), reverse=True) #시간 많은 순으로 정렬

    video_list = []

    if sorted_key[0][1] == sorted_key[1][1]:
        video_keyword = video_dict["k7"]
    else:
        video_keyword = video_dict[sorted_key[0][0]]

    '''
    video_list에 해당하는 url들 db에서 가져오기
    가져올 때 조희수/like 수 등 생각해서 높은 순서대로 상위 5개 가져오기.
    '''

    conn = sqlite3.connect("../../POSCHAIR.db")
    c = conn.cursor()

    weighted = []
    for i in range(7):
        tmp = "k"+str(i)
        c.execute("SELECT * FROM Youtube_Video WHERE keyword = ?", tmp)
        #조회수/like 수
        #liked
        row = c.fetchone()[0]
        weighted.append((row[6], row[5]/row[4], tmp))
        weighted.sort(reverse=True)

    for i in range(4):
        c.execute("SELECT ? FROM Youtube_Video WHERE keyword = ?", (vidID, weighted[i][2]))
        tmpID = c.fetchone()[0]
        video_list.append(tmpID)

    return video_list

if __name__ == '__main__':
    keyword_matching(2, [0,0,0,1])
    keyword = generate_keyword_for_video_matching()
    print("keyword:", keyword)
    print("video_list: ", video_matching(keyword))
