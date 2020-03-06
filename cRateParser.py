
#####################################################################################
# author: Kamran Husain   kamran.husain@aramco.com
#####################################################################################

import os, sys, time
from pObject import *
from string import strip,find,split,join,replace,upper
from time import *
import copy

#####################################################################################
# The states you have to parse lines in.
#####################################################################################
sIN_STATE_NONE = 'NONE'
sIN_STATE_DATE = 'DATE'
sIN_STATE_WELL = 'WELL'
sIN_STATE_ENDWELLS = 'ENDWELLS'
sIN_STATE_WELLEND =  'WELLEND'
sIN_STATE_WELLSTART = 'ATWELL'


sRateFileCasedKeywords = ['Name','Type','Fluid','Well_Radius',
				'Qo','Qw','Qg','DATUM_DEPTH','Well_Factor','BHP','Well_PI','Drainage_Radius'
				'Max_qo','Max_qw','Max_qg','Min_qo','Min_qw','Min_qg','Min_BHP','Max_DDP',
				'Min_WHP','Max_BUP','Max_BHP','Flow_Table','Well_Priority','Well_PI','Inj_Comp' ] 
sRateFileAllowedKeywords = map(upper, sRateFileCasedKeywords)

#####################################################################################
# Start of class description
#####################################################################################
class cRateFile(cParserObject):
	def __init__(self,useTheseDates={},useTheseWellNames={}):
		cParserObject.__init__(self)
		self.applyInitialTree(useTheseDates,useTheseWellNames)
		self.lastDate = None	
		self.lastWell = None
		self.lastWellName = None
		self.lineNumber = 0	
		self.filename = ' '
		self.currentState = sIN_STATE_NONE
		#self.aCasedAllowedWellKeywords = ['Name','Type','Fluid','Well_Radius',
				#'Qo','Qw','Qg','DATUM_DEPTH','Well_Factor','BHP','Well_PI','Drainage_Radius'
				#'Max_qo','Max_qw','Max_qg','Min_qo','Min_qw','Min_qg','Min_BHP','Max_DDP',
				#'Min_WHP','Max_BUP','Max_BHP','Flow_Table','Well_Priority','Well_PI','Inj_Comp' ] 
		#self.aAllowedWellKeywords = map(upper, self.aCasedAllowedWellKeywords)

		self.aCasedAllowedWellKeywords = sRateFileCasedKeywords
		self.aAllowedWellKeywords = map(upper, self.aCasedAllowedWellKeywords)

		self.aAllowedWellTypes = [ 'Producer','Injector', 
			'BHP_producer','BHP_injector', 'MP_Producer','MP_Injector','Observation_Well']
		self.aAllowedFluidTypes = [ 'oil','liquid', 'water', 'gas', 'total_fluid']

	def getAllowedKeywords(self):
		return self.aCasedAllowedWellKeywords 

	#########################################################
	def processWellLine(self,xitems):
		""" 
		Works with self.lastWell
		You must pass in a list of tokens 
		"""
		slen = len(xitems)				   # key,value pairs
		if slen == 0:					  # Blank line
			#self.currentState = sIN_STATE_WELLEND; 
			return
		####################################################################################
		# If slen is even, then process k,v pairs. 
		# If slen is odd, last item must be '/' -> if not, error
		####################################################################################
		if slen >= 1 and xitems[0] == '/':               # Comment + end of well all in one
			self.currentState = sIN_STATE_WELLEND; 
			return 

		odd = slen % 2; 
		if odd == 1: 
			if xitems[-1] <> '/': 
				self.addErrorMessage("Error %s, Line %d: Unterminated WELL " % (self.filename, self.lineNumber))
				print xitems, self.lastDate.getDate()
				return
			self.currentState = sIN_STATE_WELLEND; 
			a = xitems.pop()
			
		slen = len(xitems)				   # key,value pairs
		i = 0
		while i < slen:
			rawvalue = xitems.pop()
			key   = xitems.pop()
			i = i + 2
			# Replace with in-line .
			#value = self.removeQuotes(rawvalue)   # Get the value without quotes
			value =  rawvalue.replace("'",'')
			value = value.replace('"','')
			if value == '/' or key == '/': 
				self.currentState = sIN_STATE_WELLEND; 
				return
			self.lastWell.addKeyword(upper(key),value)	                        # Preserve it.
			#self.allWellNames[self.lastWellName].addKeyword(upper(key),value) # Accumulate only if just added!!!
			lkey = key.upper()
			if not lkey in self.aAllowedWellKeywords: 	# Check it.
				self.addErrorMessage("Error %s, Line %d: Unrecognized keyword %s" % (self.filename,self.lineNumber,key))
				sys.exit
			if lkey == 'fluid':
				lvalue = value.upper() 				# Case insensitive
				if not lvalue in self.aAllowedFluidTypes:
					self.addErrorMessage("Error %s, Line %d: Illegal Fluid Type %s" % (self.filename,self.lineNumber,value))
			if lkey == 'type':
				if not value in self.aAllowedWellTypes: # Check values for types
					self.addErrorMessage("Error %s, Line %d: Illegal well Type %s" % (self.filename, self.lineNumber,value))

	#########################################################
	def startWell(self,ilo):
		""" 
			Create a well if it does not already exist 
			and parse the rest of the input line.  
		"""
		incoming = ilo.getCookedLine()         # Removes comments,
		incoming = incoming.replace("'",'')
		incoming = incoming.replace('"','')
		tstr = incoming.replace('=',' ')	   # Remove the equal sign completely 
		items = split(tstr)					   # Tokenize
		name = items[2]					   # Get the well name, it has to be 3rd
		name = name.replace('/','')    
		if len(name) > 8: 
			self.addErrorMessage("Error: Line %d: Truncate long Well Name %s to %s " % (self.lineNumber, name, name[:8]))
			name = name[:8]
		self.lastWellName = name
		if self.allWellNames.has_key(name):         # Well already exists.
			self.lastWell = self.lastDate.addWell(name,useThisWell=self.allWellNames[name]) # Use copy.
			self.processWellLine(items[1:])		    # Process any additional keywords here.
		else:
			self.lastWell = self.lastDate.addWell(name,ilo=ilo,useThisWell=None)   # Create a new one.
			self.processWellLine(items[1:])		                  # Process any keywords here.
			self.allWellNames[name] = self.lastWell               # Running count
	###################################################################

	###################################################################
	def parseLine(self,ilo):
		"""
		Workhorse routine for the parser. Switches on keyword ilo[0].
		Ignores empty lines.
		"""
		if ilo.mustProcess == 0: return 
		items = ilo.splitcookedItems
		#if len(items) < 1: return 
		keyword = items[0]		   # The keyword
		if (keyword == 'DATE'):  
			self.processDateLine(items,source=sourceRATES)
			self.lastDate.mergeExistingWells(self.allWellNames.keys())   # July 26, 2005 - Reset running well names list
			self.currentState = sIN_STATE_DATE
			return
		if (keyword == 'WELLS'):	 
			if self.currentState <> sIN_STATE_DATE and self.currentState <> sIN_STATE_ENDWELLS:
				if self.lastDate == None: 
					self.addErrorMessage("Error %s, Line %d :WELLS starting without even one DATE keyword . " \
					% self.filename,self.lineNumber)
				else: 
					self.addErrorMessage("Error %s, Line %d :WELLS starting without a DATE. [Last %s]" \
					% (self.filename,self.lineNumber,self.lastDate.getDate()))
			self.currentState = sIN_STATE_WELLSTART
			return
		if (keyword == '/'):	 
			if not self.currentState in [sIN_STATE_WELL, sIN_STATE_WELLEND]:
				self.addErrorMessage("Error Line %s: Unterminated well near line %d state = %s\n" % \
						(self.filename,self.lineNumber, self.currentState))
			self.currentState = sIN_STATE_WELLEND; 
			return
		if (keyword == 'ENDWELLS'):	 
			if self.currentState <> sIN_STATE_WELLEND or self.currentState == sIN_STATE_WELL:
				self.addErrorMessage("Error: Bad ENDWELLS near %s, line %d Check if well terminated earlier.\n" \
						% (self.filename, self.lineNumber))
			self.currentState = sIN_STATE_ENDWELLS; 
			self.lastDate.mergeExistingWells(self.allWellNames.keys())   # July 26, 2005 - Reset running well names list
			return
		if (keyword == '&WELL'):			  
			if self.currentState == sIN_STATE_WELL or self.currentState == sIN_STATE_ENDWELLS: 
				self.addErrorMessage("Error: Bad start WELL near %s, line %d - Possible unterminated prior well definition.\n" \
						% (self.filename, self.lineNumber))
			self.currentState  = sIN_STATE_WELL
			self.startWell(ilo) 			 #Use the raw string
			return
		if (self.currentState == sIN_STATE_WELL):  
			# Special processing for wells.
			incoming = ilo.getCookedLine()
			tstr = incoming.replace('=',' ')	   # Remove the equal signs completely 
			tstr = tstr.replace("'",'')
			tstr = tstr.replace('"','')
			self.processWellLine(split(tstr)) 	   # Do NOT use the raw string
			return
		self.addErrorMessage("Warning %s, Line %d: Orphan keywords near line " % (self.filename,self.lineNumber))
		self.addErrorMessage('-- ['+ ilo.getRawLine() + ']')
	
	################################################################
	def clearMemory(self):
		self.allWellNames    = self.userWellNames
		self.allDates = self.userDates
		self.lastWell = None 
		self.lastDate = None 
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
				daWell = dt.Wells[well]
				if daWell.getErrorCount() > 0: 
					istr = istr + 1
					print daWell.getErrorReport(),"\n"
		if istr > 0: return "%d errors found" % istr
		return ''


	def printHistory(self):
		""" Debug """
		for dt in self.allDates.values(): print dt.getDate()

	def writeRateFile(self,fd):
		""" Unfinished, Not needed, Only if we develop a GUI """
		for dt in self.allDates.values(): 
			print "\n",dt.getDate(),"\n"
			if len(dt.Wells.keys()) > 0: print "\tWELLS\n"
			for well in dt.Wells.keys():
				daWell = dt.Wells[well]
				print "\t\t&WELL Name = ", daWell.aKeywords['NAME']
				for k in daWell.aKeywords.keys():
					if k <> 'NAME':
						print "\t\t\t%s = %s\n" % ( k, daWell.aKeywords[k])
				print "\t\t\t/\n\n"
			if len(dt.Wells.keys()) > 0: print "\t\tENDWELLS\n\n"

	def writeDates(self):
		for dt in self.allDates.values():
			xstr = "<DATE>" + dt.getDate() + "</DATE>\n" 
			print xstr
		

	def writeAsXML(self,fd):
		fd.write('<?xml version="1.0" standalone="yes">\n')
		fd.write("<RESPONSE>\n")
		fd.write("<PARAMETERS>\n")
		fd.write("Original query here.")
		fd.write("</PARAMETERS>\n")
		for dt in self.allDates.values():
			xstr = "<DATE>" + dt.getDate() + "</DATE>\n" 
			fd.write(xstr)
			if len(dt.Wells.keys()) > 0: 
				fd.write("<WELLS>\n")
				for well in dt.Wells.keys():
					daWell = dt.Wells[well]
					fd.write("<WELL>")
					xstr = "<NAME>" + daWell.aKeywords['NAME'] + "</NAME>\n"
					fd.write(xstr)
					for k in daWell.aKeywords.keys():
						if k <> 'NAME':
							xstr = "<" + k + ">" + daWell.aKeywords[k] + "</" + k + ">\n"
						fd.write(xstr)
					fd.write("</WELL>\n")
				fd.write("</WELLS>\n")
		fd.write("</RESPONSE>\n")


	def extractWellNames(self,filename):
		self.allWellNames = {}
		fd = open(filename,'r')
		inline = fd.readline()
		while inline <> '':
			f = inline.find('&WELL')
			if f >= 0: 
				inline = inline.replace("""'""",'')
				items = inline.split()
				wname = items[3]
				self.allWellNames[wname] = 1 
			inline = fd.readline()
		fd.close()	

####################################
#
####################################
if __name__ == '__main__':
	mx = cRateFile();
	if (len(sys.argv) > 1):
		mx.readDataFile(sys.argv[1])
		#profile.run('mx.readDataFile(sys.argv[1])')

		key = 'ZULF0197'
		well =  mx.allWellNames[key]
		print well.aKeywords

		dsorts = mx.allDates.keys()
		for d in dsorts:
			dte = mx.allDates[d]
			if dte.Wells.has_key(key):
				print dte.Wells[key].aKeywords
		sys.exit(0)
		#xstr = mx.doConsistencyCheck()
		#if len(xstr) > 0: print xstr
		#if (len(sys.argv) > 2):
			#fd = open(sys.argv[2],"w")
			#mx.writeAsXML(fd)
			#fd.close()
		#mx.writeDates()


if __name__ == '__ain__':
	mx = cRateFile();
	if (len(sys.argv) > 1):
		tmA = time()
		mx.extractWellNames(sys.argv[1])
		tmB = time()
		print "I have ", len(mx.allWellNames.keys()), " well names"
		print "Time taken ", tmB - tmA, " seconds " 

