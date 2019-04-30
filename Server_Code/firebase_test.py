import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import time

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
# app = Flask(__name__)
# app.config.from_object(__name__)

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

    print("entered firebase credential")
    cred = credentials.Certificate('/root/poschair-134c8-firebase-adminsdk-1i2vn-01f260312b.json')
    app = firebase_admin.initialize_app(cred)
    print("finished firebase credential")

    # # This registration token comes from the client FCM SDKs.
    # registration_token = 'YOUR_REGISTRATION_TOKEN'
    #
    # # See documentation on defining a message payload.
    # message = messaging.Message(
    #     android=messaging.AndroidConfig(
    #         ttl=0, #즉시 보낸다는 뜻
    #         priority='normal',
    #         notification=messaging.AndroidNotification(
    #             title='Mind your posture!',
    #             body=posture,
    #         ),
    #     )
    # )
    # The topic name can be optionally prefixed with "/topics/".

    # See documentation on defining a message payload.
    # The topic name can be optionally prefixed with "/topics/".

    # See documentation on defining a message payload.
    # message = messaging.Message(
    #     data={
    #         'title': 'Poschair',
    #         'body': 'Mind your posture!',
    #         },
    #         topic=topic,
    #         )

    message = messaging.Message(
        android=messaging.AndroidConfig(
            ttl=0,
            priority='normal',
            notification=messaging.AndroidNotification(
                title='PosChair',
                body='Mind your posture!',
                ),
                ),
                topic='poschair',
                )

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)

# @app.route('/', methods=['POST'])
# def result():
#     generate_alarm(1)
#     print("sucess")
#     time.sleep(20)
#     return "Done!"

if __name__ == '__main__':
    generate_alarm(1)
    time.sleep(1000)
