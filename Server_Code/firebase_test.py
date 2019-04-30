import firebase_admin
from firebase_admin import credentials

# create a flask application - this ``app`` object will be used to handle
# inbound requests, routing them to the proper 'view' functions, etc
app = Flask(__name__)
app.config.from_object(__name__)

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
    topic = 'poschair'

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

    # Send a message to the devices subscribed to the provided topic.
    response = messaging.send(message)
    # Response is a message ID string.
    print('Successfully sent message:', response)



@app.route('/', methods=['POST'])
def result():
    generate_alarm(1)

    return "Done!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=False)
