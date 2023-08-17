from socket import *
from calculator import DerivedData
import json
import asyncio
import csv
import sys

#스켈레톤 렌더러와 통신할 TCP Server 클래스
class TCPServer:
    
    def __init__(self,port,sensorCount):
        self.sensorCount=sensorCount
        self.derivedDataSet=[]
        self.host=''
        self.port=port
        self.clientSocket=None
        self.serverSocket=socket(AF_INET,SOCK_STREAM)
        self.serverSocket.bind((self.host,self.port))
        self.totalRawData=[]
        self.file=open('dat/'+sys.argv[1]+'.csv','a')
        self.wr=csv.writer(self.file)
        
        
        
    #클라이언트(스켈레톤 렌더러) 접속 대기 메소드
    def accept(self):
        self.serverSocket.listen(1)
        self.clientSocket,addr=self.serverSocket.accept()
        
        
    #도출 데이터 JSON 변환 메소드
    def data_to_json(self,derivedData : DerivedData):
        derivedData.acc=derivedData.acc.tolist()
        derivedData.gyro=derivedData.gyro.tolist()
        derivedData.velocity=derivedData.velocity.tolist()
        derivedData.displacement=derivedData.displacement.tolist()
        dict_derivedData=derivedData.__dict__
        return json.dumps(dict_derivedData)
        
    def addRawData(self,data : DerivedData):
        self.totalRawData.append(data)
        if(self.sensorCount==len(self.totalRawData)):
            self.writeRawData()
            self.totalRawData.clear()
             
        
    def writeRawData(self):
        armData:DerivedData
        legData:DerivedData
        for dat in self.totalRawData:
            if(dat.part=='arm'):
                armData=dat
            elif(dat.part=='leg'):
                legData=dat
                
        self.wr.writerow([armData.time,
                          armData.acc[0],armData.acc[1],armData.acc[2],
                          armData.gyro[0],armData.gyro[1],armData.gyro[2],
                          armData.roll,armData.pitch,armData.yaw,
                          legData.acc[0],legData.acc[1],legData.acc[2],
                          legData.gyro[0],legData.gyro[1],legData.gyro[2],
                          legData.roll,legData.pitch,legData.yaw
                          ])
                
        
        
    #도출 데이터셋 전송 메소드
    def sendData(self,derivedData : DerivedData):
        message=str(chr(2)) # STX
        message+=self.data_to_json(derivedData)
        message+=str(chr(3)) # ETX
        try:
            self.clientSocket.send(message.encode())
            
        except: #소켓 연결 해제 시 재연결 대기
            self.clientSocket.close()
            self.accept()
        
    #소켓 닫기 메소드
    def close(self):
        self.clientSocket.close()
        self.serverSocket.close()