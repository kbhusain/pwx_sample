"""
#
# This object is used in GRID_DATA to store an ARRAY object
# It does NOT maintain the lines themselves since the master must 
# maintain the ORDER in which lines are encountered.
#
Author: Kamran Husain  PEASD/SSD
"""
from pObject import *
from string import *

aAllowedArrayOperations = ['ADD','REPLACE','MULTIPLY','DIVIDE','SUBTRACT','EQUALS','CONSTANT', 'TOP','VALUE','ZONLY','YONLY','XONLY']
# You must specify an operation and a variable name
class pPowersArray(pObject):
	def __init__(self,id,oper,ilo=None):
		pObject.__init__(self,ilo)
		self.sVariable  = id
		self.sOperation = oper
		self.dDataItems = []
		self.typeOfObject = 'ARRAY'
		self.sIdString =	 'ARRAY %s %s' % (self.sVariable, self.sOperation)
		self.clearErrors();
		self.aAllowedOperations = aAllowedArrayOperations

	def parseLine(self,ilo):
		if ilo.mustProcess == 0: return None 
		items = ilo.getItems()
		if items[0] in [ 'ENDARRAY', 'END'] : return 'ENDARRAY' 
		self.addContentLine(ilo);	 # ALWAYS accumulate in your own block
		return None 
		
	#
	# Basically, you should only write those values that were in the input.
	# 
	def getEditableList(self,showHeader=1):
		xstr = []
		xstr.append('ARRAY %s %s \n' % (self.sVariable, self.sOperation))
		for ilo in self.aLineContents: xstr.append(ilo.getRawLine())
		xstr.append('ENDARRAY\n')
		return xstr


	def getEditableString(self,showHeader=1):
		xstr = 'ARRAY %s %s \n' % (self.sVariable, self.sOperation)
		ret = pObject.getEditableString(self,showHeader=0)
		xstr += ret + 'ENDARRAY\n'
		return xstr

	def doConsistencyCheck(self):
		self.clearErrors();
		if (not self.sOperation in self.aAllowedOperations):
		   self.str = 'Grid Data: Array Item: Bad Operation: [%s]\n' % self.sOperation
		   self.addWarningMessage(self.str)

	def getContentsAsList(self,showHeader=1,includeLineContents=0):
		"""
		Returns a list of strings with key value pairs. 
		Override this function to get better functionality in class
		that has sub classes.
		"""
		items = []
		if showHeader == 1: items.append(self.sIdString + '\n')
		for ilo in self.aLineContents:        # Okay, the guys wants it all
			items.append(ilo.getRawLine())
		if showHeader == 1: items.append('ENDARRAY\n')
		return items

	def getXMLcontentAsList(self,nm,xmldir='.'):
		retlist = []
		retlist.append( '<ARRAY id="%s" oper="%s" >' % (self.sVariable, self.sOperation))
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLlineItems():	retlist.append(item)
		retlist.append( '</ARRAY>\n')
		return retlist
		#return "".join(retlist)

####################################################################################
# This requires a GRID object for this item to be parsed. I will add this object 
# to the list of objects in the GRID object
####################################################################################
# class pPowersArrayTable_Handler(ContentHandler):
# 	def setObj(self, obj, filename):
# 		self.obj = obj
# 		self.filename = filename
# 		self.lineNumber = 1
# 		self.thisLine = ''
# 		self.inBody   = 0
# 
# 	def characters(self,characters):
# 		if self.inBody == 1: self.thisLine += characters 
# 
# 	def endElement(self,name):
# 		if name in  ['COMMENT', 'LINE']:
# 			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
# 			self.lineNumber += 1
# 			self.obj.parseLine(ilo)                    # The line is kept in raw form
# 			self.thisLine = ''
# 			self.inBody = 0
# 			return 
# 
# 	def startElement(self, name, attrs):
# 		if name == 'ARRAY':
# 			xstr = name + ' ' +  attrs.get('id','') + ' ' + attrs.get('oper','')
# 			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
# 			self.obj.parseLine(ilo)                    # The line is kept in raw form
# 			self.lineNumber += 1
# 			return 
# 		if name in  ['COMMENT','LINE']:
# 			self.thisLine = ''
# 			self.inBody = 1
# 			return
# 


if __name__ == '__main__':
	f = [ 'ARRAY KAMRAN CONSTANT', '1', 'ENDARRAY']
	p = pPowersArray('KAMRAN','CONSTANT')
	for i in f: 
		print i
		ln = pLineObject(i+'\n')
		p.parseLine(ln)
	print p.getEditableString()
