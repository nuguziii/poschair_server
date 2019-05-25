import numpy as np
import serial #arduino
import ast  #string to dict
import time
import requests

#setting
port_num = 'COM3'
seri = serial.Serial(port=port_num, baudrate=9600,)
while True:
    if seri.readable():
        res = seri.readline()
        line = res.decode()[:len(res)-2]
        dict = ast.literal_eval(line[:-1])
        v = dict["pressure"]
        values =(v[0],v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9], v[10], v[11], v[12], v[13], v[14], v[15], v[16], v[17])
        values = list(values)
        r = requests.post("http://101.101.163.32", data={'data': str(values)})
