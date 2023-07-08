import time
import datetime
import platform
import struct
import threading
import Dll.lib.device_model as deviceModel
from Dll.lib.protocol_resolver.roles.protocol_485_resolver import Protocol485Resolver
from Dll.lib.data_processor.roles.jy901s_dataProcessor import JY901SDataProcessor
from Dll.lib.Modular.interface.i_operating_equipment import IOperatingEquipment
"""
WT901C485设备
"""


class WT901C485(IOperatingEquipment):
    # 设备
    device = None
    # 是否停止读取
    IsPauseRead = False
    # 读取间隔时间（毫秒）
    """
    读取间隔时间（毫秒）
    """
    iReadInterval = 200

    def __init__(self):
        """
        初始化一个设备模型
        :param self:
        :return:
        """
        self.device = deviceModel.DeviceModel(
            "我的WT901C485",
            Protocol485Resolver(),
            JY901SDataProcessor(),
            "51_0"
        )

    @property
    def ADDR(self):
        """
        获取设备地址
        :return:
        """
        return self.device.ADDR

    @ADDR.setter
    def ADDR(self, value):
        """
        设置设备地址
        :param value: 设备地址
        :return:
        """
        self.device.ADDR = value

    def GetDeviceName(self):
        """
        获得设备名称
        :return:
        """
        return self.device.deviceName

    def SetPortName(self, portName):
        """
        设置串口号
        :param self:
        :param portName:
        :return:
        """
        self.device.serialConfig.portName = portName

    def SetBaudrate(self, baudrate):
        """
        设置波特率
        :param self:
        :param baudrate:
        :return:
        """
        self.device.serialConfig.baud = baudrate

    def Open(self):
        """
        打开设备
        :param self:
        :return:
        """
        self.device.openDevice()
        if self .device.isOpen:
            self.IsPauseRead = False
            t = threading.Thread(target=self.LoopReadThead, args=(self.device,))  # 开启一个线程读取数据
            t.start()

    def LoopReadThead(self, device):
        """
        循环读取数据
        :param device:
        :return:
        """
        iSleep = 1
        # 循环读取数据
        while self.device.isOpen:
            if self.IsPauseRead:
                iSleep = 1
            else:
                iSleep = self.iReadInterval / 1000
                self.device.readReg(self.device.StartReadReg, self.device.ReadRegCount, 0)  # 读取 数据
            time.sleep(iSleep)  # 休眠

    def AddOnRecord(self, eventOnRecord):
        """
        添加事件
        :param eventOnRecord: 接收数据事件
        :return:
        """
        self.device.dataProcessor.onVarChanged.append(eventOnRecord)  # 数据更新事件

    def RemoveOnRecord(self, eventOnRecord):
        """
        移除事件
        :param eventOnRecord: 接收数据事件
        :return:
        """
        self.device.dataProcessor.onVarChanged.remove(eventOnRecord)  # 数据更新事件

    def IsOpen(self):
        """
        串口是否打开
        :return:
        """
        return self.device.isOpen

    def UnlockReg(self):
        """
        解锁寄存器
        :return:
        """
        self.device.unlock()

    def AppliedCalibration(self):
        """
        加计校准
        :return:
        """
        self.device.AppliedCalibration()

    def StartFieldCalibration(self):
        """
        开始磁场校准
        :return:
        """
        self.device.BeginFiledCalibration()

    def EndFieldCalibration(self):
        """
        结束磁场校准
        :return:
        """
        self.device.EndFiledCalibration()

    def SetModbusId(self, modbusId):
        """
        设置传感器地址
        :param modbusId:传感器地址
        :return:
        """
        self.SendWriteReg(0x1a, modbusId)

    def SendReadReg(self, reg, waitTime):
        """
        发送读取寄存器的命令
        :param reg: 寄存器地址
        :param waitTime: 等待时间（毫秒）
        :return:
        """
        self.IsPauseRead = True
        bol = self.device.readReg(reg, 1, waitTime)
        self.IsPauseRead = False
        return bol

    def SendWriteReg(self, reg, data):
        """
        发送读取寄存器的命令
        :param reg: 寄存器地址
        :param data: 寄存器对应的值
        :return:
        """
        self.IsPauseRead = True
        bol = self.device.writeReg(reg, data)
        self.IsPauseRead = False
        return bol

    def SendProtocolData(self, data, waitTime):
        """
        发送带协议的数据
        :param data:
        :param waitTime: 等待时间（毫秒）
        :return:
        """
        self.IsPauseRead = True
        self.device.sendData(data)
        time.sleep(waitTime/1000.0)  # 休眠
        self.IsPauseRead = False

    def decToHex(self, num):
        """
        10进制转16进制
        :param num:
        :return:
        """
        return self.device.decToHex(num)

    def SaveReg(self):
        """
        保存寄存器
        :return:
        """
        self.IsPauseRead = True
        self.device.save()
        time.sleep(0.1)  # 休眠
        self.IsPauseRead = False

    def SetReturnRate(self, rate):
        """
        设置回传速率
        :param rate:回传速率
        :return:
        """
        self.device.writeReg(0x03, rate)

    def Close(self):
        """
        关闭设备
        :param self:
        :return:
        """
        self.device.closeDevice()

    def GetDeviceData(self, key):
        """
        获得Key值数据
        :param key:数据键值
        :return:
        """
        tempKey = str(key).upper()
        if str(key).upper().startswith("0X"):
            tempKey = str(key)[2:]

        return self.device.GetDeviceData(tempKey)