import json

from taskGenerator import TaskSet, Task, TaskGen
from taskAnalyser import SchedulabilityTest

try:
    with open('sim.cfg', 'r') as fh:
        config = json.load(fh)
except FileNotFoundError:
    config = None

taskSet = TaskGen().genTask('Uunifast',
        numOfTasks=10,
        totalUtilization=0.9,
        critProb = 0.5,
        wcetRatio = 2,
        minDeadlineRatio = 0.7)
taskSet.listTasks()
SchedulabilityTest(taskSet, 60, 60, 60, config).solve()