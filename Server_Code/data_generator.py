# -*- coding: utf-8 -*-

# =============================================================================
# data generation code
# posture pressure sensor values (16,) -> rgb image (w,h,3)
#
# by Chae Eun Lee (02/2019)
# nuguziii@naver.com
# https://github.com/nuguziii
# =============================================================================

# no need to run this code separately!!

import glob
import cv2
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
#import serial #arduino
import ast  #sring to dict
from scipy.interpolate import interp1d
import random
import scipy.interpolate as interpolate
from skimage.io import imread, imsave, imshow
import os

class data:
    def __init__(self):
        self.v = None
        self.w = None
        self.h = None

    def generator(self, values, w=90, h=90):
        #=======================================
        # posture sensor value to image
        # - input: sensor values list type
        # - output: (180*180*3) numpy array
        #=======================================
        self.w = w
        self.h = h
        return self._interpolation(np.asarray(values))

    def _p(self, v1, v2=None, v3=None, v4=None):
        if v2 is None:
            return self.v[v1]
        elif v3 is None:
            return int((self.v[v1]+self.v[v2])/2)
        elif v4 is None:
            return int((self.v[v1]+self.v[v2]+self.v[v3])/3)
        else:
            return int((self.v[v1]+self.v[v2]+self.v[v3]+self.v[v4])/4)

    def _value_to_color(self, values):
        #=======================================
        # sensor value to color image mapping
        #=======================================
        map_r = interp1d([0,125,250,375,500,755,880,1000], [0,125,0,0,0,255,255,255])
        map_g = interp1d([0,125,250,375,500,755,880,1000], [0,0,0,125,255,255,125,5])
        map_b = interp1d([0,125,250,375,500,755,880,1000], [0,255,255,125,0,0,0,0])

        image = np.zeros((self.w,self.h,3))

        image[:,:,0] = map_r(values)
        image[:,:,1] = map_g(values)
        image[:,:,2] = map_b(values)

        return image

    def _interpolation(self, v):
        #=======================================
        # (5*8) to (180*180*3) interpolation
        #=======================================
        self.v = v
        values = np.array([[0,self._p(1,2),self._p(2),self._p(2,3),0],[self._p(0,1),self._p(1),self._p(1,2,3,5),self._p(3),self._p(3,4)],\
                            [self._p(0),self._p(0,1,5,6),self._p(5),self._p(3,5,4,7),self._p(4)], [self._p(0,6,8),self._p(6),self._p(5,6,7),self._p(7),self._p(4,7,11)], \
                            [self._p(8),self._p(6,8,9),0,self._p(7,10,11),self._p(11)],[self._p(8,9,12),self._p(9),0,self._p(10),self._p(10,11,15)],\
                            [self._p(12),self._p(9,12,13),0,self._p(10,14,15),self._p(15)],[self._p(12,13),self._p(13),0,self._p(14),self._p(14,15)]])

        mymin, mymax = 0,1
        X = np.linspace(mymin, mymax,5)
        Y = np.linspace(mymin, mymax,8)
        x, y = np.meshgrid(X,Y)
        f = interpolate.interp2d(x, y, values, kind='cubic')

        xnew = np.linspace(mymin, mymax,self.w)
        ynew = np.linspace(mymin, mymax,self.h)

        values = f(xnew,ynew)
        values = np.clip(values,0,1000)

        image = self._value_to_color(values)

        return image

    def save_image(self, v, path):
        imsave(path, np.clip(v/255, -1,1))


if __name__ == '__main__':
    d = data()
    x = d.generator([10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160])
