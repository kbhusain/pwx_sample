"""
This file handles the input/output for Compositional objects.  The inputs can be in
XML files (preferred) or in POWERS text format.
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from pObject import *
from pPowersArray import *
import string


class pSeparatorCondition(pObject): 
	def __init__(self,ilo=None):
		pObject.__init__(self,ilo,'BEGIN_SEPARATOR_CONDITION','END_SEPARATOR_CONDITION')
		self.addKeyword('STANDARD_CONDITIONS_PRESSURE','14.7',label='Standard conditions pressure')
		self.addKeyword('STANDARD_CONDITIONS_TEMPERATURE','60.0',label='Standard conditions temperature')
		self.aAllowedKeywords =  self.aKeywords.keys()

	def parseLine(self,ilo):
		if ilo.mustProcess == 0: return None 
		self.iLineObject = ilo
		items = ilo.getItems()
		if len(items)>1: 
			keyword = items[0] 
			if keyword in [ 'END_SEPARATOR_CONDITION', 'END'] : 
				return 'END_SEPARATOR_CONDITION' 
			self.parseKeyword(keyword,items[1])
			return None
		self.addContentLine(ilo);	 # ALWAYS accumulate in your own block
		return None 

	#################################################################
	# Only these keywords are allowed, any other keyword is flagged. 
	#################################################################
	def parseKeyword(self,keyword,value):
		if (not keyword in self.aAllowedKeywords):
			self.iLineObject.markAsErred()
			self.addErrorMessage('Unrecognized keyword',self.iLineObject)
		else:
			self.addKeyword(keyword,value)

	def getEditableList(self,showHeader=1):
		xstr = []
		if showHeader == 1: xstr.append('BEGIN_SEPARATOR_CONDITION\n')
		for k in self.getKeywords(): 
			xstr.append('%s %s' % (k,self.getKeywordValue(k)))
		for ilo in self.aLineContents: xstr.append(ilo.getRawLine())
		if showHeader == 1: xstr.append('END_SEPARATOR_CONDITION\n')
		return xstr

	def getEditableString(self,showHeader=1):
		return "\n".join(self.getEditableList(showHeader))

	

class pGradientTable(pObject):
	def __init__(self,ilo=None):
		pObject.__init__(self,ilo,'BEGIN_GRADIENT_TABLE','END_GRADIENT_TABLE')
		self.sVariable  = 'GRADIENT'
		self.sOperation = ''
		self.dDataItems = []
		self.typeOfObject = 'GRADIENT'
		self.clearErrors();
		self.addKeyword('GRADIENT_CUTOFF_DEPTH','1.0',label='Gradient Cutoff Depth')
		self.addKeyword('TOP','1.0',label='Top Value')

	def parseLine(self,ilo):
		if ilo.mustProcess == 0: return None 
		self.iLineObject = ilo
		items = ilo.getItems()
		if len(items)>1: 
			keyword = items[0] 
			if keyword in [ 'END_GRADIENT_TABLE', 'END'] : 
				return 'END_GRADIENT_TABLE' 
			self.parseKeyword(keyword,items[1])
			return
		self.addContentLine(ilo);	 # ALWAYS accumulate in your own block
		return None 
		
	def parseKeyword(self,keyword,value):
		if (not keyword in self.aAllowedKeywords):
			self.iLineObject.markAsErred()
			self.addErrorMessage('Unrecognized keyword',self.iLineObject)
		else:
			self.addKeyword(keyword,value)
	#
	# Basically, you should only write those values that were in the input.
	# 
	def getEditableList(self,showHeader=1):
		xstr = []
		if showHeader == 1: xstr.append('BEGIN_GRADIENT_TABLE\n')
		for ilo in self.aLineContents: xstr.append(ilo.getRawLine())
		if showHeader == 1: xstr.append('END_GRADIENT_TABLE\n')
		return xstr

	def getEditableString(self,showHeader=1):
		return "\n".join(self.getEditableList(showHeader))


class pCompositional(pObject):
	def __init__(self,ilo=None):
		pObject.__init__(self,ilo,'BEGIN_COMPOSITIONAL_PARAMETERS','END_COMPOSITIONAL_PARAMETERS')
		self.addKeyword('OIL_RESERVOIR','FALSE',('TRUE','FALSE'))
		self.addKeyword('BINARY_COEFFICIENTS','CONSTANT',('CONSTANT','VALUE','GRADIENT'),label='Binary Coefficients Water Density')
		self.addKeyword('INITIAL_COMPOSITION','CONSTANT',('CONSTANT','VALUE','GRADIENT'),label='Initial Compositional Values')
		self.addKeyword('WATER_COMPRESSIBILITY','5.0-6',label='Water compressibility')
		self.addKeyword('WATER_REFERENCE_PRESSURE','14.696',label='Water Reference Pressure')
		self.addKeyword('WATER_REFERENCE_MOLAR_DENSITY','3.468',label='Water Molar Density')
		self.addKeyword('STANDARD_WATER_DENSITY','1.0',label='Standard Water Density')
		self.addKeyword('RESERVOIR_TEMPERATURE','1.0',label='Reservoir Temperature')
		self.addKeyword('PSEUDO_PRESSURE','1.0',label='Psuedo Pressure')
		self.aAllowedKeywords =  self.aKeywords.keys()
		self.state = 'idle'
		self.separator =  pSeparatorCondition()
		self.gradient  =  pGradientTable()
		self.arrayedNames = [ 'COMPONENT_PROPERTIES', 'BINARY_COEFFICIENTS', 'INITIAL_COMPOSITION', 'BEGIN_SEPARATOR_CONDITION']
		self.stringedArray = {} 
		for i in self.arrayedNames: self.stringedArray[i] = []
		self.lastArray = []
			

	#################################################################
	# Checks if the keywords inserted are indeed okay. Redundant.
	#################################################################
	def doConsistencyCheck(self):
		pass
	
	#################################################################
	# Parses pLineObjects
	#################################################################
	def parseLine(self,ilo):
		self.iLineObject = ilo                 # Retain the last line if you have to
		if self.state == 'BEGIN_SEPARATOR_CONDITION':
			t = self.separator.parseLine(ilo)
			if t == 'END_SEPARATOR_CONDITION': 
				self.state = 'idle'
			return
		if self.state == 'BEGIN_GRADIENT_TABLE':
			t = self.gradient.parseLine(ilo)
			if t == 'END_GRADIENT_TABLE': 
				self.state = 'idle'
			return
		items = ilo.getItems()                 # Get the items minus comments
		if self.state in self.arrayedNames:
			if (len(items)>0):
				keyword = string.upper(items[0])         # at least one keyword
				if keyword in self.arrayedNames:
					
					self.state = keyword
					self.lastArray = self.stringedArray[keyword]
					return
				if keyword in self.aAllowedKeywords: 	 #
					self.parseKeyword(keyword,items[1])
					self.state = 'idle'
					return 
			self.lastArray.append(ilo.getRawLine())
			return
		# In idle state.
		if (len(items)>0):
			keyword = string.upper(items[0])           # at least one keyword
			if keyword in self.arrayedNames:           
				
				self.state = keyword
				self.lastArray = self.stringedArray[keyword]
				return 
			if self.state == 'idle' and (len(items)==2):   # If key value line found  in idle state
				keyword = string.upper(items[0])           # normalize
				self.parseKeyword(keyword,items[1])
				self.aLineContents.append(ilo)             # Add the line here for output back. 
			return	
		if ilo.mustProcess == 0: return        # Ignore the comments 
		self.aLineContents.append(ilo)         # Add the line here for output back. 
		ilo.markAsErred()                      # Otherwise this is an error
		self.addErrorMessage('Invalid Input', ilo)

	#################################################################
	# Only these keywords are allowed, any other keyword is flagged. 
	#################################################################
	def parseKeyword(self,keyword,value):
		if (not keyword in self.aAllowedKeywords):
			self.iLineObject.markAsErred()
			self.addErrorMessage('Unrecognized keyword',self.iLineObject)
		else:
			self.addKeyword(keyword,value)

	#################################################################
	# Just so that I can change the name later.
	#################################################################
	def writeXMLfile(self,fd=sys.stdout,name='ROCKFLUID',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 

	def readXMLfile(self,filename,xmldir='.'):
		ch = pCompositionalXMLhandler()
		pObject.readXMLfile(self,filename,ch,xmldir)


##########################################################################
# The first pass attempts to recreate the aLineContents items in the file.
##########################################################################
class pCompositionalXMLhandler(ContentHandler):
	def setObj(self, obj, filename):
		self.obj = obj
		self.filename = filename
		self.lineNumber = 1
		self.thisLine = ''
		self.inBody   = 0

	def characters(self,characters):
		if self.inBody == 1: self.thisLine += characters 

	def endElement(self,name):
		if name == 'COMMENT':
			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			self.thisLine = ''
			self.inBody = 0
			return 
		if name == 'PARAMETER':
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		if name == 'BLOCK_ROCK_FLUID':
			ilo = pLineObject('BLOCK_ROCK_FLUID',self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			return
		if name == 'PARAMETER':
			key = attrs.get("NAME",'')
			val = attrs.get("VALUE",'')
			xstr = key + ' ' + val  + '\n'
			ilo = pLineObject(xstr,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)
			return 
		if name in ['COMMENT']:
			self.thisLine = ''
			self.inBody = 1
			return
			
######################################################################################
# Test program to read in XML file from actual model file.
######################################################################################
import sys
if __name__ == '__main__':
	if len(sys.argv) < 1: 
		sys.exit(0)
	fname = sys.argv[1]
	ob = pCompositional()
	ch = pCompositionalXMLhandler()
	ch.setObj(ob,fname)
	sx = make_parser()
	sx.setContentHandler(ch)
	sx.parse(fname)
	print ob.getEditableString()
	

	
