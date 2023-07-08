from dataclasses import dataclass
from datetime import datetime
import numpy as np



@dataclass
class RxData:
    acc:np.array=None
    gyro:np.array=None
    angle:np.array=None
    

@dataclass
class DerivedData:
    part:str=None
    roll:float=None
    pitch:float=None
    yaw:float=None
    velocity:np.array=None
    time:str=None


class Calculator:
    def __init__(self,part,time_unit):
        self.part=part
        self.time_unit=time_unit
        self.timeslice=None
        
        self.lastV:np.array=np.array([0,0,0])
        
        self.lastAcc:np.array=np.array([0,0,0])
        
    def derive(self,rx:RxData) -> DerivedData :
        run=self.time_unit
        derivedData=DerivedData()
        derivedData.part=self.part
        derivedData.time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        derivedData.roll=rx.angle[0]
        derivedData.pitch=rx.angle[1]
        derivedData.yaw=rx.angle[2]
        
        
        #Velocity 적분
        rise=rx.acc-self.lastAcc
        slope=rise/run
        x_intercept=-(self.lastAcc/slope)
        
        length=(rx.acc+self.lastAcc)/2
        area=None
        if(x_intercept>0 and x_intercept < run):
            area=x_intercept*self.lastAcc+x_intercept*rx.acc
            
        area=length*run
        derivedData.velocity=self.lastV+area
        
        return derivedData
    