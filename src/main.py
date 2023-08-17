#!/usr/bin/env python

import json
from rx import Receiver
from server import TCPServer
from threading import Thread
import time
import asyncio

if(__name__=='__main__'):
    baudrate:int
    tcpPort:int
    sensorCount:int
    waitTime:int
    accumulation:int
    part_port_pair:dict={}

    
    try:
        #Configuration
        with open('dat/config.json','r') as f:
            config=json.load(f)
            baudrate=config['BaudRate']
            tcpPort=config['TCPPort']
            sensorCount=config['SensorCount']
            waitTime=config['WaitTime']
            accumulation=config['Accumulation']
            serialPort=config['SerialPort']
            parts=serialPort.keys()
            for part in parts:
                port=serialPort[part]
                part_port_pair[part]=port
        
        
        #서버 객체 생성
        server=TCPServer(port=tcpPort,sensorCount=sensorCount)
        list_receiver=[]
        
        async def openReceiver(part):
            print(part,'\t',part_port_pair[part])
            receiver=Receiver(part=part,accumulation=accumulation,baudrate=baudrate,portname=part_port_pair[part],server=server)
            list_receiver.append(receiver)
            receiver.openCalibration()
            receiver.readComm(waitTime=waitTime)
        
        #센서 수신체 리스트 및 센서 수신체 생성        
        parts=part_port_pair.keys()
        for part in parts:
            loop=asyncio.get_event_loop()
            loop.run_until_complete(openReceiver(part))

        
        print('IMU Opened')
        #스켈레톤 렌더러 접속 대기
        #server.accept()
        
        def record(receiver : Receiver):
            receiver.startRecord()
        
        #스켈레톤 렌더러 접속 완료 이후에 데이터 측정 이벤트 등록        
        #for receiver in list_receiver:
        #    thread_record=Thread(target=record(receiver))
        #    thread_record.start()
        
        for receiver in list_receiver:
            receiver.startRecord()
            
        for receiver in list_receiver:
            print('test')
            print(receiver.part,' : ',receiver.imu.device.GetDeviceData('AccX'))
        
        
    except:
        for receiver in list_receiver:
            receiver.closeRecord()
        server.close()