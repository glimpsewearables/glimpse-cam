# Michael Fang
#
# class that generate logger which log all the information
# which is or above debug level into a log file
# the logName should be explicit and related to the file which uses this class
# all the informations will be stored in the file logName.log
# when w(True, False) is set, the logger will rewrite the log file instead of append to it
import sys
import logging

class log:
    def __init__(self, logName, w):
        # name of the log file in which we should keep our records
        self.logFile = logName + ".log"
        # the logger for the user to log information
        self.logger = logging.getLogger(logName)
        self.logger.setLevel(logging.DEBUG)
        # create File Handler and set level
        if (w):
            fh = logging.FileHandler(self.logFile, mode = 'w')
        else:
            fh = logging.FileHandler(self.logFile)
        fh.setLevel(logging.DEBUG)
        # create formatter and add it to the Handler
        formatter =logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s', '%m/%d/%Y %I:%M:%S %p')
        fh.setFormatter(formatter)
        # add the handler to the logger
        self.logger.addHandler(fh)

    def getLogger(self):
        return self.logger
