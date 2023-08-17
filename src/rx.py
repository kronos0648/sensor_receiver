import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import numpy as np
import threading
import csv
from datetime import datetime


from Dll.lib.Modular.JY901 import JY901
from Dll.lib.device_model import DeviceModel
from calculator import RxData,Calculator,DerivedData
from server import TCPServer

#센서 수신체 클래스
class Receiver:
    
    def __init__(self,part:str,accumulation,baudrate,portname,server:TCPServer):
        self.part=part
        self.imu=JY901()
        self.accumulation=accumulation
        self.imu.SetBaudrate(baudrate)
        self.imu.SetPortName(portname)
        self.calc : Calculator = None
        self.rxDataSet : list[RxData] = []
        self.server:TCPServer=server
        self.file=open('dat/stopdata.csv','a')
        self.wr=csv.writer(self.file)
        
    #캘리브레이션 메소드
    def openCalibration(self):
        self.imu.Open()
        if(self.imu.IsOpen()):
            self.imu.UnlockReg()
            self.imu.AppliedCalibration()
            return True
        else: return False
    
    #레지스터를 현재 읽고 있는 상태인지 체크 메소드
    def __IsReadReg(self,reg,waitTime):
        bRet=False
        if(self.imu.IsOpen()):
            if(self.imu.SendReadReg(reg,waitTime)):
                bRet=True
        return bRet
    
    #레지스터 읽기 모드 진입 메소드
    def readComm(self,waitTime):
        self.__IsReadReg(0x03,waitTime)
        self.imu.SendWriteReg(0x03,0x06)
        #self.imu.SendWriteReg(0x2A,0x01)
        
        self.imu.SaveReg()
        self.calc=Calculator(part=self.part,time_unit=waitTime)
        
        
    #데이터 측정 이벤트 메소드
    def __onRecord(self,deviceModel : DeviceModel):

        rx=RxData()
        # 3차원 벡터로 저장
        rx.acc=np.array([deviceModel.GetDeviceData('AccX'), deviceModel.GetDeviceData('AccY'), deviceModel.GetDeviceData('AccZ')])
        rx.gyro=np.array([deviceModel.GetDeviceData('GyroX'), deviceModel.GetDeviceData('GyroY'), deviceModel.GetDeviceData('GyroZ')])
        rx.angle=np.array([deviceModel.GetDeviceData('AngleX'), deviceModel.GetDeviceData('AngleY'), deviceModel.GetDeviceData('AngleZ')])
        if(np.array_equal(self.calc.accNoise,np.array([0,0,0]))):
            self.calc.accNoise=self.calc.deriveLinearAccQ(acc=rx.acc,q=self.calc.zyx_to_quaternion(rx.angle))
        #self.sendStopData(rx)
        #self.unitize(rx)
        #self.accumulate(rx)
        hasPart=False
        for dat in self.server.totalRawData:
            if(dat.part==self.part):
                hasPart=True
                break
            
        if hasPart:
            return
        
        self.sendRawData(rx)

        

    def unitize(self,rx : RxData):
        derivedData=self.calc.derive(rx)
        self.calc.stopDataCount(derivedData)
        threading.Thread(target=self.server.sendData(derivedData)).start()
    
    
    def accumulate(self,rx : RxData):
        self.rxDataSet.append(rx)
        hasMove=False
        for gyro in rx.gyro:
            if(gyro>1):
                hasMove=True
                break
                
        if(not hasMove):
            self.calc.accNoise=self.calc.deriveLinearAccQ(acc=rx.acc,q=self.calc.zyx_to_quaternion(rx.angle))
        if(len(self.rxDataSet)==self.accumulation): 
            derivedData=self.calc.derive(self.rxDataSet)
            self.rxDataSet.clear()
            threading.Thread(target=self.server.sendData(derivedData)).start()        
            
    def sendStopData(self,rx:RxData):
        print(rx.gyro)
        derivedData=self.calc.derive(rx)
        self.calc.stopDataCount(derivedData)
        hasMove=False
        for gyro in derivedData.gyro:
            if(gyro>1):
                hasMove=True
                break
                
        if(not hasMove):
            self.wr.writerow([derivedData.roll,derivedData.pitch,derivedData.yaw,derivedData.acc[0],derivedData.acc[1],derivedData.acc[2]])
        
        if(self.calc.stop_data_count%100==0):
            threading.Thread(target=self.server.sendData(derivedData)).start()   
        
    def sendRawData(self,rx : RxData):
        data=DerivedData()
        data.time=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')
        data.part=self.part
        data.acc=rx.acc
        data.gyro=rx.gyro
        data.roll=rx.angle[0]
        data.pitch=rx.angle[1]
        data.yaw=rx.angle[2]
        self.server.addRawData(data)
    
    
    #데이터 측정 이벤트 핸들러 등록 메소드
    def startRecord(self):
        self.imu.AddOnRecord(self.__onRecord)
        
    #데이터 측정 이벤트 핸들러 제거 메소드
    def closeRecord(self):
        self.imu.Close()
        self.imu.RemoveOnRecord(self.__onRecord)
    
    
        
    