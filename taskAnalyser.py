from math import floor, ceil
from math import fmod as mod
from numpy import abs
from numpy import int64

from matplotlib import pyplot as plt

from taskGenerator import TaskSet

USE_QPA = True


class RateException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return 'RateException: ' + self.message

class EpsilonException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return 'EpsilonException: ' + self.message

class FailureException(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
    def __str__(self):
        return 'FailureException: ' + self.message

class QPA():
    def __init__(self, taskSet, debug=False):

        # Warning for tasks with offsets
        for task in taskSet.values():
            if task.offset != 0:
                raise Exception("Offsets not supported!")
        
        self.lbRecurrenceLimit = 1E3
        self.taskSet = taskSet

        # Checking if the taskset has arbitrary deadlines
        self.arbitraryDeadlines = False
        for task in taskSet.values():
            if task.deadline > task.period:
                self.arbitraryDeadlines = True
        
        self.debug = debug
    
    def solve(self):

        if self.taskSet.totalUtilization > 1:
            print('Not schedulable')
            return False

        minDeadline = min([task.deadline for task in self.taskSet.values()])
        if self.taskSet.totalUtilization < 1:
            La2, La4, La9 = self.La_2(), self.La_4(), self.La_9()
            if self.debug:
                print('La2 = {:6.3f} | La4 = {:6.3f} | La9 = {:6.3f}'.format(La2, La4, La9))
            La = La4
            Lb = self.Lb()
            lValue = min(La, Lb)
        else:
            Lb = self.Lb()
            lValue = Lb

        if self.debug:
            print('La2 = {:6.3f} | La4 = {:6.3f} | La9 = {:6.3f}'.format(La2, La4, La9))
            print('Lb                           : {:6.3f}'.format(Lb))
            print('min(La, Lb)                  : {:6.3f}'.format(lValue))
        
        deadlines = set()
        for task in self.taskSet.values():
            t = 0
            while (t + task.deadline) < lValue:
                deadlines.add(t + task.deadline)
                t += task.period
        
        if self.debug:
            print('Number of deadlines to check : {}'.format(len(deadlines)))
            print('Min deadline                 : {}'.format(min(deadlines, default=None)))
        t = max(deadlines, default=0)
        h_at_t = self.h(t)

        if self.debug:
            print('t = {:8d} | h(t) = {:8d}'.format(t, h_at_t))

        while (h_at_t <= t) and (h_at_t > minDeadline):
            if h_at_t < t:
                t = h_at_t
            else:
                t = max([d for d in deadlines if d<t])
            h_at_t = self.h(t)
            if self.debug:
                print('t = {:8d} | h(t) = {:8d}'.format(t, h_at_t))

        if h_at_t <= minDeadline:
            print('Schedulable')
            return True
        else:
            print('Not schedulable')
            return False        

    
    def h(self, t):
        value = 0
        for task in self.taskSet.values():
            value += max(0, 1+floor((t - task.deadline)/task.period))*task.wcet
        return value
    
    def La_2(self):
        # Equation (2)
        maxDeadline = max([task.deadline for task in self.taskSet.values()])
        laValue = max(maxDeadline, max([task.period - task.deadline for task in self.taskSet.values()])*self.taskSet.totalUtilization/(1-self.taskSet.totalUtilization))
        return laValue

    def La_3(self):
        # Equation (3)
        # Only for constrained and implicit deadline taskset
        # Check for arbitrary deadlines
        if self.arbitraryDeadlines:
            raise Exception('Can not use La_3 function for arbitrary deadlines')
        laValue = sum([(task.period - task.deadline)*task.utilization for task in self.taskSet.values()])/(1-self.taskSet.totalUtilization)
        return laValue

    def La_4(self):
        # Equation (4)
        maxDeadline = max([task.deadline for task in self.taskSet.values()])
        laValue = max(maxDeadline, sum([(task.period - task.deadline)*task.utilization for task in self.taskSet.values()])/(1-self.taskSet.totalUtilization))
        return laValue
    
    def La_9(self):
        # Equation (9)
        laValue = max([task.deadline-task.period for task in self.taskSet.values()])
        laValue = max(laValue, sum([(task.period - task.deadline)*task.utilization for task in self.taskSet.values()])/(1-self.taskSet.totalUtilization))
        return laValue

    def Lb(self):
        # Equations (5) & (6)
        prevWork = self.calculateWork()
        work = self.calculateWork(prevWork)
        lbRecurrenceCount = 0
        while (prevWork != work) and (lbRecurrenceCount < self.lbRecurrenceLimit):
            prevWork = work
            work = self.calculateWork(prevWork)
            lbRecurrenceCount += 1
        return work
    
    def calculateWork(self, previousWork=None):
        if previousWork is None:
            return sum([task.wcet for task in self.taskSet.values()])
        else:
            return sum([ceil(previousWork/task.period)*task.wcet for task in self.taskSet.values()])


class SchedulabilityTest():
    DEBUG = False
    VERBOSE = False
    def __init__(self, taskSet, thetaN, thetaC, resourcePeriod, config=None):
        SchedulabilityTest.DEBUG = config['DEBUG']
        SchedulabilityTest.VERBOSE = config['VERBOSE']
        self.pi = resourcePeriod
        self.thetaN = thetaN
        self.thetaC = thetaC
        self.wN = thetaN/resourcePeriod
        self.wC = thetaC/resourcePeriod
        self.taskSet = taskSet
        self.epsilon = config['epsilon']


    def solve(self):
        try:
            self.scalingFactor = self._calcDeadlineV(self.epsilon)
            if self.VERBOSE:
                print('Schedulable with deadline scaling factor {}'.format(self.scalingFactor))
        except FailureException as e:
            self.scalingFactor = -1
            if self.VERBOSE:
                print(e)
        except RateException as e:
            self.scalingFactor = -2
            if self.VERBOSE:
                print(e)
        except EpsilonException as e:
            self.scalingFactor = -3
            if self.VERBOSE:
                print(e)
        
        if self.DEBUG:
            try:
                self._plot_cndnX(self._data_cndnA, 'Condition A')
                self._plot_cndnX(self._data_cndnB, 'Condition B')
                self._plot_cndnX(self._data_cndnC, 'Condition C')
                self._plot_cndnX(self._data_cndnD, 'Condition D')
            except AttributeError:
                pass
    
    def _calcL(self, precisionLimit = 1E-6):
        c1 = self.taskSet.totalUtilization_LO_LO
        c2 = self.taskSet.totalUtilization_LO_HI
        c3 = sum(task.r*task.wcetLO/task.period for task in self.taskSet.values() if task.criticality=='LO')
        c4 = self.taskSet.totalUtilization_HI_HI
        
        # if c1 + c2 < self.wN:
        if precisionLimit < abs(self.wN - (c1 + c2)):
            num = 0
            num += c1*max([task.period - task.deadline  for task in self.taskSet.values() if task.criticality == 'LO'], default=0)
            num += c2*max([task.period - task.deadlineV for task in self.taskSet.values() if task.criticality == 'HI'], default=0)
            num += 2*self.wN*(self.pi - self.thetaN)
            den = self.wN - c1 - c2
            self.lA = int(ceil(num/den))
        else:
            if self.VERBOSE:
                print("The condition 'c1 + c2 < wn' is not satisfied!")
            raise FailureException('Failed while calculating l_max for Condition A')
        
        # if c3 + c4 < self.wN:
        if precisionLimit < abs(self.wN - (c3 + c4)):
            num = 0
            num += c3*max([task.period - task.deadline + task.period/task.r for task in self.taskSet.values() if task.criticality == 'LO'], default=0)
            num += c4*max([task.period - (task.deadline - task.deadlineV) for task in self.taskSet.values() if task.criticality == 'HI'], default=0)
            num += 2*self.wN*(self.pi - self.thetaN)
            den = self.wN - c3 - c4
            self.lB = int(ceil(num/den))
        else:
            if self.VERBOSE:
                print("The condition 'c3 + c4 < wn' is not satisfied!")
            raise FailureException('Failed while calculating l_max for Condition B')
        
        # if c2 + c3 < self.wN:
        if precisionLimit < abs(self.wN - (c2 + c3)):
            num = 0
            num += c2*max([task.period - task.deadlineV for task in self.taskSet.values() if task.criticality == 'HI'], default=0)
            num += c3*max([task.period - task.deadline + task.period/task.r for task in self.taskSet.values() if task.criticality == 'LO'], default=0)
            num += 2*self.wC*(self.pi - self.thetaC)
            den = self.wC - c2 - c3
            self.lC = int(ceil(num/den))
        else:
            if self.VERBOSE:
                print("The condition 'c2 + c3 < wc' is not satisfied!")
            raise FailureException('Failed while calculating l_max for Condition C')
        
        # if c3 < self.wC:
        if precisionLimit < abs(self.wC - (c3)):
            num = 0
            num += c3*max([task.period - task.deadline + task.period/task.r for task in self.taskSet.values() if task.criticality == 'LO'], default=0)
            num += 2*self.wC*(self.pi - self.thetaC)
            den = self.wC - c3
            self.lD = int(ceil(num/den))
        else:
            if self.VERBOSE:
                print("The condition 'c3 < wc' is not satisfied!")
            raise FailureException('Failed while calculating l_max for Condition D')
    
    def _calcCndnA(self):
        if self.DEBUG:
            self._data_cndnA = list()

        if USE_QPA:
            return self._QPA(self._dbf_CndA, self._sbf_Rn, self._sbf_Rn_Inv, self.lA)
        else:
            for lValue in range(self.lA):
                lhs = self._dbf_CndA(lValue)
                rhs = self._sbf_Rn(lValue)
                if self.DEBUG:
                    self._data_cndnA.append((lValue, lhs, rhs))
                if lhs > rhs:
                    return False
            return True

    def _calcCndnB(self):
        if self.DEBUG:
            self._data_cndnB = list()

        if USE_QPA:
            return self._QPA(self._dbf_CndB, self._sbf_Rn, self._sbf_Rn_Inv, self.lB)
        else:
            for lValue in range(self.lB):
                lhs = self._dbf_CndB(lValue)
                rhs = self._sbf_Rn(lValue)
                if self.DEBUG:
                    self._data_cndnB.append((lValue, lhs, rhs))
                if lhs > rhs:
                    return False
            return True

    def _calcCndnC(self):
        if self.DEBUG:
            self._data_cndnC = list()

        if USE_QPA:
            return self._QPA(self._dbf_CndC, self._sbf_Rc, self._sbf_Rc_Inv, self.lC)
        else:
            for lValue in range(self.lC):
                lhs = self._dbf_CndC(lValue)
                rhs = self._sbf_Rc(lValue)
                if self.DEBUG:
                    self._data_cndnC.append((lValue, lhs, rhs))
                if lhs > rhs:
                    return False
            return True

    def _calcCndnD(self):
        if self.DEBUG:
            self._data_cndnD = list()

        if USE_QPA:
            return self._QPA(self._dbf_CndD, self._sbf_Rc, self._sbf_Rc_Inv, self.lD)
        else:
            for lValue in range(self.lD):
                lhs = self._dbf_CndD(lValue)
                rhs = self._sbf_Rc(lValue)
                if self.DEBUG:
                    self._data_cndnD.append((lValue, lhs, rhs))
                if lhs > rhs:
                    return False
            return True
    
    def _dbf_LO_SM1(self, task, lValue):
        return max(0, floor((lValue-task.deadline)/(task.period))+1)*task.wcetLO

    def _dbf_HI_SM1(self, task, lValue):
        return max(0, floor((lValue-task.deadlineV)/(task.period))+1)*task.wcetLO

    def _dbf_LO_SM2w(self, task, lValue):
        return max(0, ceil(task.r * (floor((lValue-task.deadline)/(task.period))+1)))*task.wcetLO

    def _dbf_HI_SM2w(self, task, lValue):
        return self._full(task,lValue) - self._done(task,lValue)

    def _dbf_LO_SM2r(self, task, lValue):
        return max(0, ceil(task.r * (floor((lValue-task.deadline)/(task.period))+1)))*task.wcetLO

    def _dbf_HI_SM2r(self, task, lValue):
        return max(0, floor((lValue-task.deadlineV)/(task.period))+1)*task.wcetLO

    def _dbf_HI_SM3(self, task, lValue):
        return self._dbf_HI_SM2w(task, lValue)

    def _full(self, task, lValue):
        return max(0, floor((lValue-(task.deadline - task.deadlineV))/(task.period))+1)*task.wcetHI

    def _done(self, task, lValue):
        n = mod(lValue, task.period)
        if ((task.deadline - task.deadlineV) <= n) and (n <= task.deadline):
            return max(0, task.wcetLO - n + task.deadline - task.deadlineV)
        else:
            return 0
    
    def _dbf_CndA(self, lValue):
        lhs = 0
        lhs += sum(self._dbf_LO_SM1(task, lValue) for task in self.taskSet.values() if task.criticality=='LO')
        lhs += sum(self._dbf_HI_SM1(task, lValue) for task in self.taskSet.values() if task.criticality=='HI')
        return lhs
    
    def _dbf_CndB(self, lValue):
        lhs = 0
        lhs += sum(self._dbf_LO_SM2w(task, lValue) for task in self.taskSet.values() if task.criticality=='LO')
        lhs += sum(self._dbf_HI_SM2w(task, lValue) for task in self.taskSet.values() if task.criticality=='HI')
        return lhs
    
    def _dbf_CndC(self, lValue):
        lhs = 0
        lhs += sum(self._dbf_LO_SM2r(task, lValue) for task in self.taskSet.values() if task.criticality=='LO')
        lhs += sum(self._dbf_HI_SM2r(task, lValue) for task in self.taskSet.values() if task.criticality=='HI')
        return lhs
    
    def _dbf_CndD(self, lValue):
        lhs = sum(self._dbf_HI_SM3(task, lValue) for task in self.taskSet.values() if task.criticality=='HI')
        return lhs
                

    def _sbf_Rn(self, delta):
        epsilon = max(0, delta-2*(self.pi - self.thetaN)-self.pi*floor((delta - (self.pi - self.thetaN))/self.pi))
        if delta <= (2*(self.pi - self.thetaN)):
            return 0
        else:
            return floor((delta - (self.pi - self.thetaN))/self.pi)*self.thetaN + epsilon

    def _sbf_Rc(self, delta):
        epsilon = max(0, delta-2*(self.pi - self.thetaC)-self.pi*floor((delta - (self.pi - self.thetaC))/self.pi))
        if delta <= (2*(self.pi - self.thetaC)):
            return 0
        else:
            return floor((delta - (self.pi - self.thetaC))/self.pi)*self.thetaC + epsilon

    def _sbf_Rn_Inv(self, supply):
        if supply == 0:
            return 2*(self.pi - self.thetaN)
        else:
            if (supply - self.thetaN*floor(supply/self.thetaN)) > 0:
                epsilon = self.pi - self.thetaN + supply - self.thetaN*floor(supply/self.thetaN)
            else:
                epsilon = 0
            return (self.pi - self.thetaN) + self.pi * floor(supply/self.thetaN) + epsilon

    def _sbf_Rc_Inv(self, supply):
        if supply == 0:
            return 2*(self.pi - self.thetaC)
        else:
            if (supply - self.thetaC*floor(supply/self.thetaC)) > 0:
                epsilon = self.pi - self.thetaC + supply - self.thetaC*floor(supply/self.thetaC)
            else:
                epsilon = 0
            return (self.pi - self.thetaC) + self.pi * floor(supply/self.thetaC) + epsilon
    
    def _calcDeadlineV(self, epsilon = 1E-2):
        delta = 0.5
        x = delta
        while delta >= epsilon:
            delta /= 2
            for task in self.taskSet.values():
                if task.criticality == 'HI':
                    task.deadlineV = x*task.deadline
            self._calcL()
            cndnA = self._calcCndnA()
            cndnB = self._calcCndnB()
            cndnC = self._calcCndnC()
            cndnD = self._calcCndnD()

            if cndnA and cndnB and cndnC and cndnD:
                return x
            elif cndnA and cndnB and cndnC and not cndnD:
                x -= delta
            elif cndnA and cndnB and not cndnC and cndnD:
                x += delta
            elif cndnA and cndnB and not cndnC and not cndnD:
                raise FailureException('x not found')
            elif cndnA and not cndnB and cndnC and cndnD:
                x -= delta
            elif cndnA and not cndnB and cndnC and not cndnD:
                x -= delta
            elif cndnA and not cndnB and not cndnC and cndnD:
                raise FailureException('x not found')
            elif cndnA and not cndnB and not cndnC and not cndnD:
                raise FailureException('x not found')
            elif not cndnA and cndnB and cndnC and cndnD:
                x += delta
            elif not cndnA and cndnB and cndnC and not cndnD:
                raise FailureException('x not found')
            elif not cndnA and cndnB and not cndnC and cndnD:
                x += delta
            elif not cndnA and cndnB and not cndnC and not cndnD:
                raise FailureException('x not found')
            elif not cndnA and not cndnB and cndnC and cndnD:
                raise FailureException('x not found')
            elif not cndnA and not cndnB and cndnC and not cndnD:
                raise FailureException('x not found')
            elif not cndnA and not cndnB and not cndnC and cndnD:
                raise FailureException('x not found')
            elif not cndnA and not cndnB and not cndnC and not cndnD:
                raise FailureException('x not found')

            # if cndnA and cndnB and cndnC and cndnD:
            #     return x
            # elif cndnA and cndnC and (not cndnB or not cndnD):
            #     x -= delta
            # elif (not cndnA or not cndnC) and cndnB and cndnD:
            #     x += delta
            # elif cndnA and (not cndnB or not cndnC) and cndnD:
            #     raise RateException('Failed to find x: \{r_i\} values maybe unsuitable.')
            # else:
            #     raise FailureException('x not found')
        else:
            raise EpsilonException('Failed to find x: Try with a smaller epsilon')
    
    def _QPA(self, dbf, sbf, sbfInv, lValue, precisionLimit = 1E-6):
        deadlines = set()
        for task in self.taskSet.values():
            t = 0
            while (t + task.deadline) < lValue:
                deadlines.add(t + task.deadline)
                t += task.period

        minDeadline = min([task.deadline for task in self.taskSet.values()])
        sbf_minDeadline = sbf(minDeadline)
        t = max(deadlines, default=0)
        dbf_t = int64(dbf(t))
        sbf_t = int64(sbf(t))
        # while (precisionLimit <= (sbf_t - dbf_t)) and (dbf_t > sbf_minDeadline):
        while (0 <= (sbf_t - dbf_t)) and (dbf_t > sbf_minDeadline):
            # if precisionLimit < abs(sbf_t - dbf_t):
            if 0 < (sbf_t - dbf_t):
                t = sbfInv(dbf_t)
            else:
                t = max([d for d in deadlines if d<t])
            dbf_t = int64(dbf(t))
            sbf_t = int64(sbf(t))
            if t > 1E10:
                print('Bad!')
        
        if dbf_t <= sbf_minDeadline:
            return True
        else:
            return False
    
    def _plot_cndnX(self, plotData, plotTitle):
        lData = list()
        lhsData = list()
        rhsData = list()
        for value1, value2, value3 in plotData:
            lData.append(value1)
            lhsData.append(value2)
            rhsData.append(value3)
        _, ax = plt.subplots()
        ax.step(lData, lhsData, '.-', where='post')
        ax.step(lData, rhsData, '.-', where='post')
        ax.legend(['lhs', 'rhs'])
        plt.title(plotTitle)
        plt.show()
