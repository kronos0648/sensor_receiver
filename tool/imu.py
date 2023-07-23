import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from Dll.lib.Modular.JY901 import JY901
from Dll.lib.device_model import DeviceModel

class IMU:
    def __init__(self,baudrate,portname):
        self.imu=JY901()
        self.imu.SetBaudrate(baudrate)
        self.imu.SetPortName(portname)
        
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
    
    
    #모듈 재시작
    def restart(self,waitTime):
        self.__IsReadReg(0x03,waitTime)
        self.imu.RestartReg()
        
        
    #모듈 공장초기화
    def factoryReset(self,waitTime):
        self.__IsReadReg(0x03,waitTime)
        self.imu.FactoryResetReg()      