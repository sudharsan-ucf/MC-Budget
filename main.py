import json

from taskGenerator import TaskSet, Task, TaskGen
from taskAnalyser import SchedulabilityTest

try:
    with open('sim.cfg', 'r') as fh:
        config = json.load(fh)
except FileNotFoundError:
    config = None

T1 = TaskSet()

T1.addTask(Task(2, 2, 10, 10, 'LO', 0.9))
T1.addTask(Task(4, 5, 10, 6, 'HI'))
T1.listTasks()

S1 = SchedulabilityTest(T1, 60, 60, 60, config)
S1.solve()