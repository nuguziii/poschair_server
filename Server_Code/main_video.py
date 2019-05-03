import numpy as np
import time
import os
from utils import *

if __name__ == '__main__':

    while(True): #안드로이드로 부터 video 신호 들어오면
    	conn = sqlite3.connect("../../POSCHAIR.db")
        keyword = generate_keyword_for_video_matching(conn) #기록을 통해 keyword dictionary 생성
        video_list = video_matching(keyword, conn) #안드로이드에 url list 보냄
        print(video_list)
