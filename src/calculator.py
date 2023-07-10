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
        self.time_unit=time_unit/1000
        
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
        
        list_area=[]
        for i in range(0,3):
            if(x_intercept[i]>0 and x_intercept[i] < run): # x절편이 범위 내에 존재 => 운동 방향 변화 발생
                #수식 : (x절편 * 직전 가속도 + (x값 변화량 - x절편) * 현재 가속도) / 2
                element_area=(x_intercept[i] * self.lastAcc[i] + (run - x_intercept[i]) * rx.acc[i]) / 2
                list_area.append(element_area)
            else:  # x절편이 범위 외에 존재 => 운동 방향 변화 X
                element_area=length[i]*run
                list_area.append(element_area)
        
        area=np.array(list_area)
        derivedData.velocity=self.lastV+area
        
        return derivedData
    