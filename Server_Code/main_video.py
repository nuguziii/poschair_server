import numpy as np
import time
import os
from utils import *

def vidFunc() : #안드로이드로 부터 video 신호 들어오면
	conn = sqlite3.connect("../../POSCHAIR.db")
	conn.row_factory = sqlite3.Row
	c = conn.cursor()

	keyword = generate_keyword_for_video_matching(conn) #기록을 통해 keyword dictionary 생성
	video_list = video_matching(keyword, conn) #안드로이드에 url list 보냄
		

	temp_rows = []
	for videoID in video_list:
		rows = c.execute("SELECT vidID,vidTitle,uploadDate,view,liked FROM Youtube_Video WHERE vidID = ?", (videoID,)).fetchall()
		temp_rows += rows

	#row 내용들 -> rows로 합친 후
	return ([dict(i) for i in temp_rows])


