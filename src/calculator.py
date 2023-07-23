from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sympy import symbols, solve
import math

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
    acc:np.array=None
    gyro:np.array=None
    velocity:np.array=None
    displacement:np.array=None
    time:str=None

#필요한 데이터를 도출하는 계산기 클래스
class Calculator:
    def __init__(self,part,time_unit):
        self.part=part
        self.time_unit=time_unit/1000
        self.lastV:np.array=np.array([0,0,0]) # 3차원 속도 벡터
        self.lastD:np.array=np.array([0,0,0]) # 3차원 변위 벡터
        self.lastAcc:np.array=np.array([0,0,0]) # 3차원 가속도 벡터
        
        
    
    # 선가속도
    def deriveLinearAcc(self,acc : np.array, angle : np.array):
        (roll,pitch,yaw)=(angle[0],angle[1],angle[2])
        rotation_matrix_zyx=np.array([[math.cos(pitch)*math.cos(yaw), -math.cos(roll)*math.sin(yaw) + math.cos(yaw)*math.sin(roll)*math.sin(pitch), math.cos(roll)*math.cos(yaw)*math.sin(pitch) + math.sin(roll)*math.sin(yaw)]
                             ,[math.cos(pitch)*math.sin(yaw), math.cos(roll)*math.cos(yaw) + math.sin(roll)*math.sin(pitch)*math.sin(yaw),math.cos(roll)*math.sin(pitch)*math.sin(yaw) - math.cos(yaw)*math.sin(roll)]
                             ,[-math.sin(pitch), math.cos(pitch)*math.sin(roll), math.cos(roll)*math.cos(pitch)]])
        
        
        gravity=np.array([1,0,0]) # z,y,x
        gravity_acceleration=rotation_matrix_zyx*gravity.T
        gravity_acceleration_vector=gravity_acceleration.T[0]
        linearAcc=acc-gravity_acceleration_vector
        return linearAcc
    
    
        
    #DerivedData 도출 메소드
    def derive(self,rxDataSet:list[RxData]) -> DerivedData :
        derivedData=DerivedData()
        derivedData.part=self.part
        derivedData.time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sum_acc=np.array([0,0,0])
        sum_gyro=np.array([0,0,0])
        sum_angle=np.array([0,0,0])
        for rx in rxDataSet:
            sum_acc=sum_acc+self.deriveLinearAcc(acc=rx.acc,angle=rx.angle)
            sum_gyro=sum_gyro+rx.gyro
            sum_angle=sum_angle+rx.angle

        derivedData.acc=sum_acc/len(rxDataSet)
        derivedData.gyro=sum_gyro/len(rxDataSet)
        angle=sum_angle/len(rxDataSet)
        derivedData.roll=angle[0]
        derivedData.pitch=angle[1]
        derivedData.yaw=angle[2]
        
        hasMove=False
        for gyro in rx.gyro:
            #각속도 발생 => 움직임 있음
            if(abs(gyro)>5):
                hasMove=True
                break
        
        #각속도 발생 X => 속도 = 0
        if(not hasMove):
            derivedData.velocity=np.array([0,0,0])
            derivedData.displacement=self.lastD
            self.lastAcc=derivedData.acc
            self.lastV=derivedData.velocity
            
        #각속도 발생
        else:
            run=self.time_unit*len(rxDataSet) # x 값 변화량
            #Velocity 적분
            rise=derivedData.acc-self.lastAcc # y 값 변화량
            slope=rise/run # 기울기
            length=(derivedData.acc+self.lastAcc)/2 # 사다리꼴 세로
            x_intercept = np.array([0,0,0])
            for i in range(0,3):
                if(slope[i]==0): continue
                x_intercept[i]=-(self.lastAcc[i]/slope[i]) # x절편
            area=None
            
            list_area=[]
            for i in range(0,3):
                if(slope[i]==0):
                    element_area=length[i]*run
                    list_area.append(element_area)
                    
                elif(x_intercept[i]>0 and x_intercept[i] < run): # x절편이 범위 내에 존재 => 운동 방향 변화 발생
                    #수식 : (x절편 * 직전 가속도 + (x값 변화량 - x절편) * 현재 가속도) / 2
                    element_area=(x_intercept[i] * self.lastAcc[i] + (run - x_intercept[i]) * derivedData.acc[i]) / 2
                    list_area.append(element_area)
                    
                else:  # x절편이 범위 외에 존재 => 운동 방향 변화 X
                    element_area=length[i]*run
                    list_area.append(element_area)
            
            area=np.array(list_area)
            derivedData.velocity=self.lastV+area
            derivedData.displacement=self.lastD+derivedData.velocity*run
            self.lastAcc=derivedData.acc
            self.lastV=derivedData.velocity
            self.lastD=derivedData.displacement
        return derivedData
    