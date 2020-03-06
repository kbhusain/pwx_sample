"""
# This object for region items.
# You must specify an operation and a variable name

# These objects read in the context of the master only.

Author: Kamran Husain  PEASD/SSD
"""
from xml.sax import make_parser
from xml.sax.handler import ContentHandler
from pObject import *
from string import *



class pRegion(pObject):
	def __init__(self,id,ilo):
		self.id = id
		self.sIdString = 'REGION %s' % id
		pObject.__init__(self,ilo,self.sIdString,'END_REGION')
		self.sIdString = 'REGION %s' % id
		self.typeOfObject = 'REGION'
		self.dDataItems = []
		self.clearErrors()
		self.sOperation = ''
		self.sVariable = ''

	def parseLine(self,ilo):
		if ilo.mustProcess == 0: return None
		items = ilo.getItems()
		if items[0] in [ 'END_REGION', 'END'] : return 'END_REGION'
		#if len(items) <> 6:
		#self.addWarningMessage('Region is not correct',ilo)
		#else:
		self.addContentLine(ilo);	    # ALWAYS accumulate in your own block
		self.dDataItems.append(items);  # Add the offending item anyway.
		return None

	def doConsistencyCheck(self):
		self.clearErrors();
		for self.i in self.dDataItems:
			if (len(self.i) <> 6):
				self.str = 'GRID: Region Item: Bad Input Line: [%s]\n' % self.i
				self.addWarningMessage(self.str)

	def getContentsAsList(self,showHeader=0,includeLineContents=0):
		"""
		Returns a list of strings with key value pairs.
		Override this function to get better functionality in class
		that has sub classes.
		"""
		items = []
		if showHeader == 1: items.append(self.sStartOfBlock + '\n')
		for ilo in self.aLineContents:        # Okay, the guys wants it all
			items.append(ilo.getRawLine())
		if showHeader == 1: items.append(self.sEndOfBlock + '\n')
		return items


	def getEditableString(self,showHeader=1):
		return "".join(self.getContentsAsList(showHeader))

	def getXMLcontent(self,nm,xmldir='.'):
		retlist = []
		retlist.append('<REGION id="%s" />\n' % self.id)
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLlineItems():	retlist.append(item)
		retlist.append('</REGION>\n')
		return "".join(retlist)

	def getXMLcontentAsList(self,nm,xmldir='.'):
		retlist = []
		retlist.append('<REGION id="%s" />\n' % self.id)
		for item in self.getIteratedXMLComments():	retlist.append(item)
		for item in self.getIteratedXMLlineItems():	retlist.append(item)
		retlist.append('</REGION>\n')
		return retlist

	def getEditableString(self,showHeader=1):
		xstr = ''
		if showHeader == 1: xstr +=  self.sIdString + "\n"
		for ilo in self.aLineContents: xstr += ilo.getRawLine()
		if showHeader == 1: xstr +=  self.sEndOfBlock  + "\n"
		return xstr

	def getIdString(self):
		return self.sIdString.replace('_',' ')

class pFluidInPlaceRegion(pObject):
	def __init__(self,id=None,ilo=None):
		self.id = None
		self.sIdString = 'FLUID_IN_PLACE_REGION'
		pObject.__init__(self,ilo,self.sIdString,'END_FLUID_IN_PLACE_REGION')
		self.sIdString = 'FLUID_IN_PLACE_REGION'
		self.typeOfObject = 'FLUID_IN_PLACE_REGION'
		self.lastRegion = None
		self.inRegion = 0
		self.iRegions = {}
		self.clearErrors()
		self.sOperation = ''
		self.sVariable = ''
		self.regionNames = []
		self.maxX = 10000
		self.maxY = 10000
		self.maxZ = 10000

	def setXYZ(self, x,y,z):
		self.maxX = x
		self.maxY = y
		self.maxZ = z

	def parseLine(self,ilo):
		if ilo.mustProcess == 0: return None
		if self.inRegion == 1: 
			#print "In region", ilo.getCookedLine()
			r = self.lastRegion.parseLine(ilo)
			if r <> None: 
				self.inRegion = 0
				return 'END_REGION'
		items = ilo.getItems()
		if items[0] == 'REGION':
			fraw = ilo.getCookedLine()
			f = fraw.find('{')
			if f > 0:
				items = ilo.getItems()
				id = fraw.replace(' ','_')
			else:
				id = items[1]
			self.lastRegion = pRegion(id,ilo)
			self.iRegions[self.lastRegion.sIdString] = self.lastRegion
			self.inRegion = 1
			return None
		if items[0] ==  'END_REGION': 
			self.inRegion = 0
			return 'END_REGION'
		if items[0] in [ 'END_FLUID_IN_PLACE_REGION', 'END'] : return 'END_FLUID_IN_PLACE_REGION'
		self.addContentLine(ilo);	 # ALWAYS accumulate in your own block
		return None

	def changeRegionName(self,oldname,incoming):
		obj = self.iRegions.get(oldname,None)
		if obj == None: return 0
		newname = incoming.strip()
		newname = newname.replace(""",""",'_')
		newname = newname.replace(""" """,'_')
		obj.sIdString = newname 
		self.iRegions[newname] = obj
		self.iRegions[oldname] = None
		del self.iRegions[oldname]

	def checkRegionName(self,name):
		if len(name) < 1: return -1
		items = name.split()
		if len(items) > 1: 
			fs = name.find('{')
			fe = name.find('}')
			fc = name.find(',')
			print "pRegion:checkRegionName:", fs, fe, fc 
			if fc <> -1:
				return -2
			if fs == -1 and fe <> -1: return -3
			if fe == -1 and fs <> -1: return -3
			return 1
		else:
			if len(name) > 0: return 1 
		return -1 

	def delRegion(self,name):
		if self.iRegions.has_key(name): self.iRegions[name] = None

	def addRegion(self,name):
		ok = self.checkRegionName(name)
		if ok < 0: return -1
		ilo = pLineObject(name)
		self.lastRegion = pRegion(name,ilo)
		self.iRegions[self.lastRegion.sIdString] = self.lastRegion
		#ilo.setLine('REGION') 
		#self.lastRegion.parseLine(ilo)
		#ilo.setLine('END_REGION') 
		#self.lastRegion.parseLine(ilo)
		return 1

	def getRegion(self,name):
		return self.iRegions.get(name,None)

	def getRegionNames(self):
		return self.iRegions.keys()

	def getContentsAsList(self,showHeader=0,includeLineContents=0):
		"""
		Returns a list of strings with key value pairs.
		Override this function to get better functionality in class
		that has sub classes.
		The question is will order matter??
		"""
		items = []
		if showHeader == 1: items.append(self.sStartOfBlock + '\n')
		for i in self.iRegions.values():
			for x in i.getContentsAsList(showHeader=1):
				items.append(x)
		for ilo in self.aLineContents:        # Okay, the guys wants it all
			items.append(ilo.getRawLine())
		if showHeader == 1: items.append(self.sEndOfBlock + '\n')
		return items

	def getXMLcontent(self,nm,xmldir='.'):
		return []

	def getXMLcontentAsList(self,nm,xmldir='.'):
		return []

####################################################################################
#
# ####################################################################################
# class pRegionTable_Handler(ContentHandler):
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
# 			self.obj.parseLine(ilo)  # Handle this in the master
# 			self.thisLine = ''
# 			self.inBody = 0
# 			return 
# 
# 	def startElement(self, name, attrs):
# 		if name == 'REGION':
# 			xstr = 'REGION ' +  attrs.get('id','')
# 			ilo =  pLineObject(self.thisLine,self.filename,self.lineNumber)
# 			self.obj.parseLine(ilo)  # Handle in master
# 			self.lineNumber += 1
# 			return 
# 		if name in  ['COMMENT','LINE']:
# 			self.thisLine = ''
# 			self.inBody = 1
# 			return
#
