"""
Created on Thu Jun  6 18:45:42 2019

@author: Sudharsan Vaidhun
@email: sudharsan.vaidhun@knights.ucf.edu
"""

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
        print("| Index | WCET (LO) | WCET (HI) | Period | Deadline | Util. (LO) | Util. (HI) |")
        print("-------------------------------------------------------------------------------")
        for taskIndex, task in self.items():
            print("| {:5d} | {:9d} | {:9d} | {:6d} | {:8d} | {:10.3f} | {:10.3f} |".format(taskIndex, task.wcetLO, task.wcetHI, task.period, task.deadline, task.utilizationLO, task.utilizationHI))
        print("-------------------------------------------------------------------------------")


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
    def __init__(self) -> None:
        pass

    def genTask(self, method='Uunifast') -> TaskSet:
        if method=='Uunifast':
            return self._genTaskUunifast()
    
    def _genTaskUunifast(self) -> TaskSet:
        taskSet = TaskSet()
        taskSet.addTask(Task())
        return taskSet