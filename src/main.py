#!/usr/bin/env python

import json
from rx import Receiver
from server import TCPServer

if(__name__=='__main__'):
    baudrate:int
    tcpPort:int
    sensorCount:int
    waitTime:int
    serialPort=None
    port_head:str
    receiver=None
    
    try:
        #Configuration
        with open('dat/config.json','r') as f:
            config=json.load(f)
            baudrate=config['BaudRate']
            tcpPort=config['TCPPort']
            sensorCount=config['SensorCount']
            waitTime=config['WaitTime']
            serialPort=config['SerialPort']
            port_head=serialPort['Head']
            
        #서버 객체 생성
        server=TCPServer(port=tcpPort,sensorCount=sensorCount)
        
        
        #센서 수신체 리스트 및 센서 수신체 생성
        list_receiver=[]
        receiver_head=Receiver(part='Head',baudrate=baudrate,portname=port_head,server=server)
        list_receiver.append(receiver_head)
        
        #일괄 캘리브레이션 및 레지스터 읽기 모드
        for receiver in list_receiver:
            receiver.openCalibration()
            receiver.readComm(waitTime=waitTime)

        #스켈레톤 렌더러 접속 대기
        server.accept()
        
        #스켈레톤 렌더러 접속 완료 이후에 데이터 측정 이벤트 등록        
        for receiver in list_receiver:
            receiver.startRecord()
        
    except:
        for receiver in list_receiver:
            receiver.closeRecord()
        server.close()