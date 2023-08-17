from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sympy import symbols, solve
import math
from multipledispatch import dispatch

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
        self.accNoise:np.array=np.array([0,0,0]) # 가속도 노이즈 벡터
        
        self.stop_data_count=0
        
    
    def zyx_to_quaternion(self,angle : np.array):
        (roll,pitch,yaw)=(angle[0],angle[1],angle[2]+180)
        w=math.cos(roll/2)*math.cos(pitch/2)*math.cos(yaw/2)+math.sin(roll/2)*math.sin(pitch/2)*math.sin(yaw/2)
        x=math.sin(roll/2)*math.cos(pitch/2)*math.cos(yaw/2)-math.cos(roll/2)*math.sin(pitch/2)*math.sin(yaw/2)
        y=math.cos(roll/2)*math.sin(pitch/2)*math.cos(yaw/2)+math.sin(roll/2)*math.cos(pitch/2)*math.sin(yaw/2)
        z=math.cos(roll/2)*math.cos(pitch/2)*math.sin(yaw/2)-math.sin(roll/2)*math.sin(pitch/2)*math.cos(yaw/2)
        return np.array([x,y,z,w])
        
        
    def deriveLinearAccQ(self,acc:np.array,q : np.array):

        q0 = q[0]
        q1 = q[1]
        q2 = q[2]
        q3 = q[3]
        
        r00 = 2 * (q0 * q0 + q1 * q1) - 1
        r01 = 2 * (q1 * q2 - q0 * q3)
        r02 = 2 * (q1 * q3 + q0 * q2)
        
        r10 = 2 * (q1 * q2 + q0 * q3)
        r11 = 2 * (q0 * q0 + q2 * q2) - 1
        r12 = 2 * (q2 * q3 - q0 * q1)
        
        r20 = 2 * (q1 * q3 - q0 * q2)
        r21 = 2 * (q2 * q3 + q0 * q1)
        r22 = 2 * (q0 * q0 + q3 * q3) - 1
        
        rotation_matrix = np.array([[r00, r01, r02],
                            [r10, r11, r12],
                            [r20, r21, r22]])
        
        gravity=np.array([0,0,1])
        gravity_acceleration=rotation_matrix*gravity.T
        
        gravity_acceleration_vector=np.flipud(gravity_acceleration.T[2])
        print('g : ',gravity_acceleration_vector)
        linearAcc=acc-gravity_acceleration_vector
        return linearAcc
    
    # 선가속도
    def deriveLinearAcc(self,acc : np.array, gyro : np.array, angle : np.array):
        (roll,pitch,yaw)=(angle[0],angle[1],angle[2]+180)
        
        print(roll,'\t',pitch,'\t',yaw)
        
        rm_x=np.array([[1,0,0]
                       ,[0,math.cos(roll),-math.sin(roll)]
                       ,[0,math.sin(roll),math.cos(roll)]])
        rm_y=np.array([[math.cos(pitch),0,-math.sin(pitch)]
                       ,[0,1,0]
                       ,[math.sin(pitch),0,math.cos(pitch)]])
        rm_z=np.array([[math.cos(yaw),-math.sin(yaw),0]
                       ,[math.sin(yaw),math.cos(yaw),0]
                       ,[0,0,1]])
        
        rotation_matrix_zyx=rm_z*rm_y*rm_x
        
        gravity=np.array([1,0,0]) # z,y,x
        gravity_acceleration=rotation_matrix_zyx*gravity.T
        print(gravity_acceleration)
        gravity_acceleration_vector=gravity_acceleration.T[0]
        
        linearAcc=acc-gravity_acceleration_vector
        return linearAcc
    
    
    def stopDataCount(self,data:DerivedData):
        hasMove=False
        for gyro in data.gyro:
            #각속도 발생 => 움직임 있음
            if(abs(gyro)>1):
                hasMove=True
                break
            
        if(not hasMove):
            self.stop_data_count+=1
            print(self.stop_data_count)
            
            

    
    #Non-Accumulation DerivedData 도출 메소드
    @dispatch(RxData)
    def derive(self,rx) -> DerivedData : 
        derivedData=DerivedData()
        derivedData.part=self.part
        derivedData.time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        derivedData.acc=self.deriveLinearAccQ(acc=rx.acc,q=self.zyx_to_quaternion(rx.angle))
        derivedData.gyro=rx.gyro
        derivedData.roll=rx.angle[0]
        derivedData.pitch=rx.angle[1]
        derivedData.yaw=rx.angle[2]
        
        hasMove=False
        for gyro in derivedData.gyro:
            #각속도 발생 => 움직임 있음
            if(abs(gyro)>1):
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
            run=self.time_unit # x 값 변화량
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

    def deriveByGyro(self,rxDataSet) -> DerivedData :
        derivedData=DerivedData()
        derivedData.part=self.part
        derivedData.time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sum_acc=np.array([0,0,0])
        sum_gyro=np.array([0,0,0])
        sum_angle=np.array([0,0,0])
        sum_velocity=np.array([0,0,0])
        for rx in rxDataSet:
            hasMove=False
            for gyro in rx.gyro:
                if(gyro>1):
                    hasMove=True
                    break
                    
            if(not hasMove):
                self.accNoise=self.deriveLinearAccQ(acc=rx.acc,q=self.zyx_to_quaternion(rx.angle))
            #sum_acc=sum_acc+rx.acc
            #sum_acc=sum_acc+self.deriveLinearAcc(acc=rx.acc,gyro=rx.gyro,angle=rx.angle)
            sum_acc=sum_acc+self.deriveLinearAccQ(acc=rx.acc,q=self.zyx_to_quaternion(rx.angle))-self.accNoise
            sum_gyro=sum_gyro+rx.gyro
            sum_angle=sum_angle+rx.angle
            sum_velocity=sum_velocity+sum
            
        derivedData.acc=sum_acc/len(rxDataSet)
        derivedData.gyro=sum_gyro/len(rxDataSet)
        angle=sum_angle/len(rxDataSet)
        derivedData.roll=angle[0]
        derivedData.pitch=angle[1]
        derivedData.yaw=angle[2]
        
        derivedData.gyro
            
            
    #Accumulation DerivedData 도출 메소드
    @dispatch(list)
    def derive(self,rxDataSet) -> DerivedData :
        
        derivedData=DerivedData()
        derivedData.part=self.part
        derivedData.time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        sum_acc=np.array([0,0,0])
        sum_gyro=np.array([0,0,0])
        sum_angle=np.array([0,0,0])
        for rx in rxDataSet:
            hasMove=False
            for gyro in rx.gyro:
                if(gyro>1):
                    hasMove=True
                    break
                    
            if(not hasMove):
                self.accNoise=self.deriveLinearAccQ(acc=rx.acc,q=self.zyx_to_quaternion(rx.angle))
            #sum_acc=sum_acc+rx.acc
            #sum_acc=sum_acc+self.deriveLinearAcc(acc=rx.acc,gyro=rx.gyro,angle=rx.angle)
            sum_acc=sum_acc+self.deriveLinearAccQ(acc=rx.acc,q=self.zyx_to_quaternion(rx.angle))-self.accNoise
            sum_gyro=sum_gyro+rx.gyro
            sum_angle=sum_angle+rx.angle

        derivedData.acc=sum_acc/len(rxDataSet)
        derivedData.gyro=sum_gyro/len(rxDataSet)
        angle=sum_angle/len(rxDataSet)
        derivedData.roll=angle[0]
        derivedData.pitch=angle[1]
        derivedData.yaw=angle[2]
        
        hasMove=False
        for gyro in derivedData.gyro:
            #각속도 발생 => 움직임 있음
            if(abs(gyro)>1):
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
    