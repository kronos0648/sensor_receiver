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
        with open('dat/config.json','r') as f:
            config=json.load(f)
            baudrate=config['BuadRate']
            tcpPort=config['TCPPort']
            sensorCount=config['SensorCount']
            waitTime=config['WaitTime']
            serialPort=config['SerialPort']
            port_head=serialPort['Head']
            
        server=TCPServer(port=tcpPort,sensorCount=sensorCount)
        
        
        list_receiver=[]
        receiver_head=Receiver(part='Head',baudrate=baudrate,portname=port_head,server=server)
        list_receiver.append(receiver)
        
        for receiver in list_receiver:
            receiver.openCalibration()
            receiver.readComm(waitTime=waitTime)

        server.accept()
        
        for receiver in list_receiver:
            receiver.startRecord()
        
    except:
        for receiver in list_receiver:
            receiver.closeRecord()
        server.close()