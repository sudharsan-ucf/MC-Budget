"""
Created on Thu Jun  6 18:45:42 2019

@author: Sudharsan Vaidhun
@email: sudharsan.vaidhun@knights.ucf.edu
"""

import numpy.random as random
from numpy import ceil

class TaskSet(dict):
    def __init__(self) -> None:
        self.numOfTasks = 0
        self.totalUtilization_HI_HI = 0
        self.totalUtilization_HI_LO = 0
        self.totalUtilization_LO_HI = 0
        self.totalUtilization_LO_LO = 0

    def addTask(self, task) -> None:
        self[task.taskIndex] = task
        self.numOfTasks = len(self)
        if task.criticality == 'LO':
            self.totalUtilization_LO_LO += task.utilizationLO
            self.totalUtilization_HI_LO += task.utilizationHI
        elif task.criticality == 'HI':
            self.totalUtilization_LO_HI += task.utilizationLO
            self.totalUtilization_HI_HI += task.utilizationHI
        else:
            raise Exception('Error!')
    
    def listTasks(self) -> None:
        print("| Index | WCET (LO) | WCET (HI) | Period | Deadline | Util. (LO) | Util. (HI) |  X |")
        print("------------------------------------------------------------------------------------")
        for taskIndex, task in self.items():
            print("| {:5d} | {:9.3f} | {:9.3f} | {:6d} | {:8d} | {:10.3f} | {:10.3f} | {:} |".format(
                taskIndex, task.wcetLO, task.wcetHI,
                task.period, task.deadline,
                task.utilizationLO, task.utilizationHI,
                task.criticality))
        print("------------------------------------------------------------------------------------")


class Task():
    counter = 0
    def __init__(self, wcetLO, wcetHI, period, deadline, criticality, rate=1) -> None:
        Task.counter += 1
        self.taskIndex = Task.counter
        self.wcetLO = wcetLO
        self.wcetHI = wcetHI
        self.deadline = deadline
        self.period = period
        self.criticality = criticality
        self.utilizationLO = self.wcetLO / self.period
        self.utilizationHI = self.wcetHI / self.period
        self.r = rate


class TaskGen:
    def genTask(self, method='Uunifast', **kwargs) -> TaskSet:
        if method=='Uunifast':
            try:
                numOfTasks = kwargs['numOfTasks']
                totalUtilization = kwargs['totalUtilization']
                critProb = kwargs['critProb']
                wcetRatio = kwargs['wcetRatio']
                deadlineRatio = kwargs['deadlineRatio']
                rate = kwargs['rate']
            except KeyError:
                print("'Uunifast' method requires numOfTasks, totalUtilization as parameters.")
                exit()
            Task.counter = 0
            return self._genTaskUunifast(numOfTasks, totalUtilization, critProb, wcetRatio, deadlineRatio, rate)
    
    def _genTaskUunifast(self, numOfTasks, totalUtilization, critProb, wcetRatio, deadlineRatio, rate) -> TaskSet:
        taskSet = TaskSet()
        utilList = self._getUtilizationsUunifast(numOfTasks, totalUtilization)
        for util in utilList:
            period = random.randint(100, 1000)
            wcetHI = int(ceil(util*period))
            taskSet.addTask(Task(
                wcetLO = int(ceil(wcetHI/wcetRatio)),
                wcetHI = wcetHI,
                period = period,
                deadline = int(deadlineRatio*period),
                criticality = 'HI' if random.rand()>critProb else 'LO',
                rate=rate
                ))
        return taskSet

    def _getUtilizationsUunifast(self, numOfTasks, totalUtilization) -> list:
        uList = list()
        tempUtil = totalUtilization
        for i in range(numOfTasks-1):
            nextUtil = tempUtil*random.rand()**(1/(numOfTasks-i))
            uList.append(tempUtil - nextUtil)
            tempUtil = nextUtil
        uList.append(tempUtil)
        return uList