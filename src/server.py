from socket import *
from calculator import DerivedData
import json
import asyncio

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