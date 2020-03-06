"""
The perf file parser for POWERS

author: Kamran Husain   husainkb@aramco.com.sa

"""
import os, sys, time
from pObject import *
from string import strip,find,split
from time import *
import copy

#####################################################################################
# The states you have to parse lines in.
#####################################################################################
sIN_STATE_NONE = 'NONE'
sIN_STATE_DATE = 'DATE'
sIN_STATE_WELL = 'WELL'
sIN_STATE_PERF = 'WELL'
sIN_STATE_ENDWELLS = 'ENDWELLS'
sIN_STATE_WELLSTART = 'WELLS'

#####################################################################################
# Start of class description
#####################################################################################
class cPerfFile(cParserObject):
	def __init__(self,useTheseDates={},useTheseWellNames={}):
		cParserObject.__init__(self)
		self.applyInitialTree(useTheseDates,useTheseWellNames)
		self.Steps = []		 # Indexed by a number
		self.lastDate = None	
		self.lastWell = None
		self.lastWellName = None
		self.lastPerf = None
		self.lineNumber = 0	
		self.currentState = sIN_STATE_NONE
		self.sQuotedKeywords = ['INCLUDE_FILE','BINARY_FILE','GRID_NAME','CD']

	#########################################################
	def startWell(self,ilo):
		""" Create a well and parse the rest of the input line.  """
		xln = ilo.getCookedLine()
		xln = xln.replace('=',' ')
		items = split(xln)
		name = self.removeQuotes(items[2])         # Get the well name, it has to be 3rd
		name = name.replace('/','')
		if len(name) > 8: 
			self.addErrorMessage("Error: Line %d: Truncate long Well Name %s to %s " % (self.lineNumber, name, name[:8]))
			name = name[:8]
		self.lastWellName = name

		######################################################################################
		# At this point the date may have a well defined from Rates parser. Use it.
		# The addWell function will copy any existing perforations and/or keywords at
		# this date.
		# The global list of allWellNames is already set per well in the
		######################################################################################
		if self.lastDate.Wells.has_key(name):
			#print "Starting with old well ", name
			self.lastWell = self.lastDate.addWell(name,useThisWell=self.lastDate.Wells[name])
		else: 
			#print "Starting with new well ", name
			self.lastWell = self.lastDate.addWell(name,ilo=ilo,useThisWell=None)   # Create a new one.
			self.allWellNames[name] = self.lastWell                                # Add to global
		#print "Finished well ", name

	###################################################################
	def parseLine(self,ilo):
		#print self.currentState, ilo.getRawLine()
		if ilo.mustProcess == 0: return 
		items = ilo.splitcookedItems
		keyword = items[0]		   # The keyword
		#print "Perf parser", ilo.getRawLine()
		if (keyword == 'DATE'):  
			#print "Perf parser", ilo.getRawLine() 
			self.processDateLine(items,source=sourcePERFS) 
			self.currentState = sIN_STATE_DATE
			self.lastDate.mergeExistingWells(self.allWellNames.keys())   # Defined well names only up to this date.
			return
		if (keyword == 'WELLS'):     
			if self.currentState <> sIN_STATE_DATE:
				self.addErrorMessage("Line %d :WELLS starting without a DATE parameter at line " % self.lineNumber)
			self.currentState = sIN_STATE_WELLSTART
			return
		if (keyword == '/'):     
			if not self.currentState in [sIN_STATE_PERF, sIN_STATE_WELL]:
				self.addErrorMessage("Error Line %d: Unterminated PERF or WELL near this line\n" % self.lineNumber)
			self.currentState = sIN_STATE_WELLSTART 
			return
		if (keyword == 'ENDWELLS'):     
			self.currentState = sIN_STATE_ENDWELLS; 
			self.lastDate.mergeExistingWells(self.allWellNames.keys())   # July 26, 2005 - Reset running well names list
			return
		if (keyword == '&WELL'):              
			#print "Perf parser start Well", self.currentState, sIN_STATE_WELL
			self.startWell(ilo)
			self.currentState  = sIN_STATE_WELL
			return
		if (keyword == '&PERF'):              
			rp = self.startPerf(ilo) 			 #Use the raw string
			if rp == 0:
				self.currentState  = sIN_STATE_PERF
			else:
				self.currentState  = sIN_STATE_WELL
			return
		if (self.currentState == sIN_STATE_PERF):  
			incoming = ilo.getCookedLine()
			tstr = incoming.replace('=',' ')   # Remove the quotes completely 
			rp  = self.processPerfLine(split(tstr)) 	   # Do NOT use the raw string
			if rp == 0:
				self.currentState  = sIN_STATE_PERF
			else:
				self.currentState  = sIN_STATE_WELL
			return
		self.addErrorMessage("Warning Line %d: Orphan keywords near line " % (self.lineNumber, ilo.getRawLine()))
		
	def startPerf(self,ilo):
		incoming = ilo.getCookedLine()
		tstr = incoming.replace('=',' ')   # Remove the equal sign completely 
		items = split(tstr)                # Tokenize
		self.lastPerf = cPerfObject(ilo)
		rcp =  self.processPerfLine(items[1:])     #
		self.lastPerf.setPerfName()                # Get the ID from I,J,K
		self.lastWell.addPerforation(self.lastPerf) # Now add to the well
		self.allWellNames[self.lastWellName] = copy.copy(self.lastWell)   # Make sure it lives!
		return rcp

	def processPerfLine(self,xitems):
		""" You must pass in a list of tokens """
		slen = len(xitems)	               # item 0 is your WELL Name
		i = 0
		while i < slen:
			key = xitems[i]
			if key == '/': return 1
			if i >= (slen-1):
				self.addErrorMessage(  "Error Line %d: Unassigned keyword %s" % (self.lineNumber,key))
				try:
					value = xitems[i+1]
				except:
					value = 0
				return 1
			#value = self.removeQuotes(xitems[i+1])   # No need.
			lkey = key.upper()                       # Always use upper case
			self.lastPerf.addKeyword(lkey,xitems[i+1])     # It will remove the quotes
			if not lkey in cPerfAllowedKeywords:
				self.addErrorMessage( "Error Line %d: Unrecognized keyword %s" % (self.lineNumber,key))
			i  = i + 2	# skip past value
		return 0

	################################################################
	def readPerfFile(self,filename,keepCopyOfLine=0,notifyFunction=None):
		self.readDataFile(filename,keepCopyOfLine,notifyFunction)


	################################################################
	def clearMemory(self):
		self.Steps = []		 # Indexed by a number
		self.allWellNames = self.userWellNames
		self.allDates     = self.userDates 
		self.lastWell = None 
		self.lastDate = None 
		self.lastPerf = None 
		self.currentState = sIN_STATE_NONE

	################################################################
	def getErrorMessages(self):
		self.errors = self.doConsistencyCheck() 
		return self.errors					


	################################################################
	def doConsistencyCheck(self):
		istr = 0  
		for dt in self.allDates.values():
			for well in dt.Wells.keys():
				if len(well) > 8: print "bad well name"
				#daWell = dt.Wells[well]
				#if daWell.getErrorCount() > 0: 
					#istr = istr + 1
					#print daWell.getErrorReport(),"\n"
		if istr > 0: return "%d errors found" % istr
		return ''


	def printHistory(self):
		""" Debug """
		for dt in self.allDates.values(): print dt.getDate()


####################################
#
####################################
if __name__ == '__main__':
	mx = cPerfFile();
	if (len(sys.argv) > 1):
		mx.readPerfFile(sys.argv[1])
		xstr = mx.doConsistencyCheck()
		if len(xstr) > 0: 
			print xstr

