from socket import *
from calculator import DerivedData
import json

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
        
        
    #도출 데이터 저장 메소드
    def addDerivedData(self,derivedData : DerivedData):
        dict_derivedData=derivedData.__dict__
        dict_derivedData['velocity']=dict_derivedData['velocity'].tolist()
        self.derivedDataSet.append(json.dumps(dict_derivedData))
        
        #모든 센서의 도출 데이터 축적 시 스켈레톤 렌더러로 데이터셋 전송
        if(len(self.derivedDataSet)==self.sensorCount):
            self.__sendData()
        
        
    #도출 데이터셋 전송 메소드
    def __sendData(self):
        message=str(chr(2)) # STX
        for data in self.derivedDataSet:
            message+=data
            message+='/' #Delimeter

        message+=str(chr(3)) # ETX
        try:
            self.clientSocket.send(message.encode())
            self.clientSocket.recv(1024).decode()
            
        except: #소켓 연결 해제 시 재연결 대기
            self.clientSocket.close()
            self.accept()
        self.derivedDataSet.clear()
        
    #소켓 닫기 메소드
    def close(self):
        self.clientSocket.close()
        self.serverSocket.close()