import os
import datetime
import pickle
import pandas


dirPathLog = os.path.join(os.getcwd(), 'logs')
if not os.path.isdir(dirPathLog):
    os.mkdir(dirPathLog)

class Logger(list):
    def addLog(self, **kwargs):
        self.append(kwargs)
    
    def dumpData(self):
        print('Writing data ...')
        filePathLog = os.path.join(dirPathLog, datetime.datetime.strftime(datetime.datetime.now(), 'log_%Y_%m_%d_%H_%M_%S_%f.pkl'))
        with open(filePathLog, 'wb') as fh:
            pickle.dump(self, fh)

class Plotter():
    def __init__(self):
        self.logFiles = []
        for fileName in os.listdir(dirPathLog):
            if fileName[-3:] == "pkl":
                self.logFiles.append(fileName)
        columnNames = ['Theta Ratio', 'Supply Budget Ratio', 'Resource Period', 'Crit Prob', 'Wcet Ratio', 'Rate', 'Deadline Ratio', 'Total Utilization', 'Iteration', 'ThetaC', 'ThetaN', 'Scaling Factor']
        self.database = pandas.DataFrame(columns=columnNames)

        for selectedFile in self.logFiles:
            with open(os.path.join(dirPathLog, selectedFile), 'rb') as fh:
                self.simData = pickle.load(fh)
            formattedSimData = []
            for unitData in self.simData:
                formattedSimData.append([
                    unitData['minThetaRatio'],
                    unitData['minBudgetUtil'],
                    unitData['resourcePeriod'],
                    unitData['critProb'],
                    unitData['wcetRatio'],
                    unitData['rate'],
                    unitData['minDeadlineRatio'],
                    unitData['totalUtilization'],
                    unitData['iteration'],
                    unitData['thetaC'],
                    unitData['thetaN'],
                    unitData['scalingFactor']
                ])
            self.database = pandas.concat(
                objs = [self.database, pandas.DataFrame(data = formattedSimData, columns=columnNames)],
                ignore_index = True)
            del self.simData
            del formattedSimData
