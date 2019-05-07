import numpy as np
import time
import os
from utils import *

if __name__ == '__main__': #함수로 바꾼 후 @app.route('/video/',methods=['GET','POST'])에서 호출해야 or 이 부분을 app.py로 이동

	while(True): #안드로이드로 부터 video 신호 들어오면
		conn = sqlite3.connect("../POSCHAIR.db")
		c = conn.cursor()

		keyword = generate_keyword_for_video_matching(conn) #기록을 통해 keyword dictionary 생성
		video_list = video_matching(keyword, conn) #안드로이드에 url list 보냄
		'''
		for videoID in video_list:
			row = c.execute("select vidID,vidTitle,view,uploadDate,liked from Youtube_Video where vidID={}".format(videoID)).fetchone()[0]

		row 내용들 -> rows로 합친 후
		return json.dumps([dict(i) for i in rows])
		'''
		print(video_list)
