import itertools
import json

from taskGenerator import TaskSet, Task, TaskGen
from taskAnalyser import SchedulabilityTest

try:
    with open('sim.cfg', 'r') as fh:
        config = json.load(fh)
        iterations = range(config['numOfIterations'])
        critProbs = config['critProbs']
        wcetRatios = config['wcetRatios']
        minDeadlineRatios = config['minDeadlineRatios']
except FileNotFoundError:
    config = None
    iterations = range(10)
    critProbs = [0.5]
    wcetRatios = [2,3]
    minDeadlineRatios = [0.7, 0.8]

for iter, critProb, wcetRatio, minDeadlineRatio in itertools.product(
    iterations, [0.5],
    [2,3], [0.7, 0.8]):

    taskSet = TaskGen().genTask('Uunifast',
            numOfTasks=10,
            totalUtilization=0.9,
            critProb = 0.5,
            wcetRatio = 2,
            minDeadlineRatio = 0.7)
    
    # if config['VERBOSE']:
    #     taskSet.listTasks()
    
    solver = SchedulabilityTest(taskSet, 60, 60, 60, config)
    solver.solve()
    if solver.scalingFactor < 0:
        printFormat = '#{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = ----- <<< Fail!'
    else:
        printFormat = '#{:3d} | P = {:4.2f} | R = {:5.2f} | D = {:4.2f} | x = {:5.3f}'
    
    print(printFormat.format(iter, critProb, wcetRatio, minDeadlineRatio, solver.scalingFactor))