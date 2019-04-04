import numpy as np
import time
import os
from utils import *

if __name__ == '__main__':

    while(True): #안드로이드로 부터 video 신호 들어오면
        keyword = generate_keyword_for_video_matching() #기록을 통해 keyword dictionary 생성
        video_matching(keyword) #안드로이드에 url list 보냄
