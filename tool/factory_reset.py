import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from imu import IMU

import json

if(__name__=='__main__'):
    baudrate:int
    tcpPort:int
    sensorCount:int
    waitTime:int
    serialPort=None
    port_head:str
    receiver=None
    
    with open('dat/config.json','r') as f:
        config=json.load(f)
        baudrate=config['BaudRate']
        tcpPort=config['TCPPort']
        sensorCount=config['SensorCount']
        waitTime=config['WaitTime']
        serialPort=config['SerialPort']
        port_head=serialPort['Head']
    
    list_receiver=[]
    receiver_head=IMU(baudrate=baudrate,portname=port_head)
    list_receiver.append(receiver_head)
    
    #일괄 캘리브레이션 및 레지스터 읽기 모드
    for receiver in list_receiver:
        receiver.openCalibration()
        receiver.factoryReset(waitTime)
        
        
    print("Factory Reset All IMU")