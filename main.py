import itertools
import json

from taskGenerator import TaskSet, Task, TaskGen
from taskAnalyser import SchedulabilityTest

try:
    with open('sim.cfg', 'r') as fh:
        config = json.load(fh)
        numOfTasks = config['numOfTasks']
        iterations = range(config['numOfIterations'])
        critProbs = config['critProbs']
        wcetRatios = config['wcetRatios']
        minDeadlineRatios = config['minDeadlineRatios']
        totalUtilizations = config['totalUtilizations']
except FileNotFoundError:
    config = None
    numOfTasks = 10
    iterations = range(10)
    critProbs = [0.5]
    wcetRatios = [2,3]
    minDeadlineRatios = [0.7, 0.8]
    totalUtilizations = [0.1, 0.3, 0.5, 0.7]

for totalUtilization, iter, critProb, wcetRatio, minDeadlineRatio in itertools.product(
    totalUtilizations, iterations, critProbs, wcetRatios, minDeadlineRatios):

    taskSet = TaskGen().genTask('Uunifast',
            numOfTasks=numOfTasks,
            totalUtilization=totalUtilization,
            critProb = critProb,
            wcetRatio = wcetRatio,
            minDeadlineRatio = minDeadlineRatio)
    
    # if config['VERBOSE']:
    #     taskSet.listTasks()
    
    solver = SchedulabilityTest(taskSet, 60, 60, 60, config)
    solver.solve()
    if solver.scalingFactor < 0:
        printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = ----- <<< Fail!'
    else:
        printFormat = 'U = {:5.3f} | #{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = {:5.3f}'
    
    print(printFormat.format(totalUtilization, iter, critProb, wcetRatio, minDeadlineRatio, solver.scalingFactor))