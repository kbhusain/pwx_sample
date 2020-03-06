
from pObject import *
import string 

class pComparator(pObject):
	def __init__(self,iLineNumber=None):
		pObject.__init__(self,iLineNumber,'BEGIN_COMPARATOR_PARAMETERS','END_COMPARATOR_PARAMETERS')
		self.addKeyword('NUMBER_OF_NODES','1')
		self.addKeyword('COMPARATOR_INIT_TOLERANCE','0')
		self.addKeyword('COMPARATOR_WELL_TOLERANCE','0')
		self.addKeyword('COMPARATOR_SAT_TOLERANCE','0')
		self.addKeyword('COMPARATOR_PRESSURE_TOLERANCE','0')
		self.aAllowedKeywords =  self.aKeywords

	#################################################################
	# Checks if the keywords inserted are indeed okay. Redundant.
	#################################################################
	def doConsistencyCheck(self):
		for self.i in self.getKeywords():
			if (not self.i in self.aAllowedKeywords):
				self.str = 'Pass 2: Comparator Parms: Unrecognized keyword in input: [%s]\n' % self.i
				self.addWarningMessage(self.str)
	
	#################################################################
	# Parses lines from input file. 
	#################################################################
	def parseLine(self,ilo):
		self.aLineContents.append(ilo)         # Add the line here for output back. 
		self.iLineObject = ilo                 # Retain the last line if you have to
		if ilo.mustProcess == 0: return   # Ignore the comments 
		items = ilo.getItems()
		if (len(items)==2):				# If key value line found. 
			keyword = string.upper(items[0])
			self.parseKeyword(keyword,items[1])
		else:
			ilo.markAsErred()
			self.addErrorMessage('Invalid Input', ilo)

	def parseKeyword(self,keyword,value):
		if (not keyword in self.aAllowedKeywords):
			self.iLineObject.markAsErred()
			self.addErrorMessage('Comparator Unrecognized keyword',self.iLineObject)
		else:
			self.addKeyword(keyword,value)

	def writeXMLfile(self,fd=sys.stdout,name='BLOCK_COMPARATOR',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 

	def readXMLfile(self,filename,xmldir='.'):
		ch = pComparatorXMLhandler()
		pObject.readXMLfile(self,filename,ch,xmldir)

##########################################################################
# The first pass attempts to recreate the aLineContents items in the file.
##########################################################################
class pComparatorXMLhandler(ContentHandler):
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
		if name == 'BLOCK_COMPARATOR':
			ilo = pLineObject('BLOCK_COMPARATOR',self.filename,self.lineNumber)
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
			
