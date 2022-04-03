import itertools
import json

from numpy import random

from taskGenerator import TaskGen
from taskAnalyser import SchedulabilityTest
from plotter import Logger

try:
    with open('sim.cfg', 'r') as fh:
        config = json.load(fh)
        numOfTasks = config['numOfTasks']
        iterations = range(config['numOfIterations'])
        critProbs = config['critProbs']
        wcetRatios = config['wcetRatios']
        minDeadlineRatios = config['minDeadlineRatios']
        totalUtilizations = config['totalUtilizations']
        minThetaRatios = config['minThetaRatios']
        minBudgetUtils = config['minBudgetUtils']
        resourcePeriods = config['resourcePeriods']
except FileNotFoundError:
    config = None
    numOfTasks = 10
    iterations = range(10)
    critProbs = [0.5]
    wcetRatios = [2,3]
    minDeadlineRatios = [0.7, 0.8]
    totalUtilizations = [0.1, 0.3, 0.5, 0.7]
    minThetaRatios = [1.0]
    minBudgetUtils = [1.0]
    resourcePeriods = [100]


log = Logger()
try:
    counter = 0
    for totalUtilization, iter, critProb, wcetRatio, minDeadlineRatio, minThetaRatio, minBudgetUtil, resourcePeriod in itertools.product(
        totalUtilizations, iterations, critProbs, wcetRatios, minDeadlineRatios, minThetaRatios, minBudgetUtils, resourcePeriods):

        taskSet = TaskGen().genTask('Uunifast',
                numOfTasks=numOfTasks,
                totalUtilization=totalUtilization,
                critProb = critProb,
                wcetRatio = wcetRatio,
                minDeadlineRatio = minDeadlineRatio)
        
        thetaC = (1-random.rand()*(1-minBudgetUtil))*resourcePeriod
        thetaN = (1-random.rand()*(1-minThetaRatio))*thetaC
        
        solver = SchedulabilityTest(taskSet, thetaN, thetaC, resourcePeriod, config)
        solver.solve()
        if solver.scalingFactor == -1:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = ----- <<< Fail!'
        elif solver.scalingFactor == -2:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = ----- <<< Fail! Infeasible rates'
        elif solver.scalingFactor == -3:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = ----- <<< Fail! Decrease epsilon'
        else:
            printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = {:5.3f}'
        
        print(printFormat.format(totalUtilization, iter, critProb, wcetRatio, minDeadlineRatio, solver.scalingFactor))
        log.addLog(
            totalUtilization=totalUtilization,
            iteration=iter,
            critProb=critProb,
            wcetRatio=wcetRatio,
            minDeadlineRatio=minDeadlineRatio,
            minThetaRatio=minThetaRatio,
            minBudgetUtil=minBudgetUtil,
            resourcePeriod=resourcePeriod,
            thetaC=thetaC,
            thetaN=thetaN,
            taskSet=taskSet,
            solver=solver
            )
        
        counter += 1
        if counter>=10000:
            counter = 0
            log.dumpData()
except:
    log.dumpData()

log.dumpData()
