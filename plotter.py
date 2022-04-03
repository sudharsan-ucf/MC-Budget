class Logger(list):
    def addLog(self, **kwargs):
        self.append(kwargs)