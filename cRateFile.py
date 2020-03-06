#####################################################################################
# author: Kamran Husain   husainkb@aramco.com.sa
#####################################################################################

import sys
import time
from pObject import *
from string import strip,find,split,join

#####################################################################################
# This is the object for tracking each step in rates file.
#####################################################################################
class cStepObject(pObject):
    def __init__(self,iLineNumber=0):
        pObject.__init__(self,iLineNumber)
        self.sTo = 0.0
        self.sFrom = 0.0
        self.Wells = {}         # Indexed by a name; no duplicates allowed. 

    ############################################################################
    # This gets the date in the form: MONTH DAY, YEAR from the incoming value. 
    # I append the value of the raw To Time to this date for reference. 
    ############################################################################
    def getToStepTime(self):
        s = time.strftime("%b %d, %Y",(time.gmtime(self.sTo * 86400)))
        sx = "(%10.4f)" % (self.sTo)
        return s + sx

    def getWellCount(self):
        s = "No. of wells= %d" % len(self.Wells)
        return s

    
    def printStartLine(self,fd):
        frac=    self.sTo/365.25
        if (self.sFrom == 0.0):
            xs = "&STEP TO =    %f /  %f   " % (self.sTo,frac)
        else:
            xs = "&STEP FROM =  %f  TO =    %f / %f    " % (self.sFrom,self.sTo,frac)
        xs = xs + time.strftime("%b %d, %Y",(time.gmtime(self.sTo * 86400)))
        xs = xs + '\n\tWELLS'
        fd.write(xs)
        
    def printStopLine(self,fd):
        fd.write('\tENDWELLS\nENDSTEP\n\n')



        
#####################################################################################
# This object tracks the keywords for a perforation object in a rates file. 
# Currently we do not check if an object has been allowed a keyword or not. 
#####################################################################################
class cPerfObject(pObject):
    def __init__(self,iLineNumber=0):
        pObject.__init__(self,iLineNumber)
   
    def printPerfLine(self,fd):
        xs = '\t\t&PERF '
        for i in self.aKeywords.keys():
            v = self.aKeywords[i]
            xs = xs + ' ' + i + ' = ' + v 
        xs = xs + '/\n'
        fd.write(xs)
        
        

#####################################################################################
# The states you have to parse lines in.
#####################################################################################
sIN_STATE_NONE = 0
sIN_STATE_STEP = 1
sIN_STATE_WELL = 2
sIN_STATE_PERF = 3
#####################################################################################
# Start of class description
#####################################################################################
class cRateFile:
    def __init__(self):
        self.Steps = []         # Indexed by a number
        self.allWellNames = []
        self.Time = "None"      # to mark each well as it is added. 
        self.lastStep = None    
        self.lastWell = "None"
        self.inState = sIN_STATE_NONE
        self.aAllowedPerfKeywords = ['Name','Type','Well_Radius','CD',
                'Productivity_Index',
                'I','J','K','Rf','K_BOTTOM','K_TOP','GRID_NAME']
        self.aAllowedWellKeywords = ['Name','Type','Well_Radius',
                'WELL_DEPTH_DATUM','MAXDDP','MAXBHP','MINBHP','BHP','Well_PI',
                'Qo','Qw','Qg']
        self.aAllowedWellTypes = [
            'Total_Liq_Prod_Rate_Specified','Total_Oil_Prod_Rate_Specified',
            'Total_Water_Prod_Rate_Specified','Gas_Prod_Rate_Specified',
            'MP_Well','Producer','Undrilled_Producer','Bottom_Hole_Pressure_Specified',
            'Water_Inj_Rate_Specified','Gas_Inj_Rate_Specified','Oil_Inj_Rate_Specified',
            'Injector','Undrilled_Injector','Unspecified_Injector']
        self.specialKeywords  = ['Name','Type','CD'] 

    #########################################################
    # 
    #########################################################
    def removeQuotes(self,incoming):
        xstr = incoming.replace("'",'')
        xstr = xstr.replace('"','')
        return xstr

    #########################################################
    # Each line that is within a well block is processed here. 
    #########################################################
    def processWellLine(self,incomingItems,echo=0):
        tempstr = join(incomingItems,' ')
        tempstr = tempstr.replace('=',' ')
        xitems = split(tempstr)
        slen = len(xitems)
        i = 0
        if echo == 1:
            print xitems 
        while i < slen:
            key = xitems[i]
            value = xitems[i+1]
            if echo == 1:
                print key,value
            self.lastWell.addKeyword(key,value)
            i  = i + 2    # skip past value

    #########################################################
    # Create a well and parse the rest of the input line.
    #########################################################
    def startWell(self,items):
        klen = len(items)      
        slen = klen - 1 
        self.lastWell = cWellObject()   # Create a well object for this step.
        wellName = self.removeQuotes(items[3])
        self.lastWell.sIdString = wellName
        if not wellName in self.allWellNames:
            self.allWellNames.append(wellName)
        self.lastStep.Wells[wellName] =  self.lastWell
        self.inState = sIN_STATE_WELL
        self.processWellLine(items[1:])
        
    #########################################################
    # Perforations are per well. Check k
    #########################################################
    def startPerf(self,items):
        self.inState = sIN_STATE_PERF
        self.lastPerf = cPerfObject()
        self.lastPerf.sIdString = 'PERF'
        self.lastPerf.sTime = self.lastStep.sTo               # Mark it at this time. 
        self.lastWell.perforations.append(self.lastPerf)
        self.processPerfLine(items[1:])

    #########################################################
    # Process the keyword=value items in the incoming list.
    #########################################################
    def processPerfLine(self,incomingItems):
        tempstr = join(incomingItems,' ')   # Trust me. 
        tempstr = tempstr.replace('=',' ')  # Get rid of equal sign
        items = split(tempstr)              # resplit into keywords.
        slen = len(items)
        i = 0
        while i < slen:
            key = items[i]
            value = items[i+1]
            self.lastPerf.addKeyword(key,value)
            i = i + 2            # skip past value


    #########################################################
    # Allowed sample lines from input file. 
    #  &STEP TO =    XX.XX  /
    #  &STEP FROM = XX.XX TO = XX.XX /
    #########################################################
    def startStep(self,items):
        kTo = -1
        kFrom = -1
        if (len(items) == 4): kTo = 3
        if (len(items) == 7): kFrom = 3; kTo = 6
        if (kTo <> -1):
            self.inState = sIN_STATE_NONE
            self.lastStep = cStepObject()       # Accumulate
            self.lastStep.sIdString = 'STEP '+items[kTo]
            self.lastStep.sTo = float(items[kTo])        # Get the TO date
            if (kFrom <> -1):
                self.lastStep.sFrom = float(items[kFrom]) # Get the FROM date if there. 
            self.Steps.append(self.lastStep)    # No need for keywords 
        else:
            print "Unable to parse tuple:",items
    
    ###################################################################
    # Once the bogus lines are removed, we can start with 
    ###################################################################
    def parseKeywords(self,incoming):
        items = split(incoming)      # 
        if (len(items) < 1):
            return; 
        keyword = items[0]           # The keyword

        ##################################################################
        # Check the end of block statements or statemnts to ignore. 
        ##################################################################
        if (keyword == 'ENDSTEP'):  self.inState = sIN_STATE_NONE; return
        if (keyword == 'ENDWELLS'): self.inState = sIN_STATE_NONE; return
        if (keyword == 'WELLS'):   return;          # Ignore this one. 

        #######################################################################
        # Check the state here. If a new well or step is started, we go there
        #######################################################################
        if (keyword == '&STEP'):   self.startStep(items); return 
        if (keyword == '&WELL'):   self.startWell(items); return 
        if (keyword == '&PERF'):   self.startPerf(items); return 

        # Check if in perforation or if in well.
        if (self.inState == sIN_STATE_PERF):  self.processPerfLine(items); return
        if (self.inState == sIN_STATE_WELL):  self.processWellLine(items); return


    ################################################################
    # The line pre-parser.
    ################################################################
    def parseLine(self,incoming):
        eol = find(incoming,'/')      # Comment on this line.
        if (eol > -1):
            incoming = incoming[0:eol]   #  remove from / to eol
        sline  = strip(incoming)   # remove blank spaces from start and end.
        if len(sline)<1:           # Ignore blank lines. 
            return
        if (sline[0] == '#'):      # ignore comments
            return
        self.parseKeywords(incoming)

    ################################################################
    # This reads from scratch.
    ################################################################
    def readRateFile(self,name):
        self.clearMemory()
        fd = open(name,'r')
        s = fd.readline() 
        while (s <> ''):                     # Check for eof.
            self.parseLine(s)
            s = fd.readline()
        fd.close();

    ################################################################
    # This clears all the arrays.
    ################################################################
    def clearMemory(self):
        self.Steps = []         # Indexed by a number
        self.allWellNames = []
        self.Time = "None"      # to mark each well as it is added. 
        self.lastStep = None    
        self.lastWell = "None"
        self.inState = sIN_STATE_NONE


    ################################################################
    #
    ################################################################
    def getErrorMessages(self):
        self.errors = '' 
        for iStep in self.Steps:
            if (iStep.getErrorCount() > 0):
                xstr = iStep.getErrorReport()    # Get summary for object.
                self.errors = self.errors + xstr # only if errors exists
            for wkey in iStep.Wells.keys():
                iWell = iStep.Wells[wkey]
                if (iWell.getErrorCount() > 0):
                    xstr = iWell.getErrorReport() + " for " + iWell.getKeywordValue('Name')
                    self.errors = self.errors + xstr # only if errors exists
                for iPerf in iWell.perforations:
                    if iPerf.getErrorCount() > 0:
                        xstr = iPerf.getErrorReport() + " for " + iPerf.getOneLiner()
                        self.errors = self.errors + xstr # only if errors exists
        return self.errors                    


    ################################################################
    # Do your consistency check here. 
    ################################################################
    def doConsistencyCheck(self):
        doCount = 0
        for istep in self.Steps:                # Forget it. Only on reads. 
            for wkey in istep.Wells.keys():     #
                iWell = istep.Wells[wkey]       # 
                iWell.clearErrors()
                checkKeys = iWell.getKeywords() #
                for ix in checkKeys:
                    if not ix in self.aAllowedWellKeywords:
                        xstr = 'Error: Bad keyword in Well %s -->[%s], step %f\n' % (ix,iWell.getKeywordValue('Name'),istep.sTo)
                        iWell.addErrorMessage(xstr)
                        doCount = doCount + 1
                        if (doCount > 100):
                            xstr = 'Too many errors... aborting this well'
                            iWell.addErrorMessage(xstr)
                            break;
                    if (ix == 'Type'):
                        sx = iWell.getKeywordValue(ix)
                        sx = self.removeQuotes(sx)
                        if not sx in self.aAllowedWellTypes:
                            xstr = 'Error: Bad well type in Well %s -->[%s], well %s step %f\n' % (ix,sx,iWell.getKeywordValue('Name'),istep.sTo)
                            iWell.addErrorMessage(xstr)
                            doCount = doCount + 1
                            if (doCount > 100):
                                xstr = 'Too many errors... aborting this well'
                                iWell.addErrorMessage(xstr)
                                break;
                for iPerf in iWell.perforations:
                    checkKeys = iPerf.getKeywords() #
                    for ix in checkKeys:
                        if not ix in self.aAllowedPerfKeywords:
                            xstr = 'Error: Bad keyword in Perf %s -->[%s]\n' % (ix,iPerf.getOneLiner)
                            iPerf.addErrorMessage(xstr)
                    


    ################################################################
    #
    ################################################################
    def writeRateFile(self,fd):
        for istep in self.Steps:                # Forget it. Only on reads. 
            istep.printStartLine(fd)             
            for wkey in istep.Wells.keys():     #
                iWell = istep.Wells[wkey]       # 
                iWell.printWellLine(fd)         #
                for iPerf in iWell.perforations:
                    iPerf.printPerfLine(fd)
            istep.printStopLine(fd)             

    ################################################################
    # Debug
    ################################################################
    def printSteps(self):
        for s in self.Steps:
            print s.getToStepTime(),s.getWellCount()

####################################
#
####################################
if __name__ == '__main__':
    import os
    import sys
    mx = cRateFile();
    if (len(sys.argv) > 1):
        mx.readRateFile(sys.argv[1])
        mx.doConsistencyCheck()
        xstr = mx.getErrorMessages()
        if (len(xstr) < 1):
            print "No errors found"
        else:
            print xstr
