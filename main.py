import itertools
import json
import sys
import os
import pickle
import datetime
from numpy import random

from taskGenerator import TaskGen
from taskAnalyser import SchedulabilityTest
# from plotter import Logger

defaultConfigFileName = 'sim.cfg'
if len(sys.argv) > 1:
    configFileName = sys.argv[1]
else:
    configFileName = defaultConfigFileName

try:
    with open(configFileName, 'r') as fh:
        config = json.load(fh)
        minThetaRatios = config['minThetaRatios']
        minBudgetUtils = config['minBudgetUtils']
        resourcePeriods = config['resourcePeriods']
        critProbs = config['critProbs']
        minWcetRatios = config['minWcetRatios']
        minRates = config['minRates']
        minDeadlineRatios = config['minDeadlineRatios']
        totalUtilizations = config['totalUtilizations']
        iterations = range(config['numOfIterations'])
        numOfTasks = config['numOfTasks']
except FileNotFoundError:
    config = dict()
    config['DEBUG'] = False
    config['VERBOSE'] = False
    config['epsilon'] = 1E-6
    minThetaRatios = [1.0]
    minBudgetUtils = [1.0]
    resourcePeriods = [100]
    critProbs = [0.5]
    minWcetRatios = [1]
    minRates = [0.1]
    minDeadlineRatios = [0.8]
    totalUtilizations = [0.8]
    iterations = range(25)
    numOfTasks = 2

class Logger(list):
    def __init__(self, logFolderName):
        self.dirPathLog = os.path.join(os.getcwd(), logFolderName)
        if not os.path.isdir(self.dirPathLog):
            os.mkdir(self.dirPathLog)

    def addLog(self, **kwargs):
        self.append(kwargs)
    
    def dumpData(self):
        print('Writing data ...')
        filePathLog = os.path.join(self.dirPathLog, datetime.datetime.strftime(datetime.datetime.now(), 'log_%Y_%m_%d_%H_%M_%S_%f.pkl'))
        with open(filePathLog, 'wb') as fh:
            pickle.dump(self, fh)

log = Logger(config['logFolder'])
try:
    counter = 0
    for totalUtilization, iter, critProb, minWcetRatio, minDeadlineRatio, minThetaRatio, minBudgetUtil, resourcePeriod, minRate in itertools.product(
        totalUtilizations, iterations, critProbs, minWcetRatios, minDeadlineRatios, minThetaRatios, minBudgetUtils, resourcePeriods, minRates):

        # Task Parameters - Fixed Ratios
        wcetRatio = minWcetRatio
        rate = minRate
        deadlineRatio = minDeadlineRatio

        taskSet = TaskGen().genTask('Iterative',
                numOfTasks=numOfTasks,
                totalUtilization=totalUtilization,
                critProb = critProb,
                wcetRatio = wcetRatio,
                deadlineRatio = deadlineRatio,
                rate = rate)
        
        # Supply Parameters - Fixed Ratios
        budgetUtil = minBudgetUtil
        thetaRatio = minThetaRatio
        thetaN = budgetUtil*resourcePeriod
        thetaC = thetaRatio*thetaN

        # thetaN = int(0.5*resourcePeriod)
        # thetaC = thetaN
        
        solver = SchedulabilityTest(taskSet, thetaN, thetaC, resourcePeriod, config)
        solver.solve()
        if solver.scalingFactor == -1:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | Tm = {:4.2f} | Bm = {:4.2f} | Pi = {:5d} | x = ----- <<< Fail!'
        elif solver.scalingFactor == -2:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | Tm = {:4.2f} | Bm = {:4.2f} | Pi = {:5d} | x = ----- <<< Fail! Infeasible rates'
        elif solver.scalingFactor == -3:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | Tm = {:4.2f} | Bm = {:4.2f} | Pi = {:5d} | x = ----- <<< Fail! Decrease epsilon'
        else:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | Tm = {:4.2f} | Bm = {:4.2f} | Pi = {:5d} | x = {:5.3f}'
        
        # print(printFormat.format(totalUtilization, iter, critProb, wcetRatio, minDeadlineRatio, solver.scalingFactor))
        print(printFormat.format(totalUtilization, iter, critProb, wcetRatio, minDeadlineRatio, minThetaRatio, minBudgetUtil, resourcePeriod, solver.scalingFactor))
        log.addLog(
            minThetaRatio=minThetaRatio,
            minBudgetUtil=minBudgetUtil,
            resourcePeriod=resourcePeriod,
            critProb=critProb,
            wcetRatio=wcetRatio,
            rate=rate,
            minDeadlineRatio=minDeadlineRatio,
            totalUtilization=totalUtilization,
            iteration=iter,
            thetaC=thetaC,
            thetaN=thetaN,
            taskSet=None,
            solver=None,
            scalingFactor=solver.scalingFactor
            )
        
        counter += 1
        if counter>=10000:
            counter = 0
            log.dumpData()
            del log
            log = Logger(config['logFolder'])

except Exception as e:
    print('Error', e)
    print('Unknown error, safely quitting ...')

log.dumpData()
