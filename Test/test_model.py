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

def test_model(model_name, image):
    #=======================================
    # deep learning model test
    # - input: (180*180*3) image
    # - output: posture label(0-15)
    #=======================================
    model = torch.load("model0225.pth")
    model.eval()
    model = model.cpu()

    x = image.astype('float32')/255
    x = x.reshape(1,x.shape[0],x.shape[1],x.shape[2])
    x_ = torch.from_numpy(x.transpose((0, 3, 1, 2)))
    x_ = x_.cpu()

    y_p = model(x_)
    y_p = y_p.detach().numpy()
    return np.argmax(y_p, axis=1)

if __name__ == '__main__':
    d = data()

    '''아두이노에서 받아온 압력센서 값 (list type)'''
    value = [10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160]

    '''압력센서 값을 image로 변경!! (이 이미지 값 실시간으로 안드로이드 전송)'''
    image = d.generator(value)
    print(image.shape, type(image)) #image type은 numpy array type.
    #imsave('./test.png', np.clip(image/255, -1,1))  #png 이미지로 저장(테스트 용)

    '''딥러닝 모델로 테스트!! (결과 안드로이드 전송 및 DB에 저장)'''
    y = test_model("model0225.pth", image) #model path, image array 입력 => 자세 번호 출력
    print(y) #int
