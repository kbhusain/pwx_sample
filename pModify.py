"""
This object is used by GRID_DATA for an array of MODIFY objects.
TODO: Separate the dOperations string into seven variables each if necessary.

Author: Kamran Husain  PEASD/SSD

# You must specify an operation and a variable name
# This object cannot be read by itself since the context of the inclusor matters.
"""

from pObject import *
from string import *

class pModify(pObject):
	def __init__(self,ilo):
		items = ilo.getItems()
		self.typeOfObject = 'MODIFY'
		self.sVariable = ''
		if len(items) > 1: self.sVariable  = items[1]
		self.VersionInline = 0	    # Expect (6 numbers operation and 1 number)
		if len(items) == 2:
			self.VersionInline = 1	# Expect (1 numbers operation and 1 number) + condition
			self.sOperation = ''
			sIdString =	 'MODIFY %s' % (self.sVariable)
		else:
			self.VersionInline = 0	# Expect 7 digits per line.
			self.sOperation = items[2]
			sIdString =	 'MODIFY %s %s' % (self.sVariable, self.sOperation)
		pObject.__init__(self,ilo,sIdString,'ENDMODIFY')
		self.sIdString = sIdString        # Force the IS
		self.dOperations = []
		self.aAllowedOperations = ['ADD','REPLACE','MULTIPLY','DIVIDE','SUBTRACT','CONSTANT']
		
	def parseLine(self,ilo):
		"""
		Parses incoming lines into objects. Returns None or ENDMODIFY at the end of block.
		Stop processing when you get an ENDMODIFY
		"""
		if ilo.mustProcess == 0: return None
		items = ilo.getItems()
		if items[0] in [ 'ENDMODIFY', 'END'] : return 'ENDMODIFY' 
		self.addContentLine(ilo)
		if self.isValidLineItem(ilo) == 1:	# If valid item, add to operations.
			self.dOperations.append(ilo);	
		return None

	def isValidLineItem(self,ilo):
		"""
		Returns 1 if valid, 0 if not.
		Marks the ilo as errored
		"""
		items = ilo.getItems()
		if (self.VersionInline):
			if (len(items) > 6): # Correct number of items per line. 
				if not (items[6] in self.aAllowedOperations) and len(self.sOperation) == 0: 
					ilo.markAsErred()
					return 0
		return 1

	def doConsistencyCheck(self):
		self.clearErrors();
		if ((self.VersionInline == 0) and (not self.sOperation in self.aAllowedOperations)):
			self.str = 'Grid Data: Modify Item: Bad Operation: [%s]\n' % self.sOperation
			self.addWarningMessage(self.str)
		for oper in self.dOperations:
			if (not self.isValidLineItem(oper)):
				self.str = 'Grid Data Bad Input Line : [%s]\n' % join(oper)
				self.addWarningMessage(self.str)

	def getEditableString(self,showHeader=1):
		return "".join(self.getContentsAsList(1,1))

	def getContentsAsList(self,showHeader=0,includeLineContents=0):
		"""
		Returns a list of strings with key value pairs. 
		Override this function to get better functionality in class
		that has sub classes.
		"""
		items = []
		if showHeader == 1: items.append(self.sIdString + '\n')
		for ilo in self.aLineContents:        # Okay, the guys wants it all
			items.append(ilo.getRawLine())
		if showHeader == 1: items.append('ENDMODIFY\n')
		return items

	def getXMLcontent(self,nm,xmldir='.'):
		retlist = []
		retlist.append('<MODIFY id="%s" operation="%s">\n' % (self.sVariable,self.sOperation))
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLlineItems():	retlist.append(item)
		retlist.append('</MODIFY>\n')
		return "".join(retlist)


	def getXMLcontentAsList(self,nm,xmldir='.'):
		retlist = []
		retlist.append('<MODIFY id="%s" operation="%s">\n' % (self.sVariable,self.sOperation))
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLlineItems():	retlist.append(item)
		retlist.append('</MODIFY>\n')
		return retlist


####################################################################################
#
####################################################################################
# class pModifyTable_Handler(ContentHandler):
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
# 		if name == 'MODIFY':
# 			xstr = 'MODIFY ' +  attrs.get('id','')
# 			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
# 			self.obj.parseLine(ilo)                    # The line is kept in raw form
# 			self.lineNumber += 1
# 			return 
# 		if name in  ['COMMENT','LINE']:
# 			self.thisLine = ''
# 			self.inBody = 1
# 			return
# 
# 
