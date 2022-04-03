import os
import datetime
import pickle


dirPathLog = os.path.join(os.getcwd(), 'logs')
if not os.path.isdir(dirPathLog):
    os.mkdir(dirPathLog)

class Logger(list):
    def addLog(self, **kwargs):
        self.append(kwargs)
    
    def dumpData(self):
        filePathLog = os.path.join(dirPathLog, datetime.datetime.strftime(datetime.datetime.now(), 'log_%Y_%m_%d_%H_%M_%S_%f.pkl'))
        with open(filePathLog, 'wb') as fh:
            pickle.dump(self, fh)
        self.__init__()