from dataclasses import dataclass
from datetime import datetime
import numpy as np



#센서로부터 수신한 데이터 클래스
@dataclass
class RxData:
    acc:np.array=None
    gyro:np.array=None
    angle:np.array=None
    

#Calculator로 연산해 도출한 데이터 클래스
@dataclass
class DerivedData:
    part:str=None
    roll:float=None
    pitch:float=None
    yaw:float=None
    velocity:np.array=None
    time:str=None


#필요한 데이터를 도출하는 계산기 클래스
class Calculator:
    def __init__(self,part,time_unit):
        self.part=part
        self.time_unit=time_unit
        
        self.lastV:np.array=np.array([0,0,0]) # 3차원 벡터
        
        self.lastAcc:np.array=np.array([0,0,0]) # 3차원 벡터
        
    #DerivedData 도출 메소드
    def derive(self,rx:RxData) -> DerivedData :
        run=self.time_unit # x 값 변화량
        derivedData=DerivedData()
        derivedData.part=self.part
        derivedData.time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        #회전각
        derivedData.roll=rx.angle[0]
        derivedData.pitch=rx.angle[1]
        derivedData.yaw=rx.angle[2]
        
        
        #Velocity 적분
        rise=rx.acc-self.lastAcc # y 값 변화량
        slope=rise/run # 기울기
        x_intercept=-(self.lastAcc/slope) # x절편
        
        length=(rx.acc+self.lastAcc)/2 # 사다리꼴 세로
        area=None
        if(x_intercept>0 and x_intercept < run): # x절편이 범위 내에 존재 => 운동 방향 변화 발생
            area=x_intercept*self.lastAcc+x_intercept*rx.acc
            
        area=length*run
        derivedData.velocity=self.lastV+area
        
        return derivedData
    