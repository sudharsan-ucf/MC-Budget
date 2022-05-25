from matplotlib import pyplot as plt
import seaborn
import os
import pandas
import pickle
import datetime

# from plotter import Plotter
from matplotlib.font_manager import FontManager
from matplotlib.font_manager import findSystemFonts
from matplotlib import rcParams

font_dirs = [os.path.join(os.getcwd(), 'fonts', 'Serif')]
font_files = findSystemFonts(fontpaths=font_dirs)

fm = FontManager()
for path in font_files:
    fm.addfont(path)
    
rcParams['font.family'] = 'Computer Modern Serif'
rcParams['text.usetex'] = True

dirPathPlot = os.path.join(os.getcwd(), 'plots')
if not os.path.isdir(dirPathPlot):
    os.mkdir(dirPathPlot)


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


class Plotter():
    def __init__(self, logFolderName = 'logs'):
        self.logFiles = []
        dirPathLog = os.path.join(os.getcwd(), logFolderName)
        for fileName in os.listdir(dirPathLog):
            if fileName[-3:] == "pkl":
                self.logFiles.append(fileName)
        columnNames = ['Theta Ratio', 'Supply Budget Ratio', 'Resource Period', 'Crit Prob', 'WCET Ratio', 'Rate', 'Deadline Ratio', 'Average Utilization', 'Iteration', 'ThetaC', 'ThetaN', 'Scaling Factor']
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


masterData = Plotter('logsWorkload')
masterData = masterData.database.assign(scheduleSuccess=masterData.database["Scaling Factor"]>=0)


# index = X Axis; columns = Parameter Varied; values = Y Axis
pPlots = "Crit Prob"
pIndex = "Average Utilization"
pColumns = "Deadline Ratio"
pValues = "Schedulability Ratio"
pCategory = "Rate"


for plotIndex in masterData[pPlots].unique():
    # successGB = masterData.groupby(by=[pCategory, pColumns, pIndex])["scheduleSuccess"]
    successGB = masterData[masterData[pPlots] == plotIndex].groupby(by=[pCategory, pColumns, pIndex])["scheduleSuccess"]
    resultsDF = successGB.sum().to_frame()
    resultsDF = resultsDF.assign(scheduleTotal=successGB.count())
    resultsDF = resultsDF.assign(scheduleRatio=lambda x: x.scheduleSuccess/x.scheduleTotal)
    resultsDF.rename(columns = {'scheduleSuccess':'Schedule Success', 'scheduleTotal':'Schedule Total', 'scheduleRatio':pValues}, inplace = True)
    resultsDF = resultsDF.reset_index()

    cColumns = resultsDF[pCategory].unique()
    numPlots = len(cColumns)

    for categoryIndex in range(numPlots):
        fig, ax = plt.subplots(figsize=(5, 3))
        plotData = resultsDF[resultsDF[pCategory] == cColumns[categoryIndex]].pivot(index=pIndex, columns=pColumns, values=pValues)
        seaborn.lineplot(
            data = plotData,
            ax = ax,
            markers = True,
            legend = False)
        ax.grid(True)
        ax.set_ylim((-0.05, 1.05))
        ax.set_ylabel(pValues)
        ax.set_title('{:} = {:}; {:} = {:}'.format(pCategory, cColumns[categoryIndex], pPlots, plotIndex))
        ax.legend(
            labels = resultsDF[pColumns].unique(),
            loc="upper right",
            title=pColumns)

        fileNamePlot = '{:}_{:}_{:02d}_{:}_{:02d}.png'.format(pColumns,pCategory,int(cColumns[categoryIndex]*10),pPlots,int(plotIndex*10)).replace(" ", "")
        fig.savefig(
            fname = os.path.join(dirPathPlot, fileNamePlot),
            bbox_inches = "tight",
            dpi = 600)

        fileNamePlot = '{:}_{:}_{:02d}_{:}_{:02d}.pdf'.format(pColumns,pCategory,int(cColumns[categoryIndex]*10),pPlots,int(plotIndex*10)).replace(" ", "")
        fig.savefig(
            fname = os.path.join(dirPathPlot, fileNamePlot),
            bbox_inches = "tight",
            dpi = 600)
