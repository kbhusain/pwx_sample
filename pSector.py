
from pObject import *
import string 

class pSectorExtract(pObject):
	def __init__(self,iLineNumber=None):
		pObject.__init__(self,iLineNumber,'BEGIN_SECTOR_EXTRACT_OPTION','END_SECTOR_EXTRACT_OPTION')
		self.addKeyword('SECTOR_BINARY_DIRECTORY','"."',label='Binary Directory')
		self.aAllowedKeywords =  self.aKeywords.keys()

	#################################################################
	# Checks if the keywords inserted are indeed okay. Redundant.
	#################################################################
	def doConsistencyCheck(self):
		for k in self.getKeywords():
			if (not k in self.aAllowedKeywords):
				self.addWarningMessage('Pass 2: SectorExtract Parms: Unrecognized keyword in input: [%s]\n' % k)
	
	#################################################################
	# Parses lines from input file. 
	#################################################################
	def parseLine(self,ilo):
		self.aLineContents.append(ilo)         # Add the line here for output back. 
		self.iLineObject = ilo                 # Retain the last line if you have to
		if ilo.mustProcess == 0: return   # Ignore the comments 
		items = ilo.getItems()
		keyword = items[0]
		value = '"Not defined"'
		if len(items) > 1: value   = items[1]
		if (keyword in self.aAllowedKeywords):
			self.addKeyword(keyword,value)
			return 
		if (len(items)<>7):				# If key value line found. 
			ilo.markAsErred()
			self.addErrorMessage('Invalid Input', ilo)

	def clearContents(self):
		"""
		Clears out any lines that have data in them 
		"""
		for i in self.aLineContents:
			if ilo.mustProcess == 0: continue   # Ignore the comments 
			items = ilo.getItems()
			keyword = items[0]      
			if (keyword in self.aAllowedKeywords):
				self.aLineContents.remove(ilo)
				continue
			if (len(items)==7): 
				self.aLineContents.remove(ilo)
				continue
			

	def parseKeyword(self,keyword,value):
		if (not keyword in self.aAllowedKeywords):
			self.iLineObject.markAsErred()
			self.addErrorMessage('SectorExtract Unrecognized keyword',self.iLineObject)
		else:
			self.addKeyword(keyword,value)

	def writeXMLfile(self,fd=sys.stdout,name='BLOCK_SECTOR_EXTRACT',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 

	def readXMLfile(self,filename,xmldir='.'):
		ch = pSectorExtract()
		pObject.readXMLfile(self,filename,ch,xmldir)

##########################################################################
# The first pass attempts to recreate the aLineContents items in the file.
##########################################################################
class pSectorExtractXMLhandler(ContentHandler):
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
		if name == 'BLOCK_SECTOR_EXTRACT':
			ilo = pLineObject('BLOCK_SECTOR_EXTRACT',self.filename,self.lineNumber)
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
			
