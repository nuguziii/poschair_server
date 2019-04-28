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
from data_generator import data
from model import vgg19
import firebase_admin
from firebase_admin import credentials


def LBCNet(model_name, image):
    #=======================================
    # deep learning model LBCNet
    # (Lower Balance Check Network)
    # - input: (90*90*3) image
    # - output: posture label(0-15)
    #=======================================
    model = torch.load(model_name, map_location='cpu')
    vgg = vgg19()

    model.eval()
    vgg.eval()

    vgg = vgg.cpu()
    model = model.cpu()

    x = image.astype('float32')/255
    x = x.reshape(1,x.shape[0],x.shape[1],x.shape[2])
    x_ = torch.from_numpy(x.transpose((0, 3, 1, 2)))
    x_ = x_.cpu()

    #print(vgg(x_).size())
    y_p = model(vgg(x_))
    result = []
    result.append(np.argmax(y_p[0].detach().numpy,axis=0))
    result.append(np.argmax(y_p[1].detach().numpy,axis=0))
    result.append(np.argmax(y_p[2].detach().numpy,axis=0))
    result.append(np.argmax(y_p[3].detach().numpy,axis=0))
    #y_p = np.asarray(list(y_p.item()))
    #y_p = y_p.detach().numpy()
    #print(y_p, y_p.shape)
    return result

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
    if (value[0] == -1 && value[1] <= 20):
        result = 0
    elif (value[0] == -1 && value[1] >= 150):
        result = 1
    else:
        result = 2

    return posture_list[result]

def messaging(upper, lower, save_db=False, send_android=False):
    #=====================================
    # generate message list, save DB and send android
    # - input
    #  upper: int type
    #  lower: list type [0,0,0,0]
    #======================================
    # 메세지는 int 형태로 안드로이드에 전송하고, 안드로이드에서 메세지 정의
    messaging_list = {"바른자세":0, "둘 이상":1, "목":2, "어깨":3, "다리꼬기":4, "앞으로 기울임":5, "뒤로기댐":6, "양반다리":7, "불균형":8, "error":-1}
    send_list = []

    if upper==0 and sum(lower)==0: #둘다 바른자세일 경우 (바른 자세입니다.)
        send_list.append(meassaging_list["바른자세"])

    if upper==3 or upper==4: #허리굽힘 & 등에 무리가는 자세(허리)
        #몸이 앞으로 기울어져 있습니다.
        send_list.append(messaging_list["앞으로 기울임"])
    elif lower[1]==1: #등에 무리가 가는 자세입니다.
        send_list.append(messaging_list["뒤로기댐"])

    if lower[3]>=1: #다리를 꼰 상태인가요?
        send_list.append(messaging_list["다리꼬기"])
    if lower[2]>=1: #다리를 의자에 올려놓은 상태인가요?
        send_list.append(messaging_list["양반다리"])
    if lower[0]>=1: #한쪽으로 중심이 쏠렸습니다.
        send_list.append(messaging_list["불균형"])

    if upper==1 or upper==2: #목을 바르게 유지해주세요
        send_list.append(messaging_list["목"])

    if save_db:
        '''DB에 send_list(현재 자세) 저장'''
        return send_list

    if len(send_list)>1:
        send_list = [messaging_list["둘 이상"]]

    if send_android:
        '''send_list안드로이드에 전송'''

def is_alarm():
    #=====================================
    # check if we should alert alarm
    # - output: list type (alarm_list)
    #======================================
    #{"바른자세":0, "목":2, "어깨":3, "다리꼬기":4, "앞으로 기울임":5, "뒤로기댐":6, "양반다리":7, "불균형":8, "error":-1}
    alarm_list = []
    '''DB에서 10분간 데이터 계산해서 85% 비율을 차지한 자세를 alarm_list에 넣음'''

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
    if (alarm_value == 0) {
        return 0 #don't send the alarm
    }
    elif (alarm_value == 1) {
        posture = 'turtle neck'
    }
    elif (alarm_value ==2) {
        posture = 'slouched'
    }

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
    keyword_list = {"목디스크":0, "거북목":1, "어깨굽음":2, "골반불균형":3, "척추틀어짐":4, "고관절통증":5, "무릎통증":6, "혈액순환":7}

    ''' DB에서 해당되는 키워드에 +1을 해줌 (Upper 경우)'''
    if upper is 1:
        keyword_list["목디스크"]
    elif upper is 2:
        keyword_list["거북목"]
    elif upper is 3 or upper is 4:
        keyword_list["어깨굽음"]

    ''' DB에서 해당되는 키워드에 +1을 해줌 (Lower 경우)'''
    if lower[2] is 1:
        keyword_list["골반불균형"]
        keyword_list["척추틀어짐"]
        keyword_list["고관절통증"]
        keyword_list["무릎통증"]
    elif lower[3] is 1:
        keyword_list["골반불균형"]
        keyword_list["척추틀어짐"]
        keyword_list["혈액순환"]
    elif lower[0] is 1:
        keyword_list["골반불균형"]
        keyword_list["척추틀어짐"]

    if lower[1] is 1 and upper is not 3:
        keyword_list["어깨굽음"]

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
    if v == sorted_key[0][0]: #가장 시간 많은 것들 video list에 저장
        video_list.append(video_dict[k])

    if len(video_list)>3:
        video_list = [video_dict[8]]

    '''
    video_list에 해당하는 url들 db에서 가져오기
    가져올 때 조희수/like 수 등 생각해서 높은 순서대로 상위 5개 가져오기.
    '''

    ''' url list 안드로이드에 전송 '''
