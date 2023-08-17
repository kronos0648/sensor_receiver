# coding:UTF-8
from Dll.lib.data_processor.interface.i_data_processor import IDataProcessor
import asyncio
import threading

"""
    JY901S数据处理器
"""


class JY901SDataProcessor(IDataProcessor):

    onVarChanged=[]
    models=[]
    
    

    #def __init__(self):
    #    self.onVarChanged = []
    
    
    def onOpen(self, deviceModel):
        pass

    def onClose(self):
        pass

    #def onUpdate(self,*args):
    #    if(len(self.onVarChanged)==0):
    #        return
    #    asyncio.run(self.onVarChanged[0](*args))
            
    #def onUpdate(self,*args):
    #    for fun in self.onVarChanged:
    #        fun(*args) 
            
    @staticmethod
    def onUpdate(*args):
        #print('onVarChanged',JY901SDataProcessor.onVarChanged)
        #print('*args',*args)
        
        for fun in JY901SDataProcessor.onVarChanged:
            asyncio.run(fun(*args))
            
            
        #for i in range(len(JY901SDataProcessor.onVarChanged)):
        #    threading.Thread(target=asyncio.run(JY901SDataProcessor.onVarChanged[i](JY901SDataProcessor.models[i]))).start()
            