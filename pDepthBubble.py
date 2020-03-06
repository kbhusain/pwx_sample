#!/work0/kamran/Python-2.2.2/python

#
# This object is instantiead of an array of depth bubble point objects.
#
from pObject import *
from string import *

class pDepthBubble(pObject):
	def __init__(self,id=0,iLineNumber=0):
		self.sIdString = 'DEPTH_BUBBLE_POINT_TABLE %d' % (int(id))
		pObject.__init__(self,iLineNumber,self.sIdString,'ENDDEPTH_BUBBLE_POINT_TABLE')  # Use default delimiters.
		self.id = id
		self.hasEnded = 0

	def setID(self,id=0): 
		self.id = id
		self.sIdString = 'DEPTH_BUBBLE_POINT_TABLE %d' % (int(id))

	def parseLine(self,ilo):
		if ilo.mustProcess == 0: return 
		rest = ilo.getItems()
		if (len(rest) == 2): 
			self.addContentLine(ilo)
		else:
			if rest[0] == 'ENDDEPTH_BUBBLE_POINT_TABLE': 
				self.hasEnded = 1
				return
			key = rest[0]
			if key[:3]== 'END': self.hasEnded = 1
			xstr = '%s Bad line ignored \n' % (self.sIdString)
			self.addErrorMessage(xstr,ilo)


	#################################################################
	# 
	#################################################################
	def writeXMLfile(self,fd=sys.stdout,name='DEPTH_BUBBLE_TABLE',xmldir='.'):
		pObject.writeXMLfile(self,fd,name,xmldir); 

	def getXMLcontent(self,name='IGNORED',pathname='.'):
		retlist=[]
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLnumericLines(2):	retlist.append(item)
		for item in self.getIteratedXMLKeywords():	retlist.append(item)
		return "".join(retlist)


	def readXMLfile(self,filename,xmldir='.'):
		ch = pDepthBubble_XMLhandler()
		pObject.readXMLfile(self,filename,ch,xmldir)

	#def getEditableString(self,showHeader=0):
	#	return self.getTableAsEditableString(showHeader)
		
####################################################################################
#
####################################################################################
class pDepthBubble_XMLhandler(ContentHandler):
	def setObj(self, obj, filename):
		self.obj = obj
		self.filename = filename
		self.lineNumber = 1
		self.thisLine = ''
		self.inBody   = 0
		self.allowedTags = [ 'COMMENT', 'LINE' ]

	def characters(self,characters):
		if self.inBody == 1: self.thisLine += characters 

	def endElement(self,name):
		if name in self.allowedTags:
			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
			self.lineNumber += 1
			self.obj.parseLine(ilo)                    # The line is kept in raw form
			self.thisLine = ''
			self.inBody = 0
			return 

	def startElement(self, name, attrs):
		if name in self.allowedTags:
			self.thisLine = ''
			self.inBody = 1
			return

