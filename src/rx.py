import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import numpy as np

from Dll.lib.Modular.JY901 import JY901
from Dll.lib.device_model import DeviceModel
from calculator import RxData,Calculator
from server import TCPServer


class Receiver:
    
    def __init__(self,part:str,baudrate,portname,server:TCPServer):
        self.part=part
        self.imu=JY901()
        self.imu.SetBaudrate(baudrate)
        self.imu.SetPortName(portname)
        self.calc : Calculator = None
        self.server:TCPServer=server
        
        
    def openCalibration(self):
        self.imu.Open()
        if(self.imu.IsOpen()):
            self.imu.UnlockReg()
            self.imu.AppliedCalibration()
            return True
        else: return False
    
    
    def __IsReadReg(self,reg,waitTime):
        bRet=False
        if(self.imu.IsOpen()):
            if(self.imu.SendReadReg(reg,waitTime)):
                bRet=True
        return bRet
    
    
    def readComm(self,waitTime):
        self.__IsReadReg(0x03,waitTime)
        self.imu.SendWriteReg(0x03,0x06)
        self.imu.SaveReg()
        self.calc=Calculator(waitTime)
        
    

    def __onRecord(self,deviceModel : DeviceModel):
        
        for data in self.server.derivedDataSet:
            if(self.part==data.part): return
            
        rx=RxData()
        rx.acc=np.array([deviceModel.GetDeviceData('AccX'), deviceModel.GetDeviceData('AccY'), deviceModel.GetDeviceData('AccZ')])
        rx.gyro=np.array([deviceModel.GetDeviceData('GyroX'), deviceModel.GetDeviceData('GyroY'), deviceModel.GetDeviceData('GyroZ')])
        rx.angle=np.array([deviceModel.GetDeviceData('AngleX'), deviceModel.GetDeviceData('AngleY'), deviceModel.GetDeviceData('AngleZ')])
        derivedData=self.calc.derive(rx)
        self.server.addDerivedData(derivedData=derivedData)
        
        
        
    
    def startRecord(self):
        self.imu.AddOnRecord(self.__onRecord)
        
    def closeRecord(self):
        self.imu.Close()
        self.imu.RemoveOnRecord(self.__onRecord)
    
    
        
    