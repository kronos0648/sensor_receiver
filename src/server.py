from socket import *
from calculator import DerivedData
import json

class TCPServer:
    
    def __init__(self,port,sensorCount):
        self.sensorCount=sensorCount
        self.derivedDataSet=[]
        self.host='127.0.0.1'
        self.port=port
        self.clientSocket=None
        self.serverSocket=socket(AF_INET,SOCK_STREAM)
        self.serverSocket.bind((self.host,self.port))
        
        
        
    def accept(self):
        self.serverSocket.listen(1)
        self.clientSocket,addr=self.serverSocket.accept()
        
        
    def addDerivedData(self,derivedData : DerivedData):
        self.derivedDataSet.append(json.dumps(derivedData))
        if(len(self.derivedDataSet)==self.sensorCount):
            self.__sendData()
        
        
    def __sendData(self):
        message=str(chr(2))
        for data in self.derivedDataSet:
            message+=data
            message+='/'
        message+=str(chr(3))
        self.clientSocket.send(message.encode())
        self.derivedDataSet.clear()
        
        
    def close(self):
        self.clientSocket.close()
        self.serverSocket.close()