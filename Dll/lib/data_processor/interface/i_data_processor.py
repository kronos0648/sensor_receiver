# coding:UTF-8
from abc import abstractmethod, ABCMeta


class IDataProcessor(metaclass=ABCMeta):
    """
    数据处理器接口类
    :param metaclass:
    :return:
    """
    

    @abstractmethod
    def onOpen(self, deviceModel):
        pass

    @abstractmethod
    def onClose(self):
        pass

    #@abstractmethod
    #def onUpdate(self,*args):
    #    pass

    @staticmethod
    def onUpdate(*args):
        pass